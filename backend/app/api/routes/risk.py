"""Risk Intelligence endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import require_analyst, require_onboarded
from app.database import get_db
from app.models import RiskAssessment, User, enums
from app.schemas.ops import RiskAssessmentOut
from app.services import analytics, audit_service, risk_service

router = APIRouter(prefix="/risk", tags=["Risk Intelligence"])


@router.get("", response_model=list[RiskAssessmentOut])
def list_risk(
    category: enums.RiskCategory | None = Query(None),
    db: Session = Depends(get_db),
    user: User = Depends(require_onboarded),
) -> list[RiskAssessment]:
    stmt = select(RiskAssessment).order_by(RiskAssessment.score.desc())
    if category:
        stmt = stmt.where(RiskAssessment.category == category)
    rows = list(db.scalars(stmt).all())
    if not rows:  # generate on first access so the module is never empty
        snap = analytics.build_snapshot(db)
        rows = risk_service.generate_and_store(db, snap, user.organization_id)
    return rows


@router.post("/generate", response_model=list[RiskAssessmentOut])
def generate(
    db: Session = Depends(get_db), user: User = Depends(require_analyst)
) -> list[RiskAssessment]:
    snap = analytics.build_snapshot(db)
    rows = risk_service.generate_and_store(db, snap, user.organization_id)
    audit_service.log(db, actor=user, action="generate_risk", entity_type="risk_assessment")
    return rows
