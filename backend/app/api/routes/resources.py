"""Resource Operations endpoints."""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_manager
from app.database import get_db
from app.models import Incident, Resource, ResourceAssignment, User, enums
from app.schemas.common import Page, PaginationParams
from app.schemas.entities import (
    ResourceAssignmentCreate,
    ResourceAssignmentOut,
    ResourceCreate,
    ResourceOut,
    ResourceUpdate,
)
from app.services import audit_service
from app.services.common import paginate

router = APIRouter(prefix="/resources", tags=["Resources"])


@router.get("", response_model=Page[ResourceOut])
def list_resources(
    params: PaginationParams = Depends(),
    resource_type: enums.ResourceType | None = Query(None),
    resource_status: enums.ResourceStatus | None = Query(None, alias="status"),
    region: str | None = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> Page[ResourceOut]:
    stmt = select(Resource)
    if resource_type:
        stmt = stmt.where(Resource.resource_type == resource_type)
    if resource_status:
        stmt = stmt.where(Resource.status == resource_status)
    if region:
        stmt = stmt.where(Resource.region == region)
    items, total = paginate(db, stmt, Resource, params, ("name", "region", "home_base"), "name")
    return Page.create(
        [ResourceOut.model_validate(r) for r in items], total, params.page, params.page_size
    )


@router.get("/utilization")
def utilization_analytics(
    db: Session = Depends(get_db), _: User = Depends(get_current_user)
) -> dict:
    rows = db.execute(
        select(Resource.resource_type, Resource.status, func.count()).group_by(
            Resource.resource_type, Resource.status
        )
    ).all()
    by_type: dict[str, dict] = {}
    for rtype, rstatus, count in rows:
        bucket = by_type.setdefault(rtype.value, {"total": 0, "by_status": {}})
        bucket["total"] += count
        bucket["by_status"][rstatus.value] = count
    for bucket in by_type.values():
        available = bucket["by_status"].get("available", 0)
        bucket["availability_pct"] = round(
            (available / bucket["total"] * 100) if bucket["total"] else 0, 1
        )
        assigned = sum(bucket["by_status"].get(s, 0) for s in ("assigned", "en_route", "on_scene"))
        bucket["utilization_pct"] = round(
            (assigned / bucket["total"] * 100) if bucket["total"] else 0, 1
        )
    return {"by_type": by_type}


@router.get("/{resource_id}", response_model=ResourceOut)
def get_resource(
    resource_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)
) -> Resource:
    resource = db.get(Resource, resource_id)
    if not resource:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Resource not found")
    return resource


@router.post("", response_model=ResourceOut, status_code=status.HTTP_201_CREATED)
def create_resource(
    payload: ResourceCreate, db: Session = Depends(get_db), user: User = Depends(require_manager)
) -> Resource:
    resource = Resource(**payload.model_dump(), organization_id=user.organization_id)
    db.add(resource)
    db.commit()
    db.refresh(resource)
    audit_service.log(
        db, actor=user, action="create_resource", entity_type="resource", entity_id=resource.id
    )
    return resource


@router.patch("/{resource_id}", response_model=ResourceOut)
def update_resource(
    resource_id: int,
    payload: ResourceUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_manager),
) -> Resource:
    resource = db.get(Resource, resource_id)
    if not resource:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Resource not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(resource, key, value)
    db.commit()
    db.refresh(resource)
    audit_service.log(
        db, actor=user, action="update_resource", entity_type="resource", entity_id=resource.id
    )
    return resource


@router.post(
    "/assignments", response_model=ResourceAssignmentOut, status_code=status.HTTP_201_CREATED
)
def assign_resource(
    payload: ResourceAssignmentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_manager),
) -> ResourceAssignment:
    resource = db.get(Resource, payload.resource_id)
    if not resource:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Resource not found")
    if payload.incident_id and not db.get(Incident, payload.incident_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Incident not found")
    assignment = ResourceAssignment(
        organization_id=user.organization_id,
        resource_id=payload.resource_id,
        incident_id=payload.incident_id,
        assigned_by_id=user.id,
        quantity=payload.quantity,
        role=payload.role,
        notes=payload.notes,
        assigned_at=datetime.now(UTC),
        active=True,
    )
    resource.status = enums.ResourceStatus.ASSIGNED
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    audit_service.log(
        db,
        actor=user,
        action="assign_resource",
        entity_type="resource_assignment",
        entity_id=assignment.id,
        detail={"resource_id": payload.resource_id, "incident_id": payload.incident_id},
    )
    return assignment


@router.get("/assignments/all", response_model=list[ResourceAssignmentOut])
def list_assignments(
    active_only: bool = Query(True),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[ResourceAssignment]:
    stmt = select(ResourceAssignment).order_by(ResourceAssignment.assigned_at.desc())
    if active_only:
        stmt = stmt.where(ResourceAssignment.active.is_(True))
    return list(db.scalars(stmt.limit(200)).all())


@router.post("/assignments/{assignment_id}/release", response_model=ResourceAssignmentOut)
def release_assignment(
    assignment_id: int, db: Session = Depends(get_db), user: User = Depends(require_manager)
) -> ResourceAssignment:
    assignment = db.get(ResourceAssignment, assignment_id)
    if not assignment:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Assignment not found")
    assignment.active = False
    assignment.released_at = datetime.now(UTC)
    if assignment.resource:
        assignment.resource.status = enums.ResourceStatus.AVAILABLE
    db.commit()
    db.refresh(assignment)
    audit_service.log(
        db,
        actor=user,
        action="release_assignment",
        entity_type="resource_assignment",
        entity_id=assignment.id,
    )
    return assignment
