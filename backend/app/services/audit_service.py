"""Immutable audit logging service.

Audit entries are append-only (enforced in ``app.core.audit_guard``). Request
context (correlation id, client IP, user agent) is captured automatically.
Secrets are never recorded — callers must pass only non-sensitive field diffs.
"""
from __future__ import annotations

import logging

from sqlalchemy.orm import Session

from app.core.context import (
    current_client_ip,
    current_correlation_id,
    current_user_agent,
)
from app.models import AuditLog, User

security_logger = logging.getLogger("eocc.security")

_REDACT_KEYS = {"password", "hashed_password", "secret", "token", "mfa_secret", "api_key"}


def _redact(value: dict | None) -> dict | None:
    if not value:
        return value
    return {
        k: ("***" if any(s in k.lower() for s in _REDACT_KEYS) else v)
        for k, v in value.items()
    }


def log(
    db: Session,
    *,
    actor: User | None,
    action: str,
    category: str = "general",
    entity_type: str | None = None,
    entity_id: str | int | None = None,
    detail: dict | None = None,
    old_value: dict | None = None,
    new_value: dict | None = None,
    ip_address: str | None = None,
    commit: bool = True,
) -> AuditLog:
    entry = AuditLog(
        organization_id=actor.organization_id if actor else None,
        actor_id=actor.id if actor else None,
        actor_email=actor.email if actor else None,
        action=action,
        category=category,
        entity_type=entity_type,
        entity_id=str(entity_id) if entity_id is not None else None,
        detail=_redact(detail),
        old_value=_redact(old_value),
        new_value=_redact(new_value),
        ip_address=ip_address or current_client_ip(),
        user_agent=current_user_agent(),
        correlation_id=current_correlation_id(),
    )
    db.add(entry)
    if category == "security":
        security_logger.warning(
            "SECURITY action=%s actor=%s entity=%s/%s ip=%s correlation=%s",
            action,
            entry.actor_email or "anonymous",
            entity_type,
            entry.entity_id,
            entry.ip_address,
            entry.correlation_id,
        )
    if commit:
        db.commit()
        db.refresh(entry)
    return entry
