"""Authentication / authorization dependencies.

Authorization is enforced server-side only. Endpoints declare the *permission*
they require via :func:`require_permission`; roles are mapped to permissions in
``app.core.permissions``. Coarse role checks remain available for convenience.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.core.permissions import has_permission, permissions_for
from app.core.security import decode_access_token
from app.core.tenancy import set_session_org
from app.database import get_db
from app.models import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_PREFIX}/auth/login", auto_error=True
)

# Role hierarchy — higher value implies broader access for convenience checks.
ROLE_RANK = {
    UserRole.VIEWER: 0,
    UserRole.EXECUTIVE: 1,
    UserRole.ANALYST: 2,
    UserRole.EMERGENCY_MANAGER: 3,
    UserRole.ADMIN: 4,
}


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None or "sub" not in payload:
        raise credentials_exc
    user = db.scalar(select(User).where(User.email == payload["sub"]))
    if user is None or not user.is_active:
        raise credentials_exc
    # Bind tenant context so every subsequent SELECT on this session is scoped.
    set_session_org(db, user.organization_id)
    return user


def require_onboarded(user: User = Depends(get_current_user)) -> User:
    """Ensures the user has completed onboarding (belongs to an organization)."""
    if not user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Onboarding required: create or join an organization first.",
        )
    return user


def require_roles(*roles: UserRole) -> Callable[..., User]:
    """Dependency factory enforcing that the user holds one of the given roles."""
    allowed: Iterable[UserRole] = roles

    def checker(user: User = Depends(get_current_user)) -> User:
        if user.role == UserRole.ADMIN:
            return user
        if user.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of roles: {', '.join(r.value for r in allowed)}",
            )
        return user

    return checker


def require_permission(*permissions: str) -> Callable[..., User]:
    """Dependency factory enforcing fine-grained permissions (least privilege).

    The user must be onboarded and hold *all* of the requested permissions.
    """

    def checker(user: User = Depends(require_onboarded)) -> User:
        for permission in permissions:
            if not has_permission(user.role, permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Missing required permission: {permission}",
                )
        return user

    return checker


def current_permissions(user: User) -> list[str]:
    return sorted(permissions_for(user.role))


# Common shortcuts (kept for back-compat with existing routers)
require_admin = require_roles(UserRole.ADMIN)
require_manager = require_roles(UserRole.ADMIN, UserRole.EMERGENCY_MANAGER)
require_analyst = require_roles(UserRole.ADMIN, UserRole.ANALYST, UserRole.EMERGENCY_MANAGER)


def client_ip(request: Request) -> str:
    fwd = request.headers.get("x-forwarded-for")
    if fwd:
        return fwd.split(",")[0].strip()
    return request.client.host if request.client else "unknown"
