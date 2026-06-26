"""Security Center endpoints (Security.View / Security.Manage)."""

from __future__ import annotations

from datetime import UTC

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import require_permission
from app.core.permissions import Permission
from app.database import get_db
from app.models import User, UserSession
from app.schemas.common import Message
from app.schemas.security import (
    ActiveSessionOut,
    LoginActivityOut,
    SecurityOverview,
)
from app.services import audit_service, security_service

router = APIRouter(prefix="/security", tags=["Security Center"])


@router.get("/overview", response_model=SecurityOverview)
def overview(
    db: Session = Depends(get_db),
    user: User = Depends(require_permission(Permission.SECURITY_VIEW)),
) -> SecurityOverview:
    return SecurityOverview(**security_service.overview(db, user.organization_id))


@router.get("/login-activity", response_model=list[LoginActivityOut])
def login_activity(
    limit: int = Query(25, ge=1, le=200),
    db: Session = Depends(get_db),
    user: User = Depends(require_permission(Permission.SECURITY_VIEW)),
) -> list[LoginActivityOut]:
    rows = security_service.recent_login_activity(db, user.organization_id, limit=limit)
    return [LoginActivityOut.model_validate(r) for r in rows]


@router.get("/sessions", response_model=list[ActiveSessionOut])
def org_sessions(
    db: Session = Depends(get_db),
    user: User = Depends(require_permission(Permission.SECURITY_VIEW)),
) -> list[ActiveSessionOut]:
    rows = security_service.active_sessions(db, user.organization_id)
    return [ActiveSessionOut.model_validate(r) for r in rows]


@router.delete("/sessions/{session_id}", response_model=Message)
def revoke_org_session(
    session_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_permission(Permission.SECURITY_MANAGE)),
) -> Message:
    """Admin override: revoke any session within the organization."""
    sess = db.get(UserSession, session_id)
    if not sess or sess.organization_id != admin.organization_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Session not found")
    from datetime import datetime

    if sess.revoked_at is None:
        sess.revoked_at = datetime.now(UTC)
        sess.revoked_reason = "admin_revoked"
        db.commit()
    audit_service.log(
        db,
        actor=admin,
        action="admin_revoke_session",
        category="security",
        entity_type="session",
        entity_id=session_id,
    )
    return Message(detail="Session revoked")
