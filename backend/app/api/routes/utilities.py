"""Utility Outage endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_manager
from app.database import get_db
from app.models import UtilityOutage, User, enums
from app.schemas.common import Page, PaginationParams
from app.schemas.entities import UtilityOutageCreate, UtilityOutageOut, UtilityOutageUpdate
from app.services import audit_service
from app.services.common import paginate

router = APIRouter(prefix="/utilities", tags=["Utilities"])


@router.get("", response_model=Page[UtilityOutageOut])
def list_outages(
    params: PaginationParams = Depends(),
    utility_type: enums.UtilityType | None = Query(None),
    outage_status: enums.UtilityOutageStatus | None = Query(None, alias="status"),
    region: str | None = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> Page[UtilityOutageOut]:
    stmt = select(UtilityOutage)
    if utility_type:
        stmt = stmt.where(UtilityOutage.utility_type == utility_type)
    if outage_status:
        stmt = stmt.where(UtilityOutage.status == outage_status)
    if region:
        stmt = stmt.where(UtilityOutage.region == region)
    items, total = paginate(db, stmt, UtilityOutage, params, ("region", "description"), "customers_affected")
    return Page.create([UtilityOutageOut.model_validate(o) for o in items], total, params.page, params.page_size)


@router.post("", response_model=UtilityOutageOut, status_code=status.HTTP_201_CREATED)
def create_outage(
    payload: UtilityOutageCreate, db: Session = Depends(get_db), user: User = Depends(require_manager)
) -> UtilityOutage:
    outage = UtilityOutage(**payload.model_dump(), organization_id=user.organization_id)
    db.add(outage)
    db.commit()
    db.refresh(outage)
    audit_service.log(db, actor=user, action="create_outage", entity_type="utility_outage", entity_id=outage.id)
    return outage


@router.patch("/{outage_id}", response_model=UtilityOutageOut)
def update_outage(
    outage_id: int, payload: UtilityOutageUpdate, db: Session = Depends(get_db), user: User = Depends(require_manager)
) -> UtilityOutage:
    outage = db.get(UtilityOutage, outage_id)
    if not outage:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Outage not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(outage, key, value)
    db.commit()
    db.refresh(outage)
    audit_service.log(db, actor=user, action="update_outage", entity_type="utility_outage", entity_id=outage.id)
    return outage
