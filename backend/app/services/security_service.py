"""Security Center analytics: posture score, activity, and recommendations.

All queries are explicitly scoped to the caller's organization (login attempts and
sessions are not part of the automatic tenant filter set, so isolation is enforced
here by filtering on ``organization_id``).
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import settings
from app.models import AuditLog, LoginAttempt, Organization, User, UserSession


def _now() -> datetime:
    return datetime.now(UTC)


def password_policy() -> dict:
    return {
        "min_length": settings.PASSWORD_MIN_LENGTH,
        "require_upper": settings.PASSWORD_REQUIRE_UPPER,
        "require_lower": settings.PASSWORD_REQUIRE_LOWER,
        "require_digit": settings.PASSWORD_REQUIRE_DIGIT,
        "require_symbol": settings.PASSWORD_REQUIRE_SYMBOL,
        "lockout_threshold": settings.MAX_FAILED_LOGINS,
        "lockout_minutes": settings.LOCKOUT_MINUTES,
    }


def overview(db: Session, org_id: int) -> dict:
    day_ago = _now() - timedelta(hours=24)
    week_ago = _now() - timedelta(days=7)

    users = list(db.scalars(select(User).where(User.organization_id == org_id)).all())
    total_users = len(users)
    mfa_users = sum(1 for u in users if u.mfa_enabled)
    verified_users = sum(1 for u in users if u.is_verified)
    locked_users = sum(1 for u in users if u.locked_until and _aware(u.locked_until) > _now())

    failed_24h = (
        db.scalar(
            select(func.count(LoginAttempt.id)).where(
                LoginAttempt.organization_id == org_id,
                LoginAttempt.successful.is_(False),
                LoginAttempt.created_at >= day_ago,
            )
        )
        or 0
    )
    success_24h = (
        db.scalar(
            select(func.count(LoginAttempt.id)).where(
                LoginAttempt.organization_id == org_id,
                LoginAttempt.successful.is_(True),
                LoginAttempt.created_at >= day_ago,
            )
        )
        or 0
    )
    active_sessions = (
        db.scalar(
            select(func.count(UserSession.id)).where(
                UserSession.organization_id == org_id,
                UserSession.revoked_at.is_(None),
                UserSession.expires_at > _now(),
            )
        )
        or 0
    )
    audit_7d = (
        db.scalar(
            select(func.count(AuditLog.id)).where(
                AuditLog.organization_id == org_id, AuditLog.created_at >= week_ago
            )
        )
        or 0
    )
    security_events_7d = (
        db.scalar(
            select(func.count(AuditLog.id)).where(
                AuditLog.organization_id == org_id,
                AuditLog.category == "security",
                AuditLog.created_at >= week_ago,
            )
        )
        or 0
    )

    org = db.get(Organization, org_id)
    score, recommendations = _score(
        total_users=total_users,
        mfa_users=mfa_users,
        verified_users=verified_users,
        failed_24h=failed_24h,
        is_demo=bool(org and org.is_demo),
    )

    return {
        "security_score": score,
        "grade": _grade(score),
        "total_users": total_users,
        "mfa_enabled_users": mfa_users,
        "mfa_adoption_pct": round((mfa_users / total_users * 100) if total_users else 0, 1),
        "verified_users": verified_users,
        "locked_users": locked_users,
        "active_sessions": active_sessions,
        "failed_logins_24h": failed_24h,
        "successful_logins_24h": success_24h,
        "audit_events_7d": audit_7d,
        "security_events_7d": security_events_7d,
        "password_policy": password_policy(),
        "recommendations": recommendations,
    }


def recent_login_activity(db: Session, org_id: int, limit: int = 25) -> list[LoginAttempt]:
    stmt = (
        select(LoginAttempt)
        .where(LoginAttempt.organization_id == org_id)
        .order_by(LoginAttempt.created_at.desc())
        .limit(limit)
    )
    return list(db.scalars(stmt).all())


def active_sessions(db: Session, org_id: int) -> list[UserSession]:
    stmt = (
        select(UserSession)
        .where(
            UserSession.organization_id == org_id,
            UserSession.revoked_at.is_(None),
            UserSession.expires_at > _now(),
        )
        .order_by(UserSession.last_used_at.desc())
    )
    return list(db.scalars(stmt).all())


def _aware(dt: datetime) -> datetime:
    return dt if dt.tzinfo else dt.replace(tzinfo=UTC)


def _score(
    *, total_users: int, mfa_users: int, verified_users: int, failed_24h: int, is_demo: bool
) -> tuple[int, list[str]]:
    score = 100
    recs: list[str] = []

    if total_users:
        mfa_ratio = mfa_users / total_users
        if mfa_ratio < 1.0:
            penalty = int((1 - mfa_ratio) * 30)
            score -= penalty
            recs.append("Enable multi-factor authentication for all users.")
        verify_ratio = verified_users / total_users
        if verify_ratio < 1.0:
            score -= int((1 - verify_ratio) * 10)
            recs.append("Ensure every user has verified their email address.")

    if failed_24h > 20:
        score -= 15
        recs.append("Investigate the elevated number of failed login attempts.")
    elif failed_24h > 5:
        score -= 5
        recs.append("Monitor recent failed login attempts.")

    if not settings.is_production:
        recs.append("Set ENVIRONMENT=production and supply strong secrets before deployment.")
    if is_demo:
        recs.append("This is a demo workspace with synthetic data; not for production use.")
    if not settings.COOKIE_SECURE:
        recs.append("Enable COOKIE_SECURE (HTTPS-only cookies) in production.")

    score = max(0, min(100, score))
    if not recs:
        recs.append("Security posture is strong. Keep dependencies and audit reviews current.")
    return score, recs


def _grade(score: int) -> str:
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    if score >= 60:
        return "D"
    return "F"
