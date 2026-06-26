"""Simulation Center service."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.engines import simulation_engine
from app.engines.snapshot import OperationalSnapshot
from app.models import Simulation, enums
from app.schemas.ops import SimulationCreate


def run_and_store(
    db: Session,
    payload: SimulationCreate,
    snap: OperationalSnapshot,
    user_id: int | None,
    org_id: int | None = None,
) -> Simulation:
    result = simulation_engine.run_simulation(payload.simulation_type, payload.parameters, snap)
    sim = Simulation(
        organization_id=org_id,
        name=payload.name,
        simulation_type=payload.simulation_type,
        status=enums.SimulationStatus.COMPLETED,
        parameters=payload.parameters,
        results=result.results,
        recommendations=result.recommendations,
        operational_risk=result.operational_risk,
        created_by_id=user_id,
    )
    db.add(sim)
    db.commit()
    db.refresh(sim)
    return sim
