"""AI Operations Copilot endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.core.deps import get_current_user
from app.database import get_db
from app.models import AIReport, User
from app.schemas.ai import AIReportOut, CopilotQuery, CopilotResponse
from app.services import analytics, copilot_service

router = APIRouter(prefix="/copilot", tags=["AI Copilot"])


@router.get("/status")
def copilot_status(_: User = Depends(get_current_user)) -> dict:
    return {
        "engine": "openai" if settings.ai_enabled else "deterministic",
        "ai_enabled": settings.ai_enabled,
        "model": settings.OPENAI_MODEL if settings.ai_enabled else "local-deterministic",
        "suggested_questions": [
            "Which hospitals are under the most stress?",
            "Where should we deploy additional resources?",
            "Which shelters will reach capacity first?",
            "What incidents pose the highest risk?",
        ],
    }


@router.post("/ask", response_model=CopilotResponse)
def ask(
    payload: CopilotQuery, db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> CopilotResponse:
    snap = analytics.build_snapshot(db)
    return copilot_service.ask(db, payload.question, snap, user.id, user.organization_id)


@router.get("/history", response_model=list[AIReportOut])
def history(db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> list[AIReport]:
    return list(
        db.scalars(
            select(AIReport)
            .where(AIReport.report_type == "copilot")
            .order_by(AIReport.created_at.desc())
            .limit(50)
        ).all()
    )
