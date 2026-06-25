"""Schemas for the Security Center."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PasswordPolicyOut(BaseModel):
    min_length: int
    require_upper: bool
    require_lower: bool
    require_digit: bool
    require_symbol: bool
    lockout_threshold: int
    lockout_minutes: int


class SecurityOverview(BaseModel):
    security_score: int
    grade: str
    total_users: int
    mfa_enabled_users: int
    mfa_adoption_pct: float
    verified_users: int
    locked_users: int
    active_sessions: int
    failed_logins_24h: int
    successful_logins_24h: int
    audit_events_7d: int
    security_events_7d: int
    password_policy: PasswordPolicyOut
    recommendations: list[str]


class LoginActivityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    successful: bool
    reason: str | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    created_at: datetime


class ActiveSessionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    device_label: str | None = None
    ip_address: str | None = None
    issued_at: datetime
    last_used_at: datetime | None = None
    expires_at: datetime
