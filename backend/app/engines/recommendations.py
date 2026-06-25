"""Recommended actions and situation-report generation.

Translates the operational snapshot into a prioritized, explainable action
list and a narrative situation report (SITREP).
"""
from __future__ import annotations

from dataclasses import dataclass

from app.engines.snapshot import OperationalSnapshot


@dataclass
class Action:
    priority: int
    title: str
    rationale: str
    category: str
    impact: str
    confidence: float


def recommend_actions(s: OperationalSnapshot) -> list[Action]:
    actions: list[Action] = []

    if s.hospitals_at_risk > 0:
        actions.append(
            Action(
                0,
                f"Load-balance {s.hospitals_at_risk} at-risk hospital(s)",
                f"Mean hospital stress is {s.avg_hospital_stress:.0f}/100 with ICU occupancy at "
                f"{s.icu_occupancy_pct:.0f}%. Diverting incoming patients prevents capacity collapse.",
                "healthcare",
                "Prevents care degradation for critical patients",
                0.9,
            )
        )

    if s.shelters_overcrowded > 0:
        actions.append(
            Action(
                0,
                f"Relieve {s.shelters_overcrowded} overcrowded shelter(s)",
                f"Shelter network is at {s.shelter_utilization_pct:.0f}% utilization. Opening overflow sites "
                "reduces displacement risk and supply strain.",
                "shelter",
                "Restores safe occupancy levels",
                0.85,
            )
        )

    if s.depleted_resource_types:
        actions.append(
            Action(
                0,
                "Resupply depleted resource categories",
                "Depleted: " + ", ".join(s.depleted_resource_types) + f". Overall availability is "
                f"{s.resource_availability_pct:.0f}%.",
                "resource",
                "Restores response capability",
                0.8,
            )
        )

    if s.escalating_incidents > 0:
        actions.append(
            Action(
                0,
                f"Escalate command posture for {s.escalating_incidents} worsening incident(s)",
                f"Peak incident severity is {s.incident_severity_score:.0f}/100. Escalating events require "
                "expanded incident command and pre-positioned assets.",
                "incident",
                "Reduces response latency as conditions worsen",
                0.88,
            )
        )

    if s.customers_without_service > 50_000:
        actions.append(
            Action(
                0,
                "Coordinate utility restoration for lifeline facilities",
                f"{s.customers_without_service:,} customers without service across "
                f"{s.utility_outages_active} outage(s). Prioritize hospitals and shelters.",
                "infrastructure",
                "Protects critical-facility continuity",
                0.82,
            )
        )

    if s.critical_alerts > 0:
        actions.append(
            Action(
                0,
                f"Triage {s.critical_alerts} critical alert(s)",
                "Unresolved critical alerts indicate active threats to life-safety or capacity.",
                "alerts",
                "Ensures fastest response to top threats",
                0.95,
            )
        )

    if not actions:
        actions.append(
            Action(
                0,
                "Maintain monitoring posture",
                f"System health is {s.overall_health_score:.0f}/100 ({s.health_status}). No critical "
                "thresholds breached.",
                "monitoring",
                "Sustains situational awareness",
                0.7,
            )
        )

    # Sort by confidence-weighted impact, assign 1-indexed priority.
    actions.sort(key=lambda a: a.confidence, reverse=True)
    for idx, action in enumerate(actions, start=1):
        action.priority = idx
    return actions


def situation_report(s: OperationalSnapshot) -> str:
    """Generate a narrative SITREP grounded in the snapshot."""
    lines: list[str] = []
    lines.append(
        f"OPERATIONAL STATUS: System health {s.overall_health_score:.0f}/100 ({s.health_status.upper()})."
    )
    lines.append(
        f"INCIDENTS: {s.active_incidents} active ({s.escalating_incidents} escalating); peak severity "
        f"{s.incident_severity_score:.0f}/100 impacting an estimated {s.total_population_impacted:,} people."
    )
    lines.append(
        f"HEALTHCARE: {s.hospital_count} hospitals tracked, {s.hospitals_at_risk} at risk; system bed "
        f"occupancy {s.hospital_capacity_pct:.0f}%, ICU occupancy {s.icu_occupancy_pct:.0f}%."
    )
    lines.append(
        f"MASS CARE: {s.shelter_count} shelters at {s.shelter_utilization_pct:.0f}% utilization; "
        f"{s.shelters_overcrowded} overcrowded, {s.shelters_low_supply} low on supplies."
    )
    lines.append(
        f"RESOURCES: {s.resource_available}/{s.resource_total} assets available "
        f"({s.resource_availability_pct:.0f}%), mean readiness {s.resource_readiness_pct:.0f}%."
    )
    lines.append(
        f"LIFELINES: {s.utility_outages_active} active utility outage(s) affecting "
        f"{s.customers_without_service:,} customers."
    )
    lines.append(
        f"ALERTS: {s.open_alerts} open ({s.critical_alerts} critical) requiring command attention."
    )
    return "\n".join(lines)
