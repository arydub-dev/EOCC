"""Audit log schemas."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AuditLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    actor_id: int | None = None
    actor_email: str | None = None
    action: str
    category: str = "general"
    entity_type: str | None = None
    entity_id: str | None = None
    detail: dict | None = None
    old_value: dict | None = None
    new_value: dict | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    correlation_id: str | None = None
    created_at: datetime
