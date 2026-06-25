"""Onboarding and workspace endpoints (organization provisioning + provenance)."""
from __future__ import annotations

import re
import secrets

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_onboarded
from app.core.tenancy import set_session_org
from app.database import get_db
from app.models import (
    Alert,
    DataSource,
    Hospital,
    Incident,
    Organization,
    Resource,
    Shelter,
    User,
    UtilityOutage,
    enums,
)
from app.schemas.auth import OnboardingRequest, OrganizationOut, WorkspaceInfo
from app.services import audit_service, provisioning

router = APIRouter(tags=["Workspace"])


def _slugify(name: str, db: Session) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")[:80] or "org"
    slug = base
    while db.scalar(select(Organization).where(Organization.slug == slug)):
        slug = f"{base}-{secrets.token_hex(3)}"
    return slug


def _origin_label(origin: str) -> str:
    return {
        "demo": "Demo",
        "manual": "Manual Entry",
        "csv": "CSV",
        "excel": "Excel",
        "api": "API",
        "gis": "GIS",
        "weather_feed": "Weather Feed",
        "hospital_system": "Hospital System",
    }.get(origin, origin.title())


@router.post("/onboarding", response_model=WorkspaceInfo, status_code=status.HTTP_201_CREATED)
def onboarding(
    payload: OnboardingRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> WorkspaceInfo:
    """Create the caller's organization and provision their workspace."""
    if user.organization_id:
        raise HTTPException(status.HTTP_409_CONFLICT, "You already belong to an organization")

    is_demo = payload.mode == enums.WorkspaceMode.DEMO
    org = Organization(
        name=payload.organization_name.strip(),
        slug=_slugify(payload.organization_name, db),
        industry=payload.industry,
        mode=payload.mode,
        plan=enums.Plan.PROFESSIONAL,
        is_demo=is_demo,
        provisioned=False,
        region=payload.region,
    )
    db.add(org)
    db.flush()

    user.organization_id = org.id
    user.organization = org.name
    db.commit()
    set_session_org(db, org.id)

    if is_demo:
        provisioning.provision_demo_workspace(db, org)

    audit_service.log(db, actor=user, action="create_organization", entity_type="organization", entity_id=org.id)
    return _build_workspace_info(db, org)


@router.post("/workspace/launch-demo", response_model=WorkspaceInfo)
def launch_demo(db: Session = Depends(get_db), user: User = Depends(require_onboarded)) -> WorkspaceInfo:
    """Provision demo data into the current (e.g. connected, empty) workspace."""
    org = db.get(Organization, user.organization_id)
    if org is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Organization not found")
    set_session_org(db, org.id)
    provisioning.provision_demo_workspace(db, org)
    org.is_demo = True
    db.commit()
    audit_service.log(db, actor=user, action="launch_demo", entity_type="organization", entity_id=org.id)
    return _build_workspace_info(db, org)


@router.get("/workspace", response_model=WorkspaceInfo)
def get_workspace(db: Session = Depends(get_db), user: User = Depends(require_onboarded)) -> WorkspaceInfo:
    org = db.get(Organization, user.organization_id)
    if org is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Organization not found")
    return _build_workspace_info(db, org)


def _build_workspace_info(db: Session, org: Organization) -> WorkspaceInfo:
    set_session_org(db, org.id)
    counts = {
        "incidents": db.scalar(select(func.count(Incident.id))) or 0,
        "hospitals": db.scalar(select(func.count(Hospital.id))) or 0,
        "shelters": db.scalar(select(func.count(Shelter.id))) or 0,
        "resources": db.scalar(select(func.count(Resource.id))) or 0,
        "utility_outages": db.scalar(select(func.count(UtilityOutage.id))) or 0,
        "alerts": db.scalar(select(func.count(Alert.id))) or 0,
        "data_sources": db.scalar(select(func.count(DataSource.id))) or 0,
    }
    total = sum(v for k, v in counts.items() if k != "data_sources")

    origins = set(db.scalars(select(Incident.data_origin).distinct()).all())
    origins |= set(db.scalars(select(Hospital.data_origin).distinct()).all())
    origins |= set(db.scalars(select(Resource.data_origin).distinct()).all())
    origins |= set(db.scalars(select(Alert.data_origin).distinct()).all())
    origin_values = sorted({o.value if hasattr(o, "value") else str(o) for o in origins})

    if org.is_demo and "demo" in origin_values:
        primary = "demo"
    elif origin_values:
        primary = origin_values[0]
    else:
        primary = "none"

    return WorkspaceInfo(
        organization=OrganizationOut.model_validate(org),
        data_sources_in_use=[_origin_label(o) for o in origin_values],
        primary_data_origin=primary,
        record_counts=counts,
        is_empty=total == 0,
    )
