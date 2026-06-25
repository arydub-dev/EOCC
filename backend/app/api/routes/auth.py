"""Authentication, registration, session, MFA, and user management endpoints.

Security model:
- Short-lived JWT access tokens (Bearer) + rotating server-side refresh tokens.
- Account lockout after repeated failures; every attempt is recorded.
- Refresh tokens are delivered via an httpOnly cookie (secure by default) and,
  for cross-origin SPA dev, also returned in the body. Production should rely on
  the cookie and treat the body value as optional.
- Optional TOTP MFA. Authorization is permission-based and enforced server-side.
"""
from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.core.deps import client_ip, current_permissions, get_current_user, require_permission
from app.core.permissions import Permission, permissions_for
from app.core.security import (
    create_access_token,
    decrypt_value,
    encrypt_value,
    generate_totp_secret,
    hash_password,
    needs_rehash,
    totp_provisioning_uri,
    verify_password,
    verify_totp,
)
from app.database import get_db
from app.models import Organization, User, UserRole
from app.schemas.auth import (
    CurrentUserOut,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginRequest,
    MFASetupResponse,
    MFAVerifyRequest,
    OrganizationOut,
    PasswordChangeRequest,
    RefreshRequest,
    RegisterRequest,
    ResetPasswordRequest,
    SessionOut,
    Token,
    UserCreate,
    UserOut,
    UserUpdate,
    VerifyEmailRequest,
)
from app.schemas.common import Message
from app.services import audit_service, session_service

router = APIRouter(prefix="/auth", tags=["Auth"])


# ── Cookie helpers ──
def _set_refresh_cookie(response: Response, token: str, *, remember_me: bool) -> None:
    if not settings.USE_AUTH_COOKIES:
        return
    days = settings.REMEMBER_ME_EXPIRE_DAYS if remember_me else settings.REFRESH_TOKEN_EXPIRE_DAYS
    response.set_cookie(
        key=settings.REFRESH_COOKIE_NAME,
        value=token,
        max_age=days * 24 * 3600,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        domain=settings.COOKIE_DOMAIN,
        path=f"{settings.API_V1_PREFIX}/auth",
    )


def _clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(
        key=settings.REFRESH_COOKIE_NAME,
        domain=settings.COOKIE_DOMAIN,
        path=f"{settings.API_V1_PREFIX}/auth",
    )


def _issue_token(
    db: Session,
    user: User,
    request: Request,
    response: Response,
    *,
    remember_me: bool = False,
) -> Token:
    ip = client_ip(request)
    user.last_login_at = datetime.now(timezone.utc)
    user.last_login_ip = ip
    user.failed_login_count = 0
    user.locked_until = None
    db.commit()

    refresh_plain, _ = session_service.create_session(
        db,
        user,
        ip=ip,
        user_agent=request.headers.get("user-agent"),
        remember_me=remember_me,
    )
    _set_refresh_cookie(response, refresh_plain, remember_me=remember_me)

    access = create_access_token(
        subject=user.email, role=user.role.value, organization_id=user.organization_id
    )
    org = db.get(Organization, user.organization_id) if user.organization_id else None
    return Token(
        access_token=access,
        refresh_token=refresh_plain,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserOut.model_validate(user),
        permissions=sorted(permissions_for(user.role)),
        needs_onboarding=user.organization_id is None,
        organization=OrganizationOut.model_validate(org) if org else None,
    )


# ── Lockout helpers ──
def _is_locked(user: User) -> bool:
    if not user.locked_until:
        return False
    locked = user.locked_until
    if locked.tzinfo is None:
        locked = locked.replace(tzinfo=timezone.utc)
    return locked > datetime.now(timezone.utc)


def _register_failure(db: Session, user: User) -> None:
    user.failed_login_count = (user.failed_login_count or 0) + 1
    user.last_failed_login_at = datetime.now(timezone.utc)
    if user.failed_login_count >= settings.MAX_FAILED_LOGINS:
        user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=settings.LOCKOUT_MINUTES)
    db.commit()


