"""Core deterministic scoring engines.

All functions return a ``ScoreResult`` containing the numeric score (0-100),
a discrete band, and the weighted factors that produced it. This makes every
number traceable back to its inputs — a hard requirement for operational
decision support.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.models import enums


@dataclass
class ScoreResult:
    score: float
    band: str
    factors: dict[str, float] = field(default_factory=dict)
    explanation: str = ""

    def rounded(self) -> float:
        return round(self.score, 1)


def _clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


# Relative danger weighting of incident types (0-1 multiplier on hazard).
INCIDENT_TYPE_WEIGHT: dict[enums.IncidentType, float] = {
    enums.IncidentType.HURRICANE: 1.0,
    enums.IncidentType.EARTHQUAKE: 0.98,
    enums.IncidentType.FLOOD: 0.85,
    enums.IncidentType.WILDFIRE: 0.88,
    enums.IncidentType.DISEASE_OUTBREAK: 0.9,
    enums.IncidentType.INDUSTRIAL_ACCIDENT: 0.7,
    enums.IncidentType.INFRASTRUCTURE_FAILURE: 0.6,
    enums.IncidentType.SEVERE_STORM: 0.75,
}

STATUS_MULTIPLIER: dict[enums.IncidentStatus, float] = {
    enums.IncidentStatus.MONITORING: 0.55,
    enums.IncidentStatus.ACTIVE: 1.0,
    enums.IncidentStatus.ESCALATING: 1.2,
    enums.IncidentStatus.CONTAINED: 0.5,
    enums.IncidentStatus.RESOLVED: 0.1,
}


def band_from_score(score: float) -> str:
    if score >= 85:
        return "critical"
    if score >= 70:
        return "severe"
    if score >= 50:
        return "high"
    if score >= 30:
        return "moderate"
    return "low"


def incident_severity(
    *,
    base_severity: int,
    incident_type: enums.IncidentType,
    status: enums.IncidentStatus,
    population_impacted: int,
    radius_km: float,
) -> ScoreResult:
    """Incident Severity Score (0-100).

    Blends operator-assigned base severity, hazard type, lifecycle status,
    impacted population (log-scaled) and geographic footprint.
    """
    type_weight = INCIDENT_TYPE_WEIGHT.get(incident_type, 0.7)
    status_mult = STATUS_MULTIPLIER.get(status, 1.0)

    # Base severity contributes up to 45 pts.
    severity_component = (base_severity / 5.0) * 45.0
    # Population (log scale) contributes up to 30 pts (saturates ~500k).
    from math import log10

    pop = max(0, population_impacted)
    population_component = _clamp((log10(pop + 1) / log10(500_000)) * 30.0, 0, 30)
    # Footprint contributes up to 25 pts (saturates ~50km radius).
    footprint_component = _clamp((radius_km / 50.0) * 25.0, 0, 25)

    raw = (severity_component + population_component + footprint_component) * type_weight
    score = _clamp(raw * status_mult)
    factors = {
        "base_severity": round(severity_component, 1),
        "population_impact": round(population_component, 1),
        "footprint": round(footprint_component, 1),
        "type_weight": type_weight,
        "status_multiplier": status_mult,
    }
    explanation = (
        f"Base severity {base_severity}/5 ({severity_component:.0f} pts), "
        f"{population_impacted:,} people impacted ({population_component:.0f} pts), "
        f"{radius_km:.1f}km footprint ({footprint_component:.0f} pts), "
        f"scaled by {incident_type.value} hazard weight {type_weight:.2f} and "
        f"{status.value} status multiplier {status_mult:.2f}."
    )
    return ScoreResult(score, band_from_score(score), factors, explanation)


def hospital_stress(
    *,
    total_beds: int,
    occupied_beds: int,
    icu_beds: int,
    icu_occupied: int,
    er_capacity: int,
    er_patients: int,
    staff_on_duty: int,
    staff_required: int,
    ventilators_total: int,
    ventilators_in_use: int,
) -> ScoreResult:
    """Hospital Stress Score (0-100). Higher = more strained."""

    def ratio(num: int, den: int) -> float:
        return (num / den) if den > 0 else 0.0

    bed_load = ratio(occupied_beds, total_beds)
    icu_load = ratio(icu_occupied, icu_beds)
    er_load = ratio(er_patients, er_capacity)
    vent_load = ratio(ventilators_in_use, ventilators_total)
    # Staffing gap: required vs on-duty.
    staffing_gap = _clamp(
        (1 - ratio(staff_on_duty, staff_required)) if staff_required else 0.0, 0, 1
    )

    # Weighted blend; ICU and ER weigh heaviest in surge conditions.
    score = _clamp(
        (icu_load * 32) + (er_load * 28) + (bed_load * 18) + (vent_load * 12) + (staffing_gap * 10)
    )
    factors = {
        "icu_load_pct": round(icu_load * 100, 1),
        "er_load_pct": round(er_load * 100, 1),
        "bed_load_pct": round(bed_load * 100, 1),
        "ventilator_load_pct": round(vent_load * 100, 1),
        "staffing_gap_pct": round(staffing_gap * 100, 1),
    }
    explanation = (
        f"ICU at {icu_load * 100:.0f}%, ER at {er_load * 100:.0f}%, "
        f"beds at {bed_load * 100:.0f}%, ventilators at {vent_load * 100:.0f}%, "
        f"staffing gap {staffing_gap * 100:.0f}%."
    )
    return ScoreResult(score, band_from_score(score), factors, explanation)


def hospital_status_from_score(score: float, accepts_diversions: bool) -> enums.HospitalStatus:
    if score >= 88 or not accepts_diversions:
        return enums.HospitalStatus.DIVERSION if score >= 88 else enums.HospitalStatus.CRITICAL
    if score >= 75:
        return enums.HospitalStatus.CRITICAL
    if score >= 55:
        return enums.HospitalStatus.STRAINED
    if score >= 35:
        return enums.HospitalStatus.ELEVATED
    return enums.HospitalStatus.NORMAL


def shelter_utilization(
    *,
    capacity: int,
    occupancy: int,
    food_supply_days: float,
    water_supply_days: float,
) -> ScoreResult:
    """Shelter Utilization / Strain Score (0-100)."""
    occ = (occupancy / capacity) if capacity > 0 else 0.0
    # Supply scarcity raises strain when below 3 days buffer.
    food_scarcity = _clamp((3.0 - min(food_supply_days, 3.0)) / 3.0, 0, 1)
    water_scarcity = _clamp((3.0 - min(water_supply_days, 3.0)) / 3.0, 0, 1)
    score = _clamp((occ * 70) + (food_scarcity * 15) + (water_scarcity * 15))
    factors = {
        "occupancy_pct": round(occ * 100, 1),
        "food_scarcity_pct": round(food_scarcity * 100, 1),
        "water_scarcity_pct": round(water_scarcity * 100, 1),
    }
    explanation = (
        f"Occupancy {occ * 100:.0f}% of capacity; "
        f"food buffer {food_supply_days:.1f}d, water buffer {water_supply_days:.1f}d."
    )
    return ScoreResult(score, band_from_score(score), factors, explanation)


def shelter_status_from(occupancy: int, capacity: int) -> enums.ShelterStatus:
    if capacity <= 0:
        return enums.ShelterStatus.CLOSED
    occ = occupancy / capacity
    if occ >= 1.0:
        return enums.ShelterStatus.FULL
    if occ >= 0.85:
        return enums.ShelterStatus.NEAR_CAPACITY
    return enums.ShelterStatus.OPEN


def resource_readiness(
    *,
    total: int,
    available: int,
    assigned: int,
    avg_readiness: float,
) -> ScoreResult:
    """Resource Readiness Score (0-100). Higher = better posture."""
    availability = (available / total) if total > 0 else 0.0
    utilization = (assigned / total) if total > 0 else 0.0
    # Healthy posture: high readiness + adequate availability, but very low
    # availability under heavy assignment indicates depletion risk.
    score = _clamp(
        (availability * 45) + (avg_readiness * 0.4) + ((1 - abs(0.4 - utilization)) * 15)
    )
    factors = {
        "availability_pct": round(availability * 100, 1),
        "utilization_pct": round(utilization * 100, 1),
        "avg_readiness_pct": round(avg_readiness, 1),
    }
    explanation = (
        f"{available}/{total} units available ({availability * 100:.0f}%), "
        f"{utilization * 100:.0f}% assigned, mean readiness {avg_readiness:.0f}%."
    )
    return ScoreResult(score, band_from_score(score), factors, explanation)


def overall_health(
    *,
    incident_severity_score: float,
    hospital_stress_score: float,
    shelter_strain_score: float,
    resource_readiness_score: float,
    open_critical_alerts: int,
) -> ScoreResult:
    """Overall Emergency Health Score (0-100). Higher = healthier system.

    Inverts strain-style metrics so all components point the same direction,
    then applies a penalty for unresolved critical alerts.
    """
    inv_incident = 100 - incident_severity_score
    inv_hospital = 100 - hospital_stress_score
    inv_shelter = 100 - shelter_strain_score
    readiness = resource_readiness_score

    weighted = inv_incident * 0.30 + inv_hospital * 0.25 + inv_shelter * 0.20 + readiness * 0.25
    alert_penalty = min(20.0, open_critical_alerts * 2.5)
    score = _clamp(weighted - alert_penalty)

    if score >= 80:
        status = "stable"
    elif score >= 60:
        status = "watch"
    elif score >= 40:
        status = "elevated"
    elif score >= 25:
        status = "severe"
    else:
        status = "critical"

    factors = {
        "incident_health": round(inv_incident, 1),
        "hospital_health": round(inv_hospital, 1),
        "shelter_health": round(inv_shelter, 1),
        "resource_readiness": round(readiness, 1),
        "critical_alert_penalty": round(alert_penalty, 1),
    }
    explanation = (
        f"Composite of incident ({inv_incident:.0f}), hospital ({inv_hospital:.0f}), "
        f"shelter ({inv_shelter:.0f}) health and resource readiness ({readiness:.0f}), "
        f"less {alert_penalty:.0f} pt penalty for {open_critical_alerts} critical alert(s)."
    )
    return ScoreResult(score, status, factors, explanation)
