"""Unit tests for the deterministic scoring engine.

These functions are the analytical core of the platform: every score must be
bounded, monotonic in the obvious direction, and reproducible.
"""

from __future__ import annotations

from app.engines import scoring
from app.models import enums


def test_band_thresholds():
    assert scoring.band_from_score(95) == "critical"
    assert scoring.band_from_score(72) == "severe"
    assert scoring.band_from_score(55) == "high"
    assert scoring.band_from_score(31) == "moderate"
    assert scoring.band_from_score(10) == "low"


def test_incident_severity_is_bounded():
    result = scoring.incident_severity(
        base_severity=5,
        incident_type=enums.IncidentType.HURRICANE,
        status=enums.IncidentStatus.ESCALATING,
        population_impacted=400_000,
        radius_km=45,
    )
    assert 0.0 <= result.score <= 100.0
    assert result.band in {"low", "moderate", "high", "severe", "critical"}
    assert result.explanation


def test_incident_severity_monotonic_in_population():
    low = scoring.incident_severity(
        base_severity=3,
        incident_type=enums.IncidentType.FLOOD,
        status=enums.IncidentStatus.ACTIVE,
        population_impacted=1_000,
        radius_km=10,
    )
    high = scoring.incident_severity(
        base_severity=3,
        incident_type=enums.IncidentType.FLOOD,
        status=enums.IncidentStatus.ACTIVE,
        population_impacted=250_000,
        radius_km=10,
    )
    assert high.score > low.score


def test_hospital_stress_high_when_saturated():
    result = scoring.hospital_stress(
        total_beds=200,
        occupied_beds=198,
        icu_beds=40,
        icu_occupied=40,
        er_capacity=50,
        er_patients=60,
        staff_on_duty=20,
        staff_required=60,
        ventilators_total=30,
        ventilators_in_use=29,
    )
    assert result.score >= 70


def test_shelter_utilization_bounds():
    result = scoring.shelter_utilization(
        capacity=0, occupancy=0, food_supply_days=0, water_supply_days=0
    )
    assert 0.0 <= result.score <= 100.0


def test_overall_health_penalizes_critical_alerts():
    base = {
        "incident_severity_score": 40,
        "hospital_stress_score": 40,
        "shelter_strain_score": 40,
        "resource_readiness_score": 70,
    }
    calm = scoring.overall_health(open_critical_alerts=0, **base)
    busy = scoring.overall_health(open_critical_alerts=8, **base)
    assert calm.score > busy.score
