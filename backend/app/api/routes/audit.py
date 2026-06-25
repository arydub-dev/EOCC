"""Audit Center endpoints (Audit.View). Audit records are immutable."""
from __future__ import annotations

import csv
import io
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import require_permission
from app.core.permissions import Permission
from app.database import get_db
from app.models import AuditLog, User
from app.schemas.audit import AuditLogOut
from app.schemas.common import Page, PaginationParams
from app.services import audit_service
from app.services.common import paginate
from app.services.file_security import sanitize_cell

router = APIRouter(prefix="/audit", tags=["Audit Center"])


def _filtered(stmt, *, action, category, entity_type, actor_email, start, end):  # noqa: ANN001
    if action:
        stmt = stmt.where(AuditLog.action == action)
    if category:
        stmt = stmt.where(AuditLog.category == category)
    if entity_type:
        stmt = stmt.where(AuditLog.entity_type == entity_type)
    if actor_email:
        stmt = stmt.where(AuditLog.actor_email.ilike(f"%{actor_email}%"))
    if start:
        stmt = stmt.where(AuditLog.created_at >= start)
    if end:
        stmt = stmt.where(AuditLog.created_at <= end)
    return stmt


@router.get("", response_model=Page[AuditLogOut])
def list_audit(
    params: PaginationParams = Depends(),
    action: str | None = Query(None),
    category: str | None = Query(None),
    entity_type: str | None = Query(None),
    actor_email: str | None = Query(None),
    start: datetime | None = Query(None),
    end: datetime | None = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(require_permission(Permission.AUDIT_VIEW)),
) -> Page[AuditLogOut]:
    stmt = _filtered(
        select(AuditLog),
        action=action, category=category, entity_type=entity_type,
        actor_email=actor_email, start=start, end=end,
    )
    items, total = paginate(
        db, stmt, AuditLog, params, ("action", "actor_email", "entity_type", "category"), "created_at"
    )
    return Page.create([AuditLogOut.model_validate(a) for a in items], total, params.page, params.page_size)


@router.get("/export")
def export_audit(
    action: str | None = Query(None),
    category: str | None = Query(None),
    entity_type: str | None = Query(None),
    actor_email: str | None = Query(None),
    start: datetime | None = Query(None),
    end: datetime | None = Query(None),
    db: Session = Depends(get_db),
    user: User = Depends(require_permission(Permission.AUDIT_VIEW)),
) -> StreamingResponse:
    """Export filtered audit records as CSV (injection-safe)."""
    stmt = _filtered(
        select(AuditLog),
        action=action, category=category, entity_type=entity_type,
        actor_email=actor_email, start=start, end=end,
    ).order_by(AuditLog.created_at.desc()).limit(50_000)
    rows = list(db.scalars(stmt).all())

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        ["timestamp", "actor", "category", "action", "entity_type", "entity_id", "ip_address", "correlation_id"]
    )
    for r in rows:
        writer.writerow(
            [
                r.created_at.isoformat() if r.created_at else "",
                sanitize_cell(r.actor_email),
                sanitize_cell(r.category),
                sanitize_cell(r.action),
                sanitize_cell(r.entity_type),
                sanitize_cell(r.entity_id),
                sanitize_cell(r.ip_address),
                sanitize_cell(r.correlation_id),
            ]
        )
    audit_service.log(
        db, actor=user, action="export_audit", category="security",
        entity_type="audit_log", detail={"rows": len(rows)},
    )
    buffer.seek(0)
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=audit-log.csv"},
    )
