"""A computed, in-memory operational snapshot shared across engines.

The analytics service builds this from the database once per request; the risk,
recommendation, briefing and copilot engines all read from it so that every
derived artifact is consistent with the same point-in-time picture.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class IncidentSnapshot:
    id: int
    name: str
    incident_type: str
    status: str
    severity_score: float
    population_impacted: int
    region: str | None


@dataclass
class HospitalRiskItem:
    id: int
    name: str
    region: str | None
    stress_score: float
    status: str
    icu_occupancy_pct: float


@dataclass
class ShelterRiskItem:
    id: int
    name: str
    region: str | None
    utilization_score: float
    occupancy_pct: float
    food_supply_days: float


@dataclass
class OperationalSnapshot:
    # Incidents
    incidents: list[IncidentSnapshot] = field(default_factory=list)
    active_incidents: int = 0
    escalating_incidents: int = 0
    incident_severity_score: float = 0.0  # max active severity
    avg_incident_severity: float = 0.0
    total_population_impacted: int = 0

    # Hospitals
    hospital_count: int = 0
    hospitals_at_risk: int = 0
    avg_hospital_stress: float = 0.0
    hospital_capacity_pct: float = 0.0  # overall bed occupancy
    icu_occupancy_pct: float = 0.0
    top_stressed_hospitals: list[HospitalRiskItem] = field(default_factory=list)

    # Shelters
    shelter_count: int = 0
    shelters_overcrowded: int = 0
    shelter_utilization_pct: float = 0.0
    avg_shelter_strain: float = 0.0
    shelters_low_supply: int = 0
    top_strained_shelters: list[ShelterRiskItem] = field(default_factory=list)

    # Resources
    resource_total: int = 0
    resource_available: int = 0
    resource_assigned: int = 0
    resource_availability_pct: float = 0.0
    resource_readiness_pct: float = 0.0
    resource_readiness_score: float = 0.0
    resource_by_type: dict[str, dict] = field(default_factory=dict)
    depleted_resource_types: list[str] = field(default_factory=list)

    # Utilities
    utility_outages_active: int = 0
    customers_without_service: int = 0
    utility_by_type: dict[str, int] = field(default_factory=dict)

    # Alerts
    open_alerts: int = 0
    critical_alerts: int = 0
    alerts_by_category: dict[str, int] = field(default_factory=dict)

    # Composite
    overall_health_score: float = 0.0
    health_status: str = "unknown"

    # Regions in play
    regions: list[str] = field(default_factory=list)
