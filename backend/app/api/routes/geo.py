"""Geographic Operations Map data endpoints.

Returns lightweight, map-ready feature collections for all operational layers
so the frontend can render a single rich, color-coded situational map.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.models import Hospital, Incident, Resource, Shelter, UtilityOutage, User, enums

router = APIRouter(prefix="/geo", tags=["Geographic Operations"])


def _risk_color(score: float) -> str:
    if score >= 85:
        return "#dc2626"  # red
    if score >= 70:
        return "#ea580c"  # orange
    if score >= 50:
        return "#f59e0b"  # amber
    if score >= 30:
        return "#eab308"  # yellow
    return "#22c55e"  # green


@router.get("/features")
def map_features(
    layers: str = Query("incidents,hospitals,shelters,resources,utilities"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> dict:
    requested = {layer.strip() for layer in layers.split(",") if layer.strip()}
    out: dict = {"layers": {}}

    if "incidents" in requested:
        out["layers"]["incidents"] = [
            {
                "id": i.id,
                "name": i.name,
                "type": i.incident_type.value,
                "status": i.status.value,
                "lat": i.latitude,
                "lng": i.longitude,
                "radius_km": i.radius_km,
                "severity_score": i.severity_score,
                "population_impacted": i.population_impacted,
                "color": _risk_color(i.severity_score),
            }
            for i in db.scalars(
                select(Incident).where(Incident.status != enums.IncidentStatus.RESOLVED)
            ).all()
        ]

    if "hospitals" in requested:
        out["layers"]["hospitals"] = [
            {
                "id": h.id,
                "name": h.name,
                "lat": h.latitude,
                "lng": h.longitude,
                "status": h.status.value,
                "stress_score": h.stress_score,
                "color": _risk_color(h.stress_score),
            }
            for h in db.scalars(select(Hospital)).all()
        ]

    if "shelters" in requested:
        out["layers"]["shelters"] = [
            {
                "id": s.id,
                "name": s.name,
                "lat": s.latitude,
                "lng": s.longitude,
                "status": s.status.value,
                "occupancy": s.occupancy,
                "capacity": s.capacity,
                "utilization_score": s.utilization_score,
                "color": _risk_color(s.utilization_score),
            }
            for s in db.scalars(select(Shelter)).all()
        ]

    if "resources" in requested:
        out["layers"]["resources"] = [
            {
                "id": r.id,
                "name": r.name,
                "type": r.resource_type.value,
                "lat": r.latitude,
                "lng": r.longitude,
                "status": r.status.value,
            }
            for r in db.scalars(select(Resource)).all()
        ]

    if "utilities" in requested:
        out["layers"]["utilities"] = [
            {
                "id": o.id,
                "type": o.utility_type.value,
                "lat": o.latitude,
                "lng": o.longitude,
                "status": o.status.value,
                "customers_affected": o.customers_affected,
            }
            for o in db.scalars(
                select(UtilityOutage).where(UtilityOutage.status != enums.UtilityOutageStatus.RESTORED)
            ).all()
        ]

    return out
