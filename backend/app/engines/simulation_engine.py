"""Deterministic simulation engine for what-if operational planning.

Each scenario consumes the current operational snapshot plus user parameters
and returns projected impacts and mitigation recommendations. Results are
fully reproducible.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.engines.scoring import _clamp
from app.engines.snapshot import OperationalSnapshot
from app.models import enums


@dataclass
class SimulationResult:
    results: dict = field(default_factory=dict)
    recommendations: list[str] = field(default_factory=list)
    operational_risk: float = 0.0


def _risk_band(score: float) -> str:
    if score >= 80:
        return "critical"
    if score >= 60:
        return "severe"
    if score >= 40:
        return "high"
    if score >= 20:
        return "moderate"
    return "low"


def _hurricane_path(s: OperationalSnapshot, p: dict) -> SimulationResult:
    category = int(p.get("category", 3))
    shift_km = float(p.get("track_shift_km", 40))
    population_density = float(p.get("population_density", 1500))  # per km^2

    swath_width = 60 + category * 25  # km
    affected_area = swath_width * max(shift_km, 50)
    population_affected = int(affected_area * population_density * 0.12)

    evac_buses = max(1, population_affected // 4000)
    shelters_needed = max(1, population_affected // 1200)
    medical_teams = max(2, population_affected // 25000)

    risk = _clamp(category * 14 + (shift_km / 5) + s.incident_severity_score * 0.2)
    return SimulationResult(
        results={
            "population_affected": population_affected,
            "projected_evacuations": int(population_affected * 0.45),
            "additional_resources_required": {
                "evacuation_buses": evac_buses,
                "medical_teams": medical_teams,
                "generators": max(5, category * 8),
            },
            "hospital_impact": {
                "facilities_in_path": max(1, int(s.hospital_count * 0.25)),
                "projected_surge_patients": int(population_affected * 0.02),
            },
            "shelter_impact": {
                "shelters_required": shelters_needed,
                "current_overcrowded": s.shelters_overcrowded,
            },
            "category": category,
            "track_shift_km": shift_km,
        },
        recommendations=[
            f"Pre-stage {evac_buses} evacuation assets along the projected track.",
            f"Open {shelters_needed} shelter(s) outside the {swath_width:.0f}km swath.",
            f"Place {medical_teams} medical strike team(s) on standby for surge.",
            "Issue mandatory evacuation orders for zones within the cone of uncertainty.",
        ],
        operational_risk=round(risk, 1),
    )


def _flood_expansion(s: OperationalSnapshot, p: dict) -> SimulationResult:
    rise_m = float(p.get("water_rise_m", 1.5))
    expansion_km2 = float(p.get("expansion_km2", 25))
    density = float(p.get("population_density", 1200))

    population_affected = int(expansion_km2 * density * (0.3 + rise_m * 0.15))
    risk = _clamp(rise_m * 18 + expansion_km2 * 0.6 + s.incident_severity_score * 0.15)
    boats = max(2, population_affected // 3000)
    return SimulationResult(
        results={
            "population_affected": population_affected,
            "inundated_area_km2": expansion_km2,
            "water_rise_m": rise_m,
            "additional_resources_required": {
                "swiftwater_rescue_boats": boats,
                "high_water_vehicles": max(2, boats // 2),
                "pumps": int(expansion_km2 * 1.5),
            },
            "shelter_impact": {"shelters_required": max(1, population_affected // 1000)},
            "hospital_impact": {"facilities_isolation_risk": max(0, int(s.hospital_count * 0.1))},
        },
        recommendations=[
            f"Deploy {boats} swiftwater rescue boats to the expanding inundation zone.",
            "Relocate ground assets above projected flood stage.",
            "Verify hospital and shelter access routes remain passable.",
        ],
        operational_risk=round(risk, 1),
    )


def _shelter_closure(s: OperationalSnapshot, p: dict) -> SimulationResult:
    closed = int(p.get("shelters_closed", 3))
    avg_occ = max(1, int(p.get("avg_occupancy", 250)))
    displaced = closed * avg_occ
    remaining_headroom = max(0, int(s.shelter_count * 300 * (1 - s.shelter_utilization_pct / 100)))
    overflow = max(0, displaced - remaining_headroom)
    risk = _clamp(50 + (overflow / max(displaced, 1)) * 50)
    return SimulationResult(
        results={
            "shelters_closed": closed,
            "population_displaced": displaced,
            "absorbable_in_network": min(displaced, remaining_headroom),
            "unhoused_overflow": overflow,
            "additional_resources_required": {
                "transport_buses": max(1, displaced // 50),
                "cots": displaced,
                "meals_per_day": displaced * 3,
            },
        },
        recommendations=[
            f"Redistribute {displaced} occupants; network can absorb "
            f"{min(displaced, remaining_headroom)}.",
            (
                f"Stand up overflow capacity for {overflow} people."
                if overflow
                else "Existing network can absorb displacement."
            ),
            "Arrange transport for occupants with mobility or medical needs first.",
        ],
        operational_risk=round(risk, 1),
    )


def _hospital_outage(s: OperationalSnapshot, p: dict) -> SimulationResult:
    beds_lost = int(p.get("beds_lost", 200))
    icu_lost = int(p.get("icu_beds_lost", 30))
    redistributed = int(beds_lost * (1 - s.hospital_capacity_pct / 100))
    risk = _clamp(40 + (s.hospital_capacity_pct * 0.4) + (icu_lost * 0.4))
    return SimulationResult(
        results={
            "beds_lost": beds_lost,
            "icu_beds_lost": icu_lost,
            "redistributable_beds": max(0, redistributed),
            "patients_requiring_transfer": beds_lost,
            "additional_resources_required": {
                "ambulances": max(2, beds_lost // 20),
                "medical_teams": max(1, icu_lost // 10),
            },
            "system_capacity_after_pct": round(
                min(100, s.hospital_capacity_pct + (beds_lost / max(s.hospital_count, 1) / 5)), 1
            ),
        },
        recommendations=[
            f"Transfer {beds_lost} patients; only {max(0, redistributed)} beds available system-wide.",
            f"Prioritize transfer of {icu_lost} ICU patients to facilities with surge capacity.",
            "Activate mutual-aid agreements and request regional medical support.",
        ],
        operational_risk=round(risk, 1),
    )


def _resource_depletion(s: OperationalSnapshot, p: dict) -> SimulationResult:
    rtype = p.get("resource_type", "ambulance")
    pct_lost = float(p.get("pct_lost", 40))
    current = s.resource_by_type.get(rtype, {}).get("total", 0)
    lost = int(current * pct_lost / 100)
    remaining = current - lost
    risk = _clamp(30 + pct_lost * 0.6 + (100 - s.resource_availability_pct) * 0.2)
    return SimulationResult(
        results={
            "resource_type": rtype,
            "current_units": current,
            "units_lost": lost,
            "units_remaining": remaining,
            "coverage_after_pct": round(_clamp((remaining / current * 100) if current else 0), 1),
            "additional_resources_required": {
                "mutual_aid_units": max(0, lost - int(remaining * 0.2))
            },
        },
        recommendations=[
            f"Request {max(0, lost)} {rtype} units via mutual aid to restore coverage.",
            "Reprioritize remaining units to highest-severity incidents.",
            "Throttle non-critical taskings until posture recovers.",
        ],
        operational_risk=round(risk, 1),
    )


def _utility_grid_failure(s: OperationalSnapshot, p: dict) -> SimulationResult:
    customers = int(p.get("customers_affected", 100000))
    duration_h = float(p.get("duration_hours", 24))
    facilities_at_risk = max(1, int(s.hospital_count * 0.3) + int(s.shelter_count * 0.2))
    generators_needed = facilities_at_risk + customers // 20000
    risk = _clamp(35 + (customers / 5000) + duration_h * 0.5)
    return SimulationResult(
        results={
            "customers_affected": customers,
            "duration_hours": duration_h,
            "critical_facilities_at_risk": facilities_at_risk,
            "additional_resources_required": {
                "generators": generators_needed,
                "fuel_trucks": max(2, generators_needed // 5),
                "fuel_liters_per_day": generators_needed * 400,
            },
            "cascading_risk": "high" if duration_h > 48 else "moderate",
        },
        recommendations=[
            f"Deploy {generators_needed} generators, prioritizing {facilities_at_risk} critical facilities.",
            "Establish fuel resupply chain for sustained generator operation.",
            "Activate warming/cooling centers if outage spans extreme temperatures.",
        ],
        operational_risk=round(risk, 1),
    )


_SCENARIOS = {
    enums.SimulationType.HURRICANE_PATH: _hurricane_path,
    enums.SimulationType.FLOOD_EXPANSION: _flood_expansion,
    enums.SimulationType.SHELTER_CLOSURE: _shelter_closure,
    enums.SimulationType.HOSPITAL_OUTAGE: _hospital_outage,
    enums.SimulationType.RESOURCE_DEPLETION: _resource_depletion,
    enums.SimulationType.UTILITY_GRID_FAILURE: _utility_grid_failure,
}


def run_simulation(
    simulation_type: enums.SimulationType,
    parameters: dict,
    snapshot: OperationalSnapshot,
) -> SimulationResult:
    handler = _SCENARIOS.get(simulation_type)
    if handler is None:  # pragma: no cover - guarded by enum validation
        raise ValueError(f"Unsupported simulation type: {simulation_type}")
    result = handler(snapshot, parameters or {})
    result.results["operational_risk_band"] = _risk_band(result.operational_risk)
    return result
