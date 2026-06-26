"""Applies the scoring engines to ORM entities and enriches output payloads."""

from __future__ import annotations

from app.engines import scoring
from app.models import Hospital, Incident, Shelter


def recompute_incident(incident: Incident) -> None:
    result = scoring.incident_severity(
        base_severity=incident.severity,
        incident_type=incident.incident_type,
        status=incident.status,
        population_impacted=incident.population_impacted,
        radius_km=incident.radius_km,
    )
    incident.severity_score = result.rounded()


def recompute_hospital(hospital: Hospital) -> None:
    result = scoring.hospital_stress(
        total_beds=hospital.total_beds,
        occupied_beds=hospital.occupied_beds,
        icu_beds=hospital.icu_beds,
        icu_occupied=hospital.icu_occupied,
        er_capacity=hospital.er_capacity,
        er_patients=hospital.er_patients,
        staff_on_duty=hospital.staff_on_duty,
        staff_required=hospital.staff_required,
        ventilators_total=hospital.ventilators_total,
        ventilators_in_use=hospital.ventilators_in_use,
    )
    hospital.stress_score = result.rounded()
    hospital.status = scoring.hospital_status_from_score(result.score, hospital.accepts_diversions)


def recompute_shelter(shelter: Shelter) -> None:
    result = scoring.shelter_utilization(
        capacity=shelter.capacity,
        occupancy=shelter.occupancy,
        food_supply_days=shelter.food_supply_days,
        water_supply_days=shelter.water_supply_days,
    )
    shelter.utilization_score = result.rounded()
    shelter.status = scoring.shelter_status_from(shelter.occupancy, shelter.capacity)


def _pct(num: int, den: int) -> float:
    return round((num / den) * 100, 1) if den > 0 else 0.0


def hospital_out(hospital: Hospital) -> dict:
    data = {c.name: getattr(hospital, c.name) for c in hospital.__table__.columns}
    data["bed_occupancy_pct"] = _pct(hospital.occupied_beds, hospital.total_beds)
    data["icu_occupancy_pct"] = _pct(hospital.icu_occupied, hospital.icu_beds)
    data["er_load_pct"] = _pct(hospital.er_patients, hospital.er_capacity)
    return data


def shelter_out(shelter: Shelter) -> dict:
    data = {c.name: getattr(shelter, c.name) for c in shelter.__table__.columns}
    data["occupancy_pct"] = _pct(shelter.occupancy, shelter.capacity)
    return data
