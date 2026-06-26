"""Alert generation and lifecycle service."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Alert, Hospital, Incident, Resource, Shelter, UtilityOutage, enums


def _exists_open(db: Session, category: enums.AlertCategory, **kwargs) -> bool:
    stmt = select(Alert.id).where(
        Alert.category == category, Alert.status != enums.AlertStatus.RESOLVED
    )
    for key, value in kwargs.items():
        stmt = stmt.where(getattr(Alert, key) == value)
    return db.scalar(stmt) is not None


def evaluate_and_generate(db: Session, org_id: int | None = None) -> list[Alert]:
    """Scan operational entities and raise alerts for breached thresholds.

    Idempotent: will not duplicate an open alert for the same subject. Reads are
    already tenant-scoped via the session; new alerts are stamped with ``org_id``.
    """
    now = datetime.now(UTC)
    created: list[Alert] = []

    # Hospitals over stress threshold.
    for h in db.scalars(select(Hospital).where(Hospital.stress_score >= 75)).all():
        if _exists_open(db, enums.AlertCategory.HOSPITAL_OVERLOAD, hospital_id=h.id):
            continue
        sev = (
            enums.AlertSeverity.EMERGENCY if h.stress_score >= 88 else enums.AlertSeverity.CRITICAL
        )
        created.append(
            Alert(
                organization_id=org_id,
                category=enums.AlertCategory.HOSPITAL_OVERLOAD,
                severity=sev,
                title=f"Hospital overload: {h.name}",
                message=f"{h.name} stress score {h.stress_score:.0f}/100 ({h.status.value}).",
                region=h.region,
                source="threshold_engine",
                hospital_id=h.id,
                triggered_at=now,
            )
        )

    # Shelters at/over capacity.
    for sh in db.scalars(select(Shelter)).all():
        if sh.capacity and sh.occupancy / sh.capacity >= 0.95:
            if _exists_open(db, enums.AlertCategory.SHELTER_CAPACITY, shelter_id=sh.id):
                continue
            created.append(
                Alert(
                    organization_id=org_id,
                    category=enums.AlertCategory.SHELTER_CAPACITY,
                    severity=enums.AlertSeverity.CRITICAL,
                    title=f"Shelter capacity exceeded: {sh.name}",
                    message=f"{sh.name} at {sh.occupancy}/{sh.capacity} occupants.",
                    region=sh.region,
                    source="threshold_engine",
                    shelter_id=sh.id,
                    triggered_at=now,
                )
            )

    # Escalating incidents.
    for inc in db.scalars(
        select(Incident).where(Incident.status == enums.IncidentStatus.ESCALATING)
    ).all():
        if _exists_open(db, enums.AlertCategory.INCIDENT_ESCALATION, incident_id=inc.id):
            continue
        created.append(
            Alert(
                organization_id=org_id,
                category=enums.AlertCategory.INCIDENT_ESCALATION,
                severity=enums.AlertSeverity.CRITICAL,
                title=f"Incident escalating: {inc.name}",
                message=f"{inc.name} severity {inc.severity_score:.0f}/100, "
                f"{inc.population_impacted:,} impacted.",
                region=inc.region,
                source="threshold_engine",
                incident_id=inc.id,
                triggered_at=now,
            )
        )

    # Resource shortages by type (availability < 15%).
    counts: dict[str, dict[str, int]] = {}
    for r in db.scalars(select(Resource)).all():
        b = counts.setdefault(r.resource_type.value, {"total": 0, "available": 0})
        b["total"] += 1
        if r.status == enums.ResourceStatus.AVAILABLE:
            b["available"] += 1
    for rtype, b in counts.items():
        if b["total"] and b["available"] / b["total"] < 0.15:
            if _exists_open(db, enums.AlertCategory.RESOURCE_SHORTAGE, source=f"resource:{rtype}"):
                continue
            created.append(
                Alert(
                    organization_id=org_id,
                    category=enums.AlertCategory.RESOURCE_SHORTAGE,
                    severity=enums.AlertSeverity.WARNING,
                    title=f"Resource shortage: {rtype.replace('_', ' ')}",
                    message=f"Only {b['available']}/{b['total']} {rtype} units available.",
                    source=f"resource:{rtype}",
                    triggered_at=now,
                )
            )

    # Large utility outages.
    for o in db.scalars(
        select(UtilityOutage).where(
            UtilityOutage.status != enums.UtilityOutageStatus.RESTORED,
            UtilityOutage.customers_affected >= 25000,
        )
    ).all():
        if _exists_open(db, enums.AlertCategory.UTILITY_FAILURE, source=f"outage:{o.id}"):
            continue
        created.append(
            Alert(
                organization_id=org_id,
                category=enums.AlertCategory.UTILITY_FAILURE,
                severity=enums.AlertSeverity.CRITICAL
                if o.customers_affected >= 100000
                else enums.AlertSeverity.WARNING,
                title=f"{o.utility_type.value.title()} outage",
                message=f"{o.customers_affected:,} customers affected in {o.region or 'region'}.",
                region=o.region,
                source=f"outage:{o.id}",
                incident_id=o.incident_id,
                triggered_at=now,
            )
        )

    for alert in created:
        db.add(alert)
    if created:
        db.commit()
        for alert in created:
            db.refresh(alert)
    return created


def acknowledge(db: Session, alert: Alert, user_id: int, notes: str | None) -> Alert:
    alert.status = enums.AlertStatus.ACKNOWLEDGED
    alert.acknowledged_by_id = user_id
    alert.acknowledged_at = datetime.now(UTC)
    actions = list(alert.response_actions or [])
    actions.append({"action": "acknowledged", "user_id": user_id, "notes": notes, "at": _now_iso()})
    alert.response_actions = actions
    db.commit()
    db.refresh(alert)
    return alert


def resolve(db: Session, alert: Alert, user_id: int, notes: str | None) -> Alert:
    alert.status = enums.AlertStatus.RESOLVED
    alert.resolved_at = datetime.now(UTC)
    actions = list(alert.response_actions or [])
    actions.append({"action": "resolved", "user_id": user_id, "notes": notes, "at": _now_iso()})
    alert.response_actions = actions
    db.commit()
    db.refresh(alert)
    return alert


def add_action(db: Session, alert: Alert, user_id: int, action: str, notes: str | None) -> Alert:
    actions = list(alert.response_actions or [])
    actions.append({"action": action, "user_id": user_id, "notes": notes, "at": _now_iso()})
    alert.response_actions = actions
    db.commit()
    db.refresh(alert)
    return alert


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()
