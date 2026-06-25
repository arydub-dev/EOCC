"""Risk Intelligence service: generates and persists risk assessments."""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.engines import risk_engine
from app.engines.snapshot import OperationalSnapshot
from app.models import RiskAssessment


def generate_and_store(
    db: Session, snap: OperationalSnapshot, org_id: int | None = None
) -> list[RiskAssessment]:
    """Regenerate the current risk picture, replacing any prior snapshot."""
    db.execute(
        delete(RiskAssessment).where(
            RiskAssessment.incident_id.is_(None),
            RiskAssessment.organization_id == org_id,
        )
    )
    now = datetime.now(timezone.utc)
    rows: list[RiskAssessment] = []
    for result in risk_engine.assess_all(snap):
        row = RiskAssessment(
            organization_id=org_id,
            category=result.category,
            severity=result.severity,
            score=result.score,
            title=result.title,
            explanation=result.explanation,
            recommendations=result.recommendations,
            factors=result.factors,
            generated_at=now,
        )
        db.add(row)
        rows.append(row)
    db.commit()
    for row in rows:
        db.refresh(row)
    return rows