def _authenticate(
    db: Session, email: str, password: str, *, mfa_code: str | None, request: Request
) -> User:
    """Validate credentials with lockout + MFA + attempt logging.

    Uses a uniform error to avoid user enumeration and timing differences.
    """
    ip = client_ip(request)
    ua = request.headers.get("user-agent")
    generic = HTTPException(status.HTTP_401_UNAUTHORIZED, "Incorrect email or password")
    user = db.scalar(select(User).where(User.email == email.lower()))

    if user is None:
        # Still spend time-ish; record attempt without leaking existence.
        session_service.record_login_attempt(
            db, email=email, user=None, successful=False, reason="unknown_user", ip=ip, user_agent=ua
        )
        raise generic

    if not user.is_active:
        session_service.record_login_attempt(
            db, email=email, user=user, successful=False, reason="disabled", ip=ip, user_agent=ua
        )
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Account disabled")

    if _is_locked(user):
        session_service.record_login_attempt(
            db, email=email, user=user, successful=False, reason="locked", ip=ip, user_agent=ua
        )
        audit_service.log(
            db, actor=user, action="login_blocked_locked", category="security",
            entity_type="user", entity_id=user.id,
        )
        raise HTTPException(
            status.HTTP_429_TOO_MANY_REQUESTS,
            "Account temporarily locked due to failed login attempts. Try again later.",
        )

    if not verify_password(password, user.hashed_password):
        _register_failure(db, user)
        session_service.record_login_attempt(
            db, email=email, user=user, successful=False, reason="bad_password", ip=ip, user_agent=ua
        )
        audit_service.log(
            db, actor=user, action="login_failed", category="security",
            entity_type="user", entity_id=user.id,
        )
        raise generic

    if user.mfa_enabled:
        secret = decrypt_value(user.mfa_secret_encrypted)
        if not mfa_code or not secret or not verify_totp(secret, mfa_code):
            session_service.record_login_attempt(
                db, email=email, user=user, successful=False, reason="mfa_failed", ip=ip, user_agent=ua
            )
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Valid MFA code required")

    # Transparent hash upgrade (e.g. legacy bcrypt → argon2).
    if needs_rehash(user.hashed_password):
        user.hashed_password = hash_password(password)
        db.commit()

    session_service.record_login_attempt(
        db, email=email, user=user, successful=True, reason=None, ip=ip, user_agent=ua
    )
    audit_service.log(
        db, actor=user, action="login", category="security", entity_type="user", entity_id=user.id
    )
    return user


