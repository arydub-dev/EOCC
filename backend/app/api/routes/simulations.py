"""Simulation Center endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_analyst
from app.database import get_db
from app.models import Simulation, User
from app.schemas.ops import SimulationCreate, SimulationOut
from app.services import analytics, audit_service, simulation_service

router = APIRouter(prefix="/simulations", tags=["Simulation Center"])


@router.get("", response_model=list[SimulationOut])
def list_simulations(db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> list[Simulation]:
    return list(db.scalars(select(Simulation).order_by(Simulation.created_at.desc()).limit(100)).all())


@router.get("/{simulation_id}", response_model=SimulationOut)
def get_simulation(
    simulation_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)
) -> Simulation:
    sim = db.get(Simulation, simulation_id)
    if not sim:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Simulation not found")
    return sim


@router.post("/run", response_model=SimulationOut, status_code=status.HTTP_201_CREATED)
def run_simulation(
    payload: SimulationCreate, db: Session = Depends(get_db), user: User = Depends(require_analyst)
) -> Simulation:
    snap = analytics.build_snapshot(db)
    sim = simulation_service.run_and_store(db, payload, snap, user.id, user.organization_id)
    audit_service.log(
        db, actor=user, action="run_simulation", entity_type="simulation", entity_id=sim.id,
        detail={"type": payload.simulation_type.value},
    )
    return sim
