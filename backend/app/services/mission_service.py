"""Mission Control aggregation service."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.engines import recommendations
from app.engines.scoring import overall_health
from app.engines.snapshot import OperationalSnapshot
from app.models import Alert, enums
from app.schemas.mission import (
    HealthBreakdown,
    MetricCard,
    MissionControlSummary,
    RecommendedAction,
)
from app.schemas.ops import AlertOut


def _metric(key, label, value, unit=None, status="normal", detail=None, trend=None) -> MetricCard:
    return MetricCard(
        key=key,
        label=label,
        value=round(value, 1),
        unit=unit,
        status=status,
        detail=detail,
        trend=trend,
    )


def _status_for(value: float, watch: float, warn: float, crit: float, invert: bool = False) -> str:
    v = value
    if invert:
        if v <= crit:
            return "critical"
        if v <= warn:
            return "warning"
        if v <= watch:
            return "watch"
        return "normal"
    if v >= crit:
        return "critical"
    if v >= warn:
        return "warning"
    if v >= watch:
        return "watch"
    return "normal"


def build_mission_control(db: Session, snap: OperationalSnapshot) -> MissionControlSummary:
    metrics = [
        _metric(
            "health",
            "System Health",
            snap.overall_health_score,
            "/100",
            _status_for(snap.overall_health_score, 80, 60, 40, invert=True),
            f"Composite operational health ({snap.health_status})",
        ),
        _metric(
            "severity",
            "Incident Severity",
            snap.incident_severity_score,
            "/100",
            _status_for(snap.incident_severity_score, 30, 50, 70),
            "Peak active incident severity",
        ),
        _metric(
            "population",
            "Population Impacted",
            snap.total_population_impacted,
            "people",
            _status_for(snap.total_population_impacted, 10000, 100000, 500000),
            "Across all active incidents",
        ),
        _metric(
            "active_incidents",
            "Active Incidents",
            snap.active_incidents,
            None,
            _status_for(snap.active_incidents, 5, 15, 30),
            f"{snap.escalating_incidents} escalating",
        ),
        _metric(
            "hospital_capacity",
            "Hospital Capacity",
            snap.hospital_capacity_pct,
            "%",
            _status_for(snap.hospital_capacity_pct, 70, 85, 95),
            f"{snap.hospitals_at_risk} at risk",
        ),
        _metric(
            "shelter_util",
            "Shelter Utilization",
            snap.shelter_utilization_pct,
            "%",
            _status_for(snap.shelter_utilization_pct, 70, 85, 95),
            f"{snap.shelters_overcrowded} overcrowded",
        ),
        _metric(
            "resource_avail",
            "Resource Availability",
            snap.resource_availability_pct,
            "%",
            _status_for(snap.resource_availability_pct, 50, 30, 15, invert=True),
            f"{snap.resource_available}/{snap.resource_total} available",
        ),
        _metric(
            "alerts",
            "Open Alerts",
            snap.open_alerts,
            None,
            _status_for(snap.critical_alerts, 1, 3, 6),
            f"{snap.critical_alerts} critical",
        ),
    ]

    critical = list(
        db.scalars(
            select(Alert)
            .where(
                Alert.status != enums.AlertStatus.RESOLVED,
                Alert.severity.in_([enums.AlertSeverity.CRITICAL, enums.AlertSeverity.EMERGENCY]),
            )
            .order_by(Alert.triggered_at.desc())
            .limit(8)
        ).all()
    )

    actions = [
        RecommendedAction(
            priority=a.priority,
            title=a.title,
            rationale=a.rationale,
            category=a.category,
            impact=a.impact,
            confidence=a.confidence,
        )
        for a in recommendations.recommend_actions(snap)
    ]

    return MissionControlSummary(
        overall_health_score=snap.overall_health_score,
        health_status=snap.health_status,
        incident_severity_score=snap.incident_severity_score,
        population_impacted=snap.total_population_impacted,
        active_incidents=snap.active_incidents,
        escalating_incidents=snap.escalating_incidents,
        hospital_capacity_pct=snap.hospital_capacity_pct,
        hospitals_at_risk=snap.hospitals_at_risk,
        shelter_utilization_pct=snap.shelter_utilization_pct,
        shelters_overcrowded=snap.shelters_overcrowded,
        resource_availability_pct=snap.resource_availability_pct,
        resource_readiness_pct=snap.resource_readiness_pct,
        open_alerts=snap.open_alerts,
        critical_alerts=snap.critical_alerts,
        metrics=metrics,
        critical_alerts_list=[AlertOut.model_validate(a) for a in critical],
        recommended_actions=actions,
        situation_report=recommendations.situation_report(snap),
    )


def build_health_breakdown(snap: OperationalSnapshot) -> HealthBreakdown:
    result = overall_health(
        incident_severity_score=snap.incident_severity_score,
        hospital_stress_score=snap.avg_hospital_stress,
        shelter_strain_score=snap.avg_shelter_strain,
        resource_readiness_score=snap.resource_readiness_score,
        open_critical_alerts=snap.critical_alerts,
    )
    return HealthBreakdown(
        overall_health_score=result.rounded(),
        health_status=result.band,
        components=result.factors,
        explanation=result.explanation,
    )
