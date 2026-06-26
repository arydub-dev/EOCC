"""Authentication and user schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.core.security import validate_password_policy
from app.models.enums import Industry, Plan, UserRole, WorkspaceMode


def _check_password(value: str) -> str:
    errors = validate_password_policy(value)
    if errors:
        raise ValueError(" ".join(errors))
    return value


class OrganizationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    industry: Industry
    mode: WorkspaceMode
    plan: Plan
    is_demo: bool
    provisioned: bool
    region: str | None = None


class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=1, max_length=255)
    role: UserRole = UserRole.ANALYST
    organization: str | None = None


class UserCreate(UserBase):
    password: str = Field(min_length=12, max_length=256)

    @field_validator("password")
    @classmethod
    def _policy(cls, v: str) -> str:
        return _check_password(v)


class UserUpdate(BaseModel):
    full_name: str | None = Field(default=None, max_length=255)
    role: UserRole | None = None
    organization: str | None = None
    is_active: bool | None = None
    password: str | None = Field(default=None, max_length=256)

    @field_validator("password")
    @classmethod
    def _policy(cls, v: str | None) -> str | None:
        return _check_password(v) if v else v


class UserOut(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    organization_id: int | None = None
    is_active: bool
    is_verified: bool = False
    mfa_enabled: bool = False
    last_login_at: datetime | None = None
    created_at: datetime


class CurrentUserOut(UserOut):
    """`/auth/me` payload — includes the server-resolved permission set."""

    permissions: list[str] = []


class Token(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"
    expires_in: int = 0  # access-token lifetime in seconds
    user: UserOut
    permissions: list[str] = []
    needs_onboarding: bool = False
    organization: OrganizationOut | None = None
    mfa_required: bool = False


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(max_length=256)
    remember_me: bool = False
    mfa_code: str | None = Field(default=None, max_length=10)


class RegisterRequest(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=12, max_length=256)

    @field_validator("password")
    @classmethod
    def _policy(cls, v: str) -> str:
        return _check_password(v)


class RefreshRequest(BaseModel):
    # Optional in body; the refresh token is preferred from an httpOnly cookie.
    refresh_token: str | None = None


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ForgotPasswordResponse(BaseModel):
    detail: str
    # Mock email delivery: token is returned directly for demo/eval purposes.
    reset_token: str


class ResetPasswordRequest(BaseModel):
    token: str = Field(max_length=256)
    new_password: str = Field(min_length=12, max_length=256)

    @field_validator("new_password")
    @classmethod
    def _policy(cls, v: str) -> str:
        return _check_password(v)


class VerifyEmailRequest(BaseModel):
    token: str = Field(max_length=256)


class SessionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    device_label: str | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    issued_at: datetime
    last_used_at: datetime | None = None
    expires_at: datetime
    revoked_at: datetime | None = None
    revoked_reason: str | None = None

    @property
    def active(self) -> bool:  # pragma: no cover - convenience
        return self.revoked_at is None


class MFASetupResponse(BaseModel):
    secret: str
    otpauth_uri: str


class MFAVerifyRequest(BaseModel):
    code: str = Field(min_length=6, max_length=10)


class PasswordChangeRequest(BaseModel):
    current_password: str = Field(max_length=256)
    new_password: str = Field(min_length=12, max_length=256)

    @field_validator("new_password")
    @classmethod
    def _policy(cls, v: str) -> str:
        return _check_password(v)


class OnboardingRequest(BaseModel):
    organization_name: str = Field(min_length=2, max_length=255)
    industry: Industry = Industry.OTHER
    mode: WorkspaceMode = WorkspaceMode.DEMO
    region: str | None = Field(default=None, max_length=120)


class WorkspaceInfo(BaseModel):
    organization: OrganizationOut
    data_sources_in_use: list[str]
    primary_data_origin: str
    record_counts: dict[str, int]
    is_empty: bool


Token.model_rebuild()
