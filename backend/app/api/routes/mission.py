"""Mission Control endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.models import User
from app.schemas.mission import HealthBreakdown, MissionControlSummary
from app.services import analytics, mission_service

router = APIRouter(prefix="/mission-control", tags=["Mission Control"])


@router.get("/summary", response_model=MissionControlSummary)
def summary(
    db: Session = Depends(get_db), _: User = Depends(get_current_user)
) -> MissionControlSummary:
    snap = analytics.build_snapshot(db)
    return mission_service.build_mission_control(db, snap)


@router.get("/health", response_model=HealthBreakdown)
def health(db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> HealthBreakdown:
    snap = analytics.build_snapshot(db)
    return mission_service.build_health_breakdown(snap)
