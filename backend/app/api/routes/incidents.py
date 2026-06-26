"""Incident Management endpoints."""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import require_permission
from app.core.permissions import Permission
from app.database import get_db
from app.models import Incident, IncidentEvent, User, enums
from app.schemas.common import Message, Page, PaginationParams
from app.schemas.entities import (
    IncidentCreate,
    IncidentDetail,
    IncidentEventOut,
    IncidentOut,
    IncidentUpdate,
)
from app.services import audit_service
from app.services.common import paginate
from app.services.scoring_service import recompute_incident

router = APIRouter(prefix="/incidents", tags=["Incidents"])


@router.get("", response_model=Page[IncidentOut])
def list_incidents(
    params: PaginationParams = Depends(),
    incident_type: enums.IncidentType | None = Query(None),
    incident_status: enums.IncidentStatus | None = Query(None, alias="status"),
    region: str | None = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(require_permission(Permission.INCIDENT_READ)),
) -> Page[IncidentOut]:
    stmt = select(Incident)
    if incident_type:
        stmt = stmt.where(Incident.incident_type == incident_type)
    if incident_status:
        stmt = stmt.where(Incident.status == incident_status)
    if region:
        stmt = stmt.where(Incident.region == region)
    items, total = paginate(
        db, stmt, Incident, params, ("name", "region", "description"), "severity_score"
    )
    return Page.create(
        [IncidentOut.model_validate(i) for i in items], total, params.page, params.page_size
    )


@router.get("/{incident_id}", response_model=IncidentDetail)
def get_incident(
    incident_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission(Permission.INCIDENT_READ)),
) -> Incident:
    incident = db.get(Incident, incident_id)
    if not incident or incident.deleted_at is not None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Incident not found")
    return incident


@router.get("/{incident_id}/timeline", response_model=list[IncidentEventOut])
def incident_timeline(
    incident_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission(Permission.INCIDENT_READ)),
) -> list[IncidentEvent]:
    incident = db.get(Incident, incident_id)
    if not incident:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Incident not found")
    return list(
        db.scalars(
            select(IncidentEvent)
            .where(IncidentEvent.incident_id == incident_id)
            .order_by(IncidentEvent.occurred_at)
        ).all()
    )


@router.post("", response_model=IncidentDetail, status_code=status.HTTP_201_CREATED)
def create_incident(
    payload: IncidentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission(Permission.INCIDENT_MANAGE)),
) -> Incident:
    incident = Incident(**payload.model_dump(), organization_id=user.organization_id)
    incident.data_origin = enums.DataOrigin.MANUAL
    incident.created_by_id = user.id
    incident.updated_by_id = user.id
    recompute_incident(incident)
    db.add(incident)
    db.flush()
    db.add(
        IncidentEvent(
            incident_id=incident.id,
            event_type="created",
            description=f"Incident '{incident.name}' opened at severity {incident.severity}/5.",
            occurred_at=datetime.now(UTC),
        )
    )
    db.commit()
    db.refresh(incident)
    audit_service.log(
        db,
        actor=user,
        action="create_incident",
        category="incident",
        entity_type="incident",
        entity_id=incident.id,
        new_value={
            "name": incident.name,
            "type": incident.incident_type.value,
            "severity": incident.severity,
        },
    )
    return incident


@router.patch("/{incident_id}", response_model=IncidentDetail)
def update_incident(
    incident_id: int,
    payload: IncidentUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission(Permission.INCIDENT_UPDATE)),
) -> Incident:
    incident = db.get(Incident, incident_id)
    if not incident or incident.deleted_at is not None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Incident not found")
    data = payload.model_dump(exclude_unset=True)
    expected_version = data.pop("expected_version", None)
    if expected_version is not None and expected_version != incident.version:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            f"Incident was modified by another user (expected v{expected_version}, current v{incident.version}).",
        )
    before = {"status": incident.status.value, "severity": incident.severity, "name": incident.name}
    prior_status = incident.status
    for key, value in data.items():
        setattr(incident, key, value)
    if incident.status == enums.IncidentStatus.RESOLVED and not incident.resolved_at:
        incident.resolved_at = datetime.now(UTC)
    incident.updated_by_id = user.id
    recompute_incident(incident)
    event_descr = f"Incident updated (severity {incident.severity_score:.0f}/100)."
    if "status" in data and data["status"] != prior_status:
        event_descr = f"Status changed {prior_status.value} → {incident.status.value}."
    db.add(
        IncidentEvent(
            incident_id=incident.id,
            event_type="update",
            description=event_descr,
            occurred_at=datetime.now(UTC),
        )
    )
    db.commit()
    db.refresh(incident)
    after = {"status": incident.status.value, "severity": incident.severity, "name": incident.name}
    audit_service.log(
        db,
        actor=user,
        action="update_incident",
        category="incident",
        entity_type="incident",
        entity_id=incident.id,
        old_value=before,
        new_value=after,
    )
    return incident


@router.delete("/{incident_id}", response_model=Message)
def delete_incident(
    incident_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission(Permission.INCIDENT_MANAGE)),
) -> Message:
    incident = db.get(Incident, incident_id)
    if not incident or incident.deleted_at is not None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Incident not found")
    # Soft delete preserves the record for audit/forensics.
    incident.deleted_at = datetime.now(UTC)
    incident.updated_by_id = user.id
    db.commit()
    audit_service.log(
        db,
        actor=user,
        action="delete_incident",
        category="incident",
        entity_type="incident",
        entity_id=incident_id,
    )
    return Message(detail="Incident deleted")
