"""Builds the OperationalSnapshot from the database.

This is the single source of truth aggregation used by Mission Control, Risk
Intelligence, the Copilot, the Briefing Center and the Simulation Center.
"""
from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.engines import scoring
from app.engines.snapshot import (
    HospitalRiskItem,
    IncidentSnapshot,
    OperationalSnapshot,
    ShelterRiskItem,
)
from app.models import (
    Alert,
    Hospital,
    Incident,
    Resource,
    Shelter,
    UtilityOutage,
    enums,
)

ACTIVE_INCIDENT_STATUSES = (
    enums.IncidentStatus.ACTIVE,
    enums.IncidentStatus.ESCALATING,
    enums.IncidentStatus.MONITORING,
)


def build_snapshot(db: Session) -> OperationalSnapshot:
    snap = OperationalSnapshot()
    regions: set[str] = set()

    # ── Incidents ──
    incidents = list(
        db.scalars(select(Incident).where(Incident.status.in_(ACTIVE_INCIDENT_STATUSES))).all()
    )
    severities: list[float] = []
    for inc in incidents:
        snap.incidents.append(
            IncidentSnapshot(
                id=inc.id,
                name=inc.name,
                incident_type=inc.incident_type.value,
                status=inc.status.value,
                severity_score=inc.severity_score,
                population_impacted=inc.population_impacted,
                region=inc.region,
            )
        )
        severities.append(inc.severity_score)
        snap.total_population_impacted += inc.population_impacted
        if inc.region:
            regions.add(inc.region)
        if inc.status == enums.IncidentStatus.ESCALATING:
            snap.escalating_incidents += 1
    snap.active_incidents = len(incidents)
    snap.incident_severity_score = round(max(severities), 1) if severities else 0.0
    snap.avg_incident_severity = round(sum(severities) / len(severities), 1) if severities else 0.0

    # ── Hospitals ──
    hospitals = list(db.scalars(select(Hospital)).all())
    snap.hospital_count = len(hospitals)
    total_beds = occ_beds = icu_beds = icu_occ = 0
    stress_sum = 0.0
    hosp_items: list[HospitalRiskItem] = []
    for h in hospitals:
        total_beds += h.total_beds
        occ_beds += h.occupied_beds
        icu_beds += h.icu_beds
        icu_occ += h.icu_occupied
        stress_sum += h.stress_score
        if h.stress_score >= 55:
            snap.hospitals_at_risk += 1
        if h.region:
            regions.add(h.region)
        hosp_items.append(
            HospitalRiskItem(
                id=h.id,
                name=h.name,
                region=h.region,
                stress_score=h.stress_score,
                status=h.status.value,
                icu_occupancy_pct=round((h.icu_occupied / h.icu_beds * 100) if h.icu_beds else 0, 1),
            )
        )
    snap.avg_hospital_stress = round(stress_sum / len(hospitals), 1) if hospitals else 0.0
    snap.hospital_capacity_pct = round((occ_beds / total_beds * 100) if total_beds else 0, 1)
    snap.icu_occupancy_pct = round((icu_occ / icu_beds * 100) if icu_beds else 0, 1)
    snap.top_stressed_hospitals = sorted(hosp_items, key=lambda x: x.stress_score, reverse=True)[:10]

    # ── Shelters ──
    shelters = list(db.scalars(select(Shelter)).all())
    snap.shelter_count = len(shelters)
    cap_sum = occ_sum = 0
    strain_sum = 0.0
    shelter_items: list[ShelterRiskItem] = []
    for sh in shelters:
        cap_sum += sh.capacity
        occ_sum += sh.occupancy
        strain_sum += sh.utilization_score
        if sh.capacity and sh.occupancy / sh.capacity >= 0.95:
            snap.shelters_overcrowded += 1
        if sh.food_supply_days < 2 or sh.water_supply_days < 2:
            snap.shelters_low_supply += 1
        if sh.region:
            regions.add(sh.region)
        shelter_items.append(
            ShelterRiskItem(
                id=sh.id,
                name=sh.name,
                region=sh.region,
                utilization_score=sh.utilization_score,
                occupancy_pct=round((sh.occupancy / sh.capacity * 100) if sh.capacity else 0, 1),
                food_supply_days=sh.food_supply_days,
            )
        )
    snap.shelter_utilization_pct = round((occ_sum / cap_sum * 100) if cap_sum else 0, 1)
    snap.avg_shelter_strain = round(strain_sum / len(shelters), 1) if shelters else 0.0
    snap.top_strained_shelters = sorted(shelter_items, key=lambda x: x.utilization_score, reverse=True)[:10]

    # ── Resources ──
    resources = list(db.scalars(select(Resource)).all())
    snap.resource_total = len(resources)
    readiness_sum = 0.0
    by_type: dict[str, dict] = {}
    for r in resources:
        readiness_sum += r.readiness
        bucket = by_type.setdefault(
            r.resource_type.value, {"total": 0, "available": 0, "assigned": 0, "readiness_sum": 0.0}
        )
        bucket["total"] += 1
        bucket["readiness_sum"] += r.readiness
        if r.status == enums.ResourceStatus.AVAILABLE:
            snap.resource_available += 1
            bucket["available"] += 1
        elif r.status in (
            enums.ResourceStatus.ASSIGNED,
            enums.ResourceStatus.EN_ROUTE,
            enums.ResourceStatus.ON_SCENE,
        ):
            snap.resource_assigned += 1
            bucket["assigned"] += 1
        if r.region:
            regions.add(r.region)
    for name, bucket in by_type.items():
        bucket["readiness_avg"] = round(bucket["readiness_sum"] / bucket["total"], 1) if bucket["total"] else 0
        avail_pct = (bucket["available"] / bucket["total"] * 100) if bucket["total"] else 0
        if avail_pct < 15:
            snap.depleted_resource_types.append(name)
    snap.resource_by_type = by_type
    snap.resource_availability_pct = round(
        (snap.resource_available / snap.resource_total * 100) if snap.resource_total else 0, 1
    )
    snap.resource_readiness_pct = round(readiness_sum / snap.resource_total, 1) if snap.resource_total else 0.0
    readiness_result = scoring.resource_readiness(
        total=snap.resource_total,
        available=snap.resource_available,
        assigned=snap.resource_assigned,
        avg_readiness=snap.resource_readiness_pct,
    )
    snap.resource_readiness_score = readiness_result.rounded()

    # ── Utilities ──
    outages = list(
        db.scalars(
            select(UtilityOutage).where(
                UtilityOutage.status != enums.UtilityOutageStatus.RESTORED
            )
        ).all()
    )
    snap.utility_outages_active = len(outages)
    for o in outages:
        snap.customers_without_service += o.customers_affected
        snap.utility_by_type[o.utility_type.value] = snap.utility_by_type.get(o.utility_type.value, 0) + 1
        if o.region:
            regions.add(o.region)

    # ── Alerts ──
    open_alerts = list(db.scalars(select(Alert).where(Alert.status != enums.AlertStatus.RESOLVED)).all())
    snap.open_alerts = len(open_alerts)
    for a in open_alerts:
        if a.severity in (enums.AlertSeverity.CRITICAL, enums.AlertSeverity.EMERGENCY):
            snap.critical_alerts += 1
        snap.alerts_by_category[a.category.value] = snap.alerts_by_category.get(a.category.value, 0) + 1

    # ── Composite health ──
    health = scoring.overall_health(
        incident_severity_score=snap.incident_severity_score,
        hospital_stress_score=snap.avg_hospital_stress,
        shelter_strain_score=snap.avg_shelter_strain,
        resource_readiness_score=snap.resource_readiness_score,
        open_critical_alerts=snap.critical_alerts,
    )
    snap.overall_health_score = health.rounded()
    snap.health_status = health.band
    snap.regions = sorted(regions)
    return snap