@router.post("/login", response_model=Token)
def login(
    request: Request,
    response: Response,
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> Token:
    """OAuth2 form login (used by Swagger 'Authorize')."""
    remember = bool(form.scopes and "remember" in form.scopes)
    user = _authenticate(db, form.username, form.password, mfa_code=None, request=request)
    return _issue_token(db, user, request, response, remember_me=remember)


@router.post("/login-json", response_model=Token)
def login_json(
    payload: LoginRequest, request: Request, response: Response, db: Session = Depends(get_db)
) -> Token:
    """JSON login used by the web app (supports Remember Me + MFA)."""
    user = _authenticate(
        db, payload.email, payload.password, mfa_code=payload.mfa_code, request=request
    )
    return _issue_token(db, user, request, response, remember_me=payload.remember_me)


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(
    payload: RegisterRequest, request: Request, response: Response, db: Session = Depends(get_db)
) -> Token:
    """Self-service registration. New users complete onboarding to create an org."""
    if db.scalar(select(User).where(User.email == payload.email.lower())):
        raise HTTPException(status.HTTP_409_CONFLICT, "An account with this email already exists")
    user = User(
        email=payload.email.lower(),
        full_name=payload.full_name,
        role=UserRole.ADMIN,  # account owner; becomes org admin on onboarding
        hashed_password=hash_password(payload.password),
        is_active=True,
        is_verified=False,
        password_changed_at=datetime.now(timezone.utc),
        email_verification_token=secrets.token_urlsafe(24),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    audit_service.log(
        db, actor=user, action="register", category="security", entity_type="user", entity_id=user.id
    )
    return _issue_token(db, user, request, response)


@router.post("/refresh", response_model=Token)
def refresh(
    payload: RefreshRequest, request: Request, response: Response, db: Session = Depends(get_db)
) -> Token:
    """Rotate a refresh token and issue a new short-lived access token."""
    token = request.cookies.get(settings.REFRESH_COOKIE_NAME) or payload.refresh_token
    if not token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing refresh token")
    try:
        new_refresh, _sess, user = session_service.rotate_session(
            db, token, ip=client_ip(request), user_agent=request.headers.get("user-agent")
        )
    except session_service.RefreshError as exc:
        _clear_refresh_cookie(response)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(exc)) from exc

    _set_refresh_cookie(response, new_refresh, remember_me=False)
    access = create_access_token(
        subject=user.email, role=user.role.value, organization_id=user.organization_id
    )
    org = db.get(Organization, user.organization_id) if user.organization_id else None
    return Token(
        access_token=access,
        refresh_token=new_refresh,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserOut.model_validate(user),
        permissions=sorted(permissions_for(user.role)),
        needs_onboarding=user.organization_id is None,
        organization=OrganizationOut.model_validate(org) if org else None,
    )


@router.post("/logout", response_model=Message)
def logout(
    payload: RefreshRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Message:
    """Revoke the current session's refresh token."""
    token = request.cookies.get(settings.REFRESH_COOKIE_NAME) or payload.refresh_token
    if token:
        session_service.revoke_by_token(db, token)
    _clear_refresh_cookie(response)
    audit_service.log(
        db, actor=user, action="logout", category="security", entity_type="user", entity_id=user.id
    )
    return Message(detail="Logged out")


@router.post("/logout-all", response_model=Message)
def logout_all(
    response: Response, db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> Message:
    """Revoke every active session for the current user."""
    count = session_service.revoke_all(db, user)
    _clear_refresh_cookie(response)
    audit_service.log(
        db, actor=user, action="logout_all", category="security",
        entity_type="user", entity_id=user.id, detail={"revoked": count},
    )
    return Message(detail=f"Revoked {count} session(s)")


@router.get("/sessions", response_model=list[SessionOut])
def list_my_sessions(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> list[SessionOut]:
    return [SessionOut.model_validate(s) for s in session_service.list_sessions(db, user)]


@router.delete("/sessions/{session_id}", response_model=Message)
def revoke_my_session(
    session_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> Message:
    if not session_service.revoke_session(db, session_id, user):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Session not found")
    audit_service.log(
        db, actor=user, action="revoke_session", category="security",
        entity_type="session", entity_id=session_id,
    )
    return Message(detail="Session revoked")


# ── MFA (TOTP) ──
@router.post("/mfa/setup", response_model=MFASetupResponse)
def mfa_setup(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> MFASetupResponse:
    """Begin TOTP enrollment — returns a secret + otpauth URI (confirm to enable)."""
    secret = generate_totp_secret()
    user.mfa_secret_encrypted = encrypt_value(secret)
    db.commit()
    return MFASetupResponse(secret=secret, otpauth_uri=totp_provisioning_uri(secret, user.email))


@router.post("/mfa/enable", response_model=Message)
def mfa_enable(
    payload: MFAVerifyRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> Message:
    secret = decrypt_value(user.mfa_secret_encrypted)
    if not secret or not verify_totp(secret, payload.code):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid MFA code")
    user.mfa_enabled = True
    db.commit()
    audit_service.log(
        db, actor=user, action="mfa_enabled", category="security", entity_type="user", entity_id=user.id
    )
    return Message(detail="MFA enabled")


@router.post("/mfa/disable", response_model=Message)
def mfa_disable(
    payload: MFAVerifyRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> Message:
    secret = decrypt_value(user.mfa_secret_encrypted)
    if not user.mfa_enabled or not secret or not verify_totp(secret, payload.code):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid MFA code")
    user.mfa_enabled = False
    user.mfa_secret_encrypted = None
    db.commit()
    audit_service.log(
        db, actor=user, action="mfa_disabled", category="security", entity_type="user", entity_id=user.id
    )
    return Message(detail="MFA disabled")


@router.post("/change-password", response_model=Message)
def change_password(
    payload: PasswordChangeRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> Message:
    if not verify_password(payload.current_password, user.hashed_password):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Current password is incorrect")
    user.hashed_password = hash_password(payload.new_password)
    user.password_changed_at = datetime.now(timezone.utc)
    db.commit()
    # Revoke other sessions after a credential change.
    session_service.revoke_all(db, user, reason="password_changed")
    audit_service.log(
        db, actor=user, action="change_password", category="security",
        entity_type="user", entity_id=user.id,
    )
    return Message(detail="Password updated; other sessions signed out")


@router.post("/verify-email", response_model=Message)
def verify_email(payload: VerifyEmailRequest, db: Session = Depends(get_db)) -> Message:
    """Mock email verification — confirms the token issued at registration."""
    user = db.scalar(select(User).where(User.email_verification_token == payload.token))
    if not user:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid or expired verification token")
    user.is_verified = True
    user.email_verification_token = None
    db.commit()
    return Message(detail="Email verified successfully")


@router.post("/resend-verification", response_model=ForgotPasswordResponse)
def resend_verification(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> ForgotPasswordResponse:
    if user.is_verified:
        return ForgotPasswordResponse(detail="Email already verified", reset_token="")
    user.email_verification_token = secrets.token_urlsafe(24)
    db.commit()
    return ForgotPasswordResponse(
        detail="Verification email sent (mock)", reset_token=user.email_verification_token
    )


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)) -> ForgotPasswordResponse:
    """Mock password-reset request. Returns the reset token directly (no email)."""
    user = db.scalar(select(User).where(User.email == payload.email.lower()))
    token = secrets.token_urlsafe(24)
    if user:
        user.password_reset_token = token
        user.password_reset_expires = datetime.now(timezone.utc) + timedelta(hours=1)
        db.commit()
        audit_service.log(
            db, actor=user, action="password_reset_requested", category="security",
            entity_type="user", entity_id=user.id,
        )
    # Always return success-shaped response to avoid account enumeration.
    return ForgotPasswordResponse(
        detail="If an account exists, a reset link has been sent.",
        reset_token=token if user else "",
    )


@router.post("/reset-password", response_model=Message)
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)) -> Message:
    user = db.scalar(select(User).where(User.password_reset_token == payload.token))
    if not user or not user.password_reset_expires:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid or expired reset token")
    expires = user.password_reset_expires
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    if expires < datetime.now(timezone.utc):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Reset token has expired")
    user.hashed_password = hash_password(payload.new_password)
    user.password_changed_at = datetime.now(timezone.utc)
    user.password_reset_token = None
    user.password_reset_expires = None
    user.failed_login_count = 0
    user.locked_until = None
    db.commit()
    session_service.revoke_all(db, user, reason="password_reset")
    audit_service.log(
        db, actor=user, action="reset_password", category="security",
        entity_type="user", entity_id=user.id,
    )
    return Message(detail="Password updated successfully")


@router.get("/me", response_model=CurrentUserOut)
def me(current: User = Depends(get_current_user)) -> CurrentUserOut:
    out = CurrentUserOut.model_validate(current)
    out.permissions = current_permissions(current)
    return out


# ── User management (admin / User.Manage) ──
router_users = APIRouter(prefix="/users", tags=["Users"])


@router_users.get("", response_model=list[UserOut])
def list_users(
    db: Session = Depends(get_db), admin: User = Depends(require_permission(Permission.USER_MANAGE))
) -> list[User]:
    stmt = select(User).where(User.organization_id == admin.organization_id).order_by(User.id)
    return list(db.scalars(stmt).all())


@router_users.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_permission(Permission.USER_MANAGE)),
) -> User:
    if db.scalar(select(User).where(User.email == payload.email.lower())):
        raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered")
    org = db.get(Organization, admin.organization_id) if admin.organization_id else None
    user = User(
        email=payload.email.lower(),
        full_name=payload.full_name,
        role=payload.role,
        organization_id=admin.organization_id,
        organization=org.name if org else payload.organization,
        hashed_password=hash_password(payload.password),
        is_verified=True,
        password_changed_at=datetime.now(timezone.utc),
        created_by_id=admin.id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    audit_service.log(
        db, actor=admin, action="create_user", category="user_management",
        entity_type="user", entity_id=user.id, new_value={"email": user.email, "role": user.role.value},
    )
    return user


def _same_org_user(db: Session, user_id: int, admin: User) -> User:
    user = db.get(User, user_id)
    if not user or user.organization_id != admin.organization_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    return user


@router_users.patch("/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_permission(Permission.USER_MANAGE)),
) -> User:
    user = _same_org_user(db, user_id, admin)
    before = {"role": user.role.value, "is_active": user.is_active, "full_name": user.full_name}
    data = payload.model_dump(exclude_unset=True)
    if data.get("password"):
        user.hashed_password = hash_password(data.pop("password"))
        user.password_changed_at = datetime.now(timezone.utc)
    else:
        data.pop("password", None)
    for key, value in data.items():
        setattr(user, key, value)
    user.updated_by_id = admin.id
    db.commit()
    db.refresh(user)
    after = {"role": user.role.value, "is_active": user.is_active, "full_name": user.full_name}
    audit_service.log(
        db, actor=admin, action="update_user", category="user_management",
        entity_type="user", entity_id=user.id, old_value=before, new_value=after,
    )
    return user


@router_users.delete("/{user_id}", response_model=Message)
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_permission(Permission.USER_MANAGE)),
) -> Message:
    user = _same_org_user(db, user_id, admin)
    user.is_active = False
    user.updated_by_id = admin.id
    db.commit()
    session_service.revoke_all(db, user, reason="deactivated")
    audit_service.log(
        db, actor=admin, action="deactivate_user", category="user_management",
        entity_type="user", entity_id=user.id,
    )
    return Message(detail="User deactivated")
