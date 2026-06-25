"""Hospital Operations endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_manager
from app.database import get_db
from app.models import Hospital, User
from app.schemas.common import Page, PaginationParams
from app.schemas.entities import HospitalCreate, HospitalOut, HospitalUpdate
from app.services import audit_service
from app.services.common import paginate
from app.services.scoring_service import hospital_out, recompute_hospital

router = APIRouter(prefix="/hospitals", tags=["Hospitals"])


@router.get("", response_model=Page[HospitalOut])
def list_hospitals(
    params: PaginationParams = Depends(),
    region: str | None = Query(None),
    at_risk: bool = Query(False, description="Only hospitals with stress >= 55"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> Page[HospitalOut]:
    stmt = select(Hospital)
    if region:
        stmt = stmt.where(Hospital.region == region)
    if at_risk:
        stmt = stmt.where(Hospital.stress_score >= 55)
    items, total = paginate(db, stmt, Hospital, params, ("name", "region"), "stress_score")
    return Page.create(
        [HospitalOut.model_validate(hospital_out(h)) for h in items], total, params.page, params.page_size
    )


@router.get("/{hospital_id}", response_model=HospitalOut)
def get_hospital(hospital_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> HospitalOut:
    hospital = db.get(Hospital, hospital_id)
    if not hospital:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Hospital not found")
    return HospitalOut.model_validate(hospital_out(hospital))


@router.post("", response_model=HospitalOut, status_code=status.HTTP_201_CREATED)
def create_hospital(
    payload: HospitalCreate, db: Session = Depends(get_db), user: User = Depends(require_manager)
) -> HospitalOut:
    hospital = Hospital(**payload.model_dump(), organization_id=user.organization_id)
    recompute_hospital(hospital)
    db.add(hospital)
    db.commit()
    db.refresh(hospital)
    audit_service.log(db, actor=user, action="create_hospital", entity_type="hospital", entity_id=hospital.id)
    return HospitalOut.model_validate(hospital_out(hospital))


@router.patch("/{hospital_id}", response_model=HospitalOut)
def update_hospital(
    hospital_id: int, payload: HospitalUpdate, db: Session = Depends(get_db), user: User = Depends(require_manager)
) -> HospitalOut:
    hospital = db.get(Hospital, hospital_id)
    if not hospital:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Hospital not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(hospital, key, value)
    recompute_hospital(hospital)
    db.commit()
    db.refresh(hospital)
    audit_service.log(db, actor=user, action="update_hospital", entity_type="hospital", entity_id=hospital.id)
    return HospitalOut.model_validate(hospital_out(hospital))
