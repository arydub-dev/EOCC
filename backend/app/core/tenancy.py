"""Automatic multi-tenant data isolation.

A single ``do_orm_execute`` listener scopes every SELECT to the organization
stored on the active session (``session.info['org_id']``). This guarantees that
no query can read another tenant's rows, without having to thread an org filter
through every router and service.

Writes still set ``organization_id`` explicitly at creation time.
"""
from __future__ import annotations

from sqlalchemy import event
from sqlalchemy.orm import Session, with_loader_criteria

from app.models.models import (
    AIReport,
    Alert,
    AuditLog,
    DataSource,
    Hospital,
    ImportJob,
    Incident,
    Resource,
    ResourceAssignment,
    RiskAssessment,
    Shelter,
    Simulation,
    UtilityOutage,
)

# Entities that carry an ``organization_id`` and must be tenant-isolated.
TENANT_MODELS = [
    Incident,
    Hospital,
    Shelter,
    Resource,
    ResourceAssignment,
    UtilityOutage,
    RiskAssessment,
    Alert,
    Simulation,
    AIReport,
    DataSource,
    ImportJob,
    AuditLog,
]

# Entities supporting soft delete — deleted rows are hidden from all reads.
SOFT_DELETE_MODELS = [Incident, DataSource]

ORG_KEY = "org_id"


def set_session_org(db: Session, org_id: int | None) -> None:
    """Bind the active organization to a session for the duration of a request."""
    db.info[ORG_KEY] = org_id if org_id is not None else -1


@event.listens_for(Session, "do_orm_execute")
def _apply_tenant_filter(state) -> None:  # noqa: ANN001
    if not state.is_select:
        return

    # Hide soft-deleted rows regardless of tenant context.
    for model in SOFT_DELETE_MODELS:
        state.statement = state.statement.options(
            with_loader_criteria(model, model.deleted_at.is_(None), include_aliases=True)
        )

    org_id = state.session.info.get(ORG_KEY)
    if org_id is None:
        # No tenant context (e.g. seeding / provisioning) → no implicit org filter.
        return
    for model in TENANT_MODELS:
        state.statement = state.statement.options(
            with_loader_criteria(
                model,
                model.organization_id == org_id,
                include_aliases=True,
            )
        )


def register_tenancy() -> None:
    """No-op hook; importing this module registers the listener."""
    return None
