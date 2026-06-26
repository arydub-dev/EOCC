"""Refresh-token session lifecycle: issue, rotate, revoke, track.

Implements rotating refresh tokens with theft detection: each refresh issues a
new token and revokes the old one. If a previously-rotated (already replaced)
token is presented again, the entire family is revoked — the canonical defense
against refresh-token replay.
"""

from __future__ import annotations

import secrets
from datetime import UTC, datetime, timedelta

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.config import settings
from app.core.security import generate_refresh_token, hash_refresh_token
from app.models import LoginAttempt, User, UserSession


class RefreshError(Exception):
    """Raised when a refresh token is invalid, expired, or reused."""


def _now() -> datetime:
    return datetime.now(UTC)


def _aware(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=UTC)


def device_label(user_agent: str | None) -> str:
    if not user_agent:
        return "Unknown device"
    ua = user_agent.lower()
    os = "Unknown OS"
    for needle, label in (
        ("windows", "Windows"),
        ("mac os", "macOS"),
        ("iphone", "iPhone"),
        ("android", "Android"),
        ("linux", "Linux"),
    ):
        if needle in ua:
            os = label
            break
    browser = "browser"
    for needle, label in (
        ("edg", "Edge"),
        ("chrome", "Chrome"),
        ("firefox", "Firefox"),
        ("safari", "Safari"),
    ):
        if needle in ua:
            browser = label
            break
    return f"{browser} on {os}"


def create_session(
    db: Session,
    user: User,
    *,
    ip: str | None,
    user_agent: str | None,
    remember_me: bool = False,
    family_id: str | None = None,
    commit: bool = True,
) -> tuple[str, UserSession]:
    token = generate_refresh_token()
    days = settings.REMEMBER_ME_EXPIRE_DAYS if remember_me else settings.REFRESH_TOKEN_EXPIRE_DAYS
    sess = UserSession(
        user_id=user.id,
        organization_id=user.organization_id,
        family_id=family_id or secrets.token_urlsafe(16),
        refresh_token_hash=hash_refresh_token(token),
        issued_at=_now(),
        expires_at=_now() + timedelta(days=days),
        last_used_at=_now(),
        ip_address=ip,
        user_agent=(user_agent or "")[:400],
        device_label=device_label(user_agent),
    )
    db.add(sess)
    if commit:
        db.commit()
        db.refresh(sess)
    return token, sess


def rotate_session(
    db: Session, refresh_token: str, *, ip: str | None, user_agent: str | None
) -> tuple[str, UserSession, User]:
    token_hash = hash_refresh_token(refresh_token)
    sess = db.scalar(select(UserSession).where(UserSession.refresh_token_hash == token_hash))
    if sess is None:
        raise RefreshError("Invalid refresh token")

    # Reuse detection: a token that was already rotated/revoked is being replayed.
    if sess.revoked_at is not None:
        _revoke_family(db, sess.family_id, reason="reuse_detected")
        db.commit()
        raise RefreshError("Refresh token reuse detected; sessions revoked")

    if _aware(sess.expires_at) < _now():
        sess.revoked_at = _now()
        sess.revoked_reason = "expired"
        db.commit()
        raise RefreshError("Refresh token expired")

    user = db.get(User, sess.user_id)
    if user is None or not user.is_active:
        raise RefreshError("Account unavailable")

    # Issue replacement in the same family, revoke the old token.
    new_token, new_sess = create_session(
        db,
        user,
        ip=ip,
        user_agent=user_agent,
        family_id=sess.family_id,
        commit=False,
    )
    db.flush()
    sess.revoked_at = _now()
    sess.revoked_reason = "rotated"
    sess.replaced_by_id = new_sess.id
    db.commit()
    db.refresh(new_sess)
    return new_token, new_sess, user


def revoke_by_token(db: Session, refresh_token: str) -> None:
    token_hash = hash_refresh_token(refresh_token)
    sess = db.scalar(select(UserSession).where(UserSession.refresh_token_hash == token_hash))
    if sess and sess.revoked_at is None:
        sess.revoked_at = _now()
        sess.revoked_reason = "logout"
        db.commit()


def revoke_session(db: Session, session_id: int, user: User) -> bool:
    sess = db.get(UserSession, session_id)
    if not sess or sess.user_id != user.id:
        return False
    if sess.revoked_at is None:
        sess.revoked_at = _now()
        sess.revoked_reason = "user_revoked"
        db.commit()
    return True


def revoke_all(db: Session, user: User, reason: str = "logout_all") -> int:
    result = db.execute(
        update(UserSession)
        .where(UserSession.user_id == user.id, UserSession.revoked_at.is_(None))
        .values(revoked_at=_now(), revoked_reason=reason)
    )
    db.commit()
    return result.rowcount or 0


def _revoke_family(db: Session, family_id: str, reason: str) -> None:
    db.execute(
        update(UserSession)
        .where(UserSession.family_id == family_id, UserSession.revoked_at.is_(None))
        .values(revoked_at=_now(), revoked_reason=reason)
    )


def list_sessions(db: Session, user: User, *, active_only: bool = False) -> list[UserSession]:
    stmt = select(UserSession).where(UserSession.user_id == user.id)
    if active_only:
        stmt = stmt.where(UserSession.revoked_at.is_(None), UserSession.expires_at > _now())
    return list(db.scalars(stmt.order_by(UserSession.issued_at.desc())).all())


def record_login_attempt(
    db: Session,
    *,
    email: str,
    user: User | None,
    successful: bool,
    reason: str | None,
    ip: str | None,
    user_agent: str | None,
    commit: bool = True,
) -> LoginAttempt:
    attempt = LoginAttempt(
        email=email[:255],
        user_id=user.id if user else None,
        organization_id=user.organization_id if user else None,
        successful=successful,
        reason=reason,
        ip_address=ip,
        user_agent=(user_agent or "")[:400],
    )
    db.add(attempt)
    if commit:
        db.commit()
    return attempt
