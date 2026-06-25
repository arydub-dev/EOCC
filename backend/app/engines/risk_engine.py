"""Deterministic risk intelligence engine.

Produces explainable risk assessments across the five doctrinal categories.
Each assessment is a pure function of the operational snapshot.
"""
from __future__ import annotations

from dataclasses import dataclass

from app.engines.scoring import _clamp
from app.engines.snapshot import OperationalSnapshot
from app.models import enums


@dataclass
class RiskResult:
    category: enums.RiskCategory
    severity: enums.RiskSeverity
    score: float
    title: str
    explanation: str
    recommendations: list[str]
    factors: dict


def _severity_from_score(score: float) -> enums.RiskSeverity:
    if score >= 85:
        return enums.RiskSeverity.CRITICAL
    if score >= 70:
        return enums.RiskSeverity.SEVERE
    if score >= 50:
        return enums.RiskSeverity.HIGH
    if score >= 30:
        return enums.RiskSeverity.MODERATE
    return enums.RiskSeverity.LOW


def _population_risk(s: OperationalSnapshot) -> RiskResult:
    from math import log10

    pop_factor = _clamp((log10(s.total_population_impacted + 1) / log10(1_000_000)) * 60, 0, 60)
    escalation_factor = _clamp(s.escalating_incidents * 8, 0, 25)
    shelter_factor = _clamp(s.shelters_overcrowded * 3, 0, 15)
    score = _clamp(pop_factor + escalation_factor + shelter_factor)
    recs = []
    if s.shelters_overcrowded:
        recs.append(f"Open overflow capacity for {s.shelters_overcrowded} overcrowded shelter(s).")
    if s.escalating_incidents:
        recs.append("Issue evacuation guidance for escalating incident zones.")
    recs.append("Pre-position mass-care supplies near highest-population impact areas.")
    return RiskResult(
        enums.RiskCategory.POPULATION,
        _severity_from_score(score),
        round(score, 1),
        "Population Exposure Risk",
        f"{s.total_population_impacted:,} people across active incidents, "
        f"{s.escalating_incidents} escalating event(s), {s.shelters_overcrowded} overcrowded shelter(s).",
        recs,
        {"population": pop_factor, "escalation": escalation_factor, "shelter": shelter_factor},
    )


def _infrastructure_risk(s: OperationalSnapshot) -> RiskResult:
    from math import log10

    outage_factor = _clamp((log10(s.customers_without_service + 1) / log10(500_000)) * 55, 0, 55)
    active_factor = _clamp(s.utility_outages_active * 1.5, 0, 30)
    score = _clamp(outage_factor + active_factor)
    recs = ["Prioritize restoration for outages serving hospitals and shelters."]
    if s.utility_by_type.get("power", 0):
        recs.append(f"Deploy mobile generators to {s.utility_by_type.get('power')} power-outage zone(s).")
    if s.customers_without_service > 50_000:
        recs.append("Coordinate with utility partners for mutual-aid crews.")
    return RiskResult(
        enums.RiskCategory.INFRASTRUCTURE,
        _severity_from_score(score),
        round(score, 1),
        "Infrastructure & Lifeline Risk",
        f"{s.utility_outages_active} active outage(s) affecting {s.customers_without_service:,} customers.",
        recs,
        {"customers_affected": outage_factor, "active_outages": active_factor},
    )


def _healthcare_risk(s: OperationalSnapshot) -> RiskResult:
    stress_factor = _clamp(s.avg_hospital_stress * 0.7, 0, 60)
    at_risk_factor = _clamp(s.hospitals_at_risk * 6, 0, 25)
    icu_factor = _clamp((s.icu_occupancy_pct - 70) * 0.5, 0, 15) if s.icu_occupancy_pct > 70 else 0
    score = _clamp(stress_factor + at_risk_factor + icu_factor)
    recs = []
    if s.hospitals_at_risk:
        recs.append(f"Activate load-balancing / diversion for {s.hospitals_at_risk} at-risk hospital(s).")
    if s.icu_occupancy_pct > 80:
        recs.append("Stand up surge ICU capacity and request regional mutual aid.")
    recs.append("Deploy additional medical teams to highest-stress facilities.")
    return RiskResult(
        enums.RiskCategory.HEALTHCARE,
        _severity_from_score(score),
        round(score, 1),
        "Healthcare System Risk",
        f"Mean hospital stress {s.avg_hospital_stress:.0f}/100, {s.hospitals_at_risk} facility(ies) at risk, "
        f"system ICU occupancy {s.icu_occupancy_pct:.0f}%.",
        recs,
        {"avg_stress": stress_factor, "at_risk": at_risk_factor, "icu": icu_factor},
    )


def _resource_risk(s: OperationalSnapshot) -> RiskResult:
    scarcity = _clamp((100 - s.resource_availability_pct) * 0.6, 0, 50)
    readiness_gap = _clamp((100 - s.resource_readiness_pct) * 0.3, 0, 25)
    depletion = _clamp(len(s.depleted_resource_types) * 8, 0, 25)
    score = _clamp(scarcity + readiness_gap + depletion)
    recs = []
    if s.depleted_resource_types:
        recs.append(
            "Resupply depleted categories: " + ", ".join(s.depleted_resource_types) + "."
        )
    if s.resource_availability_pct < 40:
        recs.append("Request mutual-aid resources from neighboring jurisdictions.")
    recs.append("Rebalance idle assets toward highest-severity incidents.")
    return RiskResult(
        enums.RiskCategory.RESOURCE,
        _severity_from_score(score),
        round(score, 1),
        "Resource Adequacy Risk",
        f"{s.resource_availability_pct:.0f}% of assets available, mean readiness {s.resource_readiness_pct:.0f}%, "
        f"{len(s.depleted_resource_types)} category(ies) depleted.",
        recs,
        {"scarcity": scarcity, "readiness_gap": readiness_gap, "depletion": depletion},
    )


def _environmental_risk(s: OperationalSnapshot) -> RiskResult:
    sev_factor = _clamp(s.incident_severity_score * 0.6, 0, 60)
    escalation = _clamp(s.escalating_incidents * 6, 0, 25)
    breadth = _clamp(s.active_incidents * 2, 0, 15)
    score = _clamp(sev_factor + escalation + breadth)
    recs = [
        "Maintain continuous monitoring of weather and hazard feeds.",
        "Update forecast-based pre-positioning for highest-severity hazards.",
    ]
    if s.escalating_incidents:
        recs.insert(0, "Escalate incident command posture for worsening events.")
    return RiskResult(
        enums.RiskCategory.ENVIRONMENTAL,
        _severity_from_score(score),
        round(score, 1),
        "Environmental & Hazard Risk",
        f"Peak incident severity {s.incident_severity_score:.0f}/100 across {s.active_incidents} active "
        f"incident(s), {s.escalating_incidents} escalating.",
        recs,
        {"peak_severity": sev_factor, "escalation": escalation, "breadth": breadth},
    )


def assess_all(s: OperationalSnapshot) -> list[RiskResult]:
    return [
        _population_risk(s),
        _infrastructure_risk(s),
        _healthcare_risk(s),
        _resource_risk(s),
        _environmental_risk(s),
    ]
