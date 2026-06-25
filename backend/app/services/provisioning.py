"""Workspace provisioning.

Generates a complete, organization-scoped synthetic operational picture for a
tenant's *Demo Mode* workspace. Connected Mode workspaces start empty and are
populated via the Data Integration Center instead.
"""
from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.tenancy import set_session_org
from app.models import (
    Alert,
    DataSource,
    Hospital,
    Incident,
    IncidentEvent,
    Organization,
    Resource,
    Shelter,
    UtilityOutage,
    enums,
)
from app.seed import data as ref
from app.services import analytics, risk_service, simulation_service
from app.services.scoring_service import (
    recompute_hospital,
    recompute_incident,
    recompute_shelter,
)

DEMO = enums.DataOrigin.DEMO


def _now() -> datetime:
    return datetime.now(timezone.utc)


def provision_demo_workspace(
    db: Session,
    org: Organization,
    *,
    rng: random.Random | None = None,
    incidents: int = 30,
    hospitals: int = 15,
    shelters: int = 45,
    resources: int = 250,
    utility_outages: int = 90,
    alerts: int = 180,
) -> dict:
    """Populate an organization with synthetic demo data (all origin=demo)."""
    r = rng or random.Random(f"{org.id}-{org.slug}")
    oid = org.id

    def jitter(c: float, s: float) -> float:
        return round(c + r.uniform(-s, s), 5)

    # ── Incidents + event timelines ──
    inc_rows: list[Incident] = []
    for _ in range(incidents):
        region, lat, lng, density = r.choice(ref.REGIONS)
        itype = r.choice(list(enums.IncidentType))
        prefix = r.choice(ref.INCIDENT_NAME_PREFIX[itype.value])
        suffix = r.choice(ref.INCIDENT_NAME_SUFFIX[itype.value])
        severity = r.choices([1, 2, 3, 4, 5], weights=[10, 22, 30, 25, 13])[0]
        status = r.choices(list(enums.IncidentStatus), weights=[15, 40, 12, 18, 15])[0]
        radius = round(r.uniform(2, 45), 1)
        population = int(radius * radius * density * (severity / 5) * r.uniform(0.05, 0.25))
        started = _now() - timedelta(hours=r.uniform(1, 240))
        inc = Incident(
            organization_id=oid,
            data_origin=DEMO,
            name=f"{prefix} {suffix}",
            incident_type=itype,
            status=status,
            description=f"{itype.value.replace('_', ' ').title()} affecting the {region} area.",
            region=region,
            latitude=jitter(lat, 0.6),
            longitude=jitter(lng, 0.6),
            radius_km=radius,
            severity=severity,
            population_impacted=population,
            started_at=started,
            estimated_duration_hours=round(r.uniform(6, 168), 1),
            resolved_at=started + timedelta(hours=r.uniform(4, 80))
            if status == enums.IncidentStatus.RESOLVED
            else None,
        )
        recompute_incident(inc)
        db.add(inc)
        inc_rows.append(inc)
    db.flush()

    events = [
        ("report", "Initial report received and incident opened."),
        ("resource_dispatch", "Initial response resources dispatched to scene."),
        ("escalation", "Conditions worsened; incident severity reassessed."),
        ("evacuation", "Evacuation advisory issued for affected zone."),
        ("update", "Situation update logged by incident commander."),
        ("containment", "Partial containment achieved by response teams."),
    ]
    for inc in inc_rows:
        t = inc.started_at
        for i in range(r.randint(2, 6)):
            etype, descr = events[min(i, len(events) - 1)]
            t += timedelta(hours=r.uniform(1, 12))
            db.add(
                IncidentEvent(
                    incident_id=inc.id,
                    event_type=etype,
                    description=descr,
                    severity_delta=round(r.uniform(-3, 6), 1),
                    occurred_at=t,
                )
            )

    # ── Hospitals ──
    hosp_rows: list[Hospital] = []
    for _ in range(hospitals):
        region, lat, lng, _ = r.choice(ref.REGIONS)
        total_beds = r.randint(80, 700)
        icu_beds = int(total_beds * r.uniform(0.08, 0.18))
        er_cap = r.randint(20, 120)
        staff_required = int(total_beds * r.uniform(0.8, 1.2))
        h = Hospital(
            organization_id=oid,
            data_origin=DEMO,
            name=f"{region.split()[0]} {r.choice(ref.HOSPITAL_NAMES)} Hospital",
            region=region,
            latitude=jitter(lat, 0.4),
            longitude=jitter(lng, 0.4),
            total_beds=total_beds,
            occupied_beds=min(total_beds, int(total_beds * r.uniform(0.55, 0.99))),
            icu_beds=icu_beds,
            icu_occupied=min(icu_beds, int(icu_beds * r.uniform(0.5, 1.05))),
            er_capacity=er_cap,
            er_patients=int(er_cap * r.uniform(0.4, 1.2)),
            staff_required=staff_required,
            staff_on_duty=int(staff_required * r.uniform(0.6, 1.05)),
            ventilators_total=int(icu_beds * r.uniform(0.6, 1.0)) + 2,
            ventilators_in_use=0,
            accepts_diversions=r.random() > 0.15,
        )
        h.ventilators_in_use = int(h.ventilators_total * r.uniform(0.3, 1.0))
        recompute_hospital(h)
        db.add(h)
        hosp_rows.append(h)

    # ── Shelters ──
    shelter_rows: list[Shelter] = []
    for _ in range(shelters):
        region, lat, lng, _ = r.choice(ref.REGIONS)
        capacity = r.randint(50, 1200)
        sh = Shelter(
            organization_id=oid,
            data_origin=DEMO,
            name=f"{region} {r.choice(ref.SHELTER_VENUES)}",
            region=region,
            latitude=jitter(lat, 0.5),
            longitude=jitter(lng, 0.5),
            capacity=capacity,
            occupancy=min(int(capacity * 1.05), int(capacity * r.uniform(0.2, 1.05))),
            food_supply_days=round(r.uniform(0.5, 10), 1),
            water_supply_days=round(r.uniform(0.5, 10), 1),
            medical_kits=r.randint(0, 60),
            medical_staff=r.randint(0, 12),
        )
        recompute_shelter(sh)
        db.add(sh)
        shelter_rows.append(sh)

    # ── Resources ──
    statuses = list(enums.ResourceStatus)
    weights = [42, 24, 12, 10, 8, 4]
    for i in range(resources):
        region, lat, lng, _ = r.choice(ref.REGIONS)
        rtype = r.choice(list(enums.ResourceType))
        label, unit, base_cap = ref.RESOURCE_LABELS[rtype.value]
        capacity = base_cap * r.uniform(0.7, 1.5)
        db.add(
            Resource(
                organization_id=oid,
                data_origin=DEMO,
                name=f"{label} {i + 1:04d}",
                resource_type=rtype,
                status=r.choices(statuses, weights=weights)[0],
                region=region,
                home_base=f"{region} Operations Base",
                latitude=jitter(lat, 0.7),
                longitude=jitter(lng, 0.7),
                capacity=round(capacity, 1),
                capacity_unit=unit,
                quantity_available=round(capacity * r.uniform(0.1, 1.0), 1),
                readiness=round(r.uniform(45, 100), 1),
            )
        )

    # ── Utility outages ──
    for _ in range(utility_outages):
        region, lat, lng, _ = r.choice(ref.REGIONS)
        started = _now() - timedelta(hours=r.uniform(0.5, 96))
        db.add(
            UtilityOutage(
                organization_id=oid,
                data_origin=DEMO,
                utility_type=r.choice(list(enums.UtilityType)),
                status=r.choices(list(enums.UtilityOutageStatus), weights=[25, 25, 30, 20])[0],
                region=region,
                latitude=jitter(lat, 0.7),
                longitude=jitter(lng, 0.7),
                customers_affected=r.choices(
                    [r.randint(50, 5000), r.randint(5000, 50000), r.randint(50000, 250000)],
                    weights=[60, 30, 10],
                )[0],
                description="Service interruption reported by automated monitoring.",
                started_at=started,
                estimated_restoration=started + timedelta(hours=r.uniform(2, 72)),
                incident_id=r.choice(inc_rows).id if inc_rows and r.random() < 0.25 else None,
            )
        )

    # ── Data sources ──
    for name, stype, endpoint in ref.DATA_SOURCES:
        status = r.choices(list(enums.DataSourceStatus), weights=[70, 18, 8, 4])[0]
        db.add(
            DataSource(
                organization_id=oid,
                name=name,
                source_type=enums.DataSourceType(stype),
                status=status,
                endpoint=endpoint,
                description=f"Connector for {name}.",
                last_sync_at=_now() - timedelta(minutes=r.uniform(1, 120)),
                sync_interval_minutes=r.choice([5, 10, 15, 30, 60]),
                records_synced=r.randint(1000, 500000),
                health_score=round(r.uniform(60, 100), 1)
                if status == enums.DataSourceStatus.HEALTHY
                else round(r.uniform(20, 70), 1),
                enabled=True,
            )
        )

    # ── Alerts ──
    cats = list(enums.AlertCategory)
    sevs = list(enums.AlertSeverity)
    stats = list(enums.AlertStatus)
    titles = {
        enums.AlertCategory.HOSPITAL_OVERLOAD: "Hospital approaching capacity",
        enums.AlertCategory.SHELTER_CAPACITY: "Shelter nearing capacity",
        enums.AlertCategory.RESOURCE_SHORTAGE: "Resource availability low",
        enums.AlertCategory.INCIDENT_ESCALATION: "Incident severity increasing",
        enums.AlertCategory.UTILITY_FAILURE: "Utility service disruption",
        enums.AlertCategory.ENVIRONMENTAL: "Environmental hazard detected",
    }
    for _ in range(alerts):
        cat = r.choice(cats)
        status = r.choices(stats, weights=[35, 25, 40])[0]
        triggered = _now() - timedelta(hours=r.uniform(0.2, 200))
        region = r.choice(ref.REGIONS)[0]
        db.add(
            Alert(
                organization_id=oid,
                data_origin=DEMO,
                category=cat,
                severity=r.choices(sevs, weights=[30, 38, 24, 8])[0],
                status=status,
                title=titles[cat],
                message=f"{titles[cat]} in {region}. Automated threshold breach detected.",
                region=region,
                source="threshold_engine",
                incident_id=r.choice(inc_rows).id if inc_rows and r.random() < 0.4 else None,
                hospital_id=r.choice(hosp_rows).id
                if hosp_rows and cat == enums.AlertCategory.HOSPITAL_OVERLOAD
                else None,
                shelter_id=r.choice(shelter_rows).id
                if shelter_rows and cat == enums.AlertCategory.SHELTER_CAPACITY
                else None,
                triggered_at=triggered,
                acknowledged_at=triggered + timedelta(minutes=r.uniform(5, 60))
                if status != enums.AlertStatus.OPEN
                else None,
                resolved_at=triggered + timedelta(hours=r.uniform(1, 24))
                if status == enums.AlertStatus.RESOLVED
                else None,
            )
        )

    db.commit()

    # ── Derived intelligence (scoped to this org) ──
    set_session_org(db, oid)
    snap = analytics.build_snapshot(db)
    risk_service.generate_and_store(db, snap, oid)
    _provision_sample_sims(db, snap, oid)

    org.provisioned = True
    db.commit()
    return {
        "incidents": incidents,
        "hospitals": hospitals,
        "shelters": shelters,
        "resources": resources,
        "utility_outages": utility_outages,
        "alerts": alerts,
    }


def _provision_sample_sims(db: Session, snap, oid: int) -> None:
    from app.schemas.ops import SimulationCreate

    samples = [
        SimulationCreate(
            name="Category 4 Hurricane — 60km track shift",
            simulation_type=enums.SimulationType.HURRICANE_PATH,
            parameters={"category": 4, "track_shift_km": 60, "population_density": 1800},
        ),
        SimulationCreate(
            name="Riverine Flood — 2.5m rise",
            simulation_type=enums.SimulationType.FLOOD_EXPANSION,
            parameters={"water_rise_m": 2.5, "expansion_km2": 40, "population_density": 1500},
        ),
    ]
    for sample in samples:
        simulation_service.run_and_store(db, sample, snap, user_id=None, org_id=oid)
