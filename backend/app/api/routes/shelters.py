"""Shelter Operations endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_manager
from app.database import get_db
from app.models import Shelter, User, enums
from app.schemas.common import Page, PaginationParams
from app.schemas.entities import ShelterCreate, ShelterOut, ShelterUpdate
from app.services import audit_service
from app.services.common import paginate
from app.services.scoring_service import recompute_shelter, shelter_out

router = APIRouter(prefix="/shelters", tags=["Shelters"])


@router.get("", response_model=Page[ShelterOut])
def list_shelters(
    params: PaginationParams = Depends(),
    region: str | None = Query(None),
    shelter_status: enums.ShelterStatus | None = Query(None, alias="status"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> Page[ShelterOut]:
    stmt = select(Shelter)
    if region:
        stmt = stmt.where(Shelter.region == region)
    if shelter_status:
        stmt = stmt.where(Shelter.status == shelter_status)
    items, total = paginate(db, stmt, Shelter, params, ("name", "region"), "utilization_score")
    return Page.create(
        [ShelterOut.model_validate(shelter_out(s)) for s in items],
        total,
        params.page,
        params.page_size,
    )


@router.get("/{shelter_id}", response_model=ShelterOut)
def get_shelter(
    shelter_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)
) -> ShelterOut:
    shelter = db.get(Shelter, shelter_id)
    if not shelter:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Shelter not found")
    return ShelterOut.model_validate(shelter_out(shelter))


@router.post("", response_model=ShelterOut, status_code=status.HTTP_201_CREATED)
def create_shelter(
    payload: ShelterCreate, db: Session = Depends(get_db), user: User = Depends(require_manager)
) -> ShelterOut:
    shelter = Shelter(**payload.model_dump(), organization_id=user.organization_id)
    recompute_shelter(shelter)
    db.add(shelter)
    db.commit()
    db.refresh(shelter)
    audit_service.log(
        db, actor=user, action="create_shelter", entity_type="shelter", entity_id=shelter.id
    )
    return ShelterOut.model_validate(shelter_out(shelter))


@router.patch("/{shelter_id}", response_model=ShelterOut)
def update_shelter(
    shelter_id: int,
    payload: ShelterUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_manager),
) -> ShelterOut:
    shelter = db.get(Shelter, shelter_id)
    if not shelter:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Shelter not found")
    data = payload.model_dump(exclude_unset=True)
    explicit_status = data.pop("status", None)
    for key, value in data.items():
        setattr(shelter, key, value)
    recompute_shelter(shelter)
    if explicit_status is not None:
        shelter.status = explicit_status
    db.commit()
    db.refresh(shelter)
    audit_service.log(
        db, actor=user, action="update_shelter", entity_type="shelter", entity_id=shelter.id
    )
    return ShelterOut.model_validate(shelter_out(shelter))
