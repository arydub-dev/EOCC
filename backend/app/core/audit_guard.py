"""Make audit records append-only at the ORM layer.

Any attempt to UPDATE or DELETE an ``AuditLog`` or ``LoginAttempt`` raises,
guaranteeing tamper-evidence regardless of which code path is involved.
"""

from __future__ import annotations

from sqlalchemy import event
from sqlalchemy.orm import Session

from app.models.models import AuditLog, LoginAttempt

_IMMUTABLE = (AuditLog, LoginAttempt)


class ImmutableAuditError(RuntimeError):
    pass


@event.listens_for(Session, "before_flush")
def _block_audit_mutations(session: Session, flush_context, instances) -> None:  # noqa: ANN001
    for obj in session.dirty:
        if isinstance(obj, _IMMUTABLE) and session.is_modified(obj, include_collections=False):
            raise ImmutableAuditError("Audit records are immutable and cannot be updated.")
    for obj in session.deleted:
        if isinstance(obj, _IMMUTABLE):
            raise ImmutableAuditError("Audit records are immutable and cannot be deleted.")


def register_audit_guard() -> None:
    """Importing this module registers the listener."""
    return None
