"""Executive Briefing Center endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.models import AIReport, User
from app.schemas.ai import ExecutiveBriefing
from app.services import analytics, briefing_service

router = APIRouter(prefix="/briefing", tags=["Executive Briefing"])


@router.post("/generate", response_model=ExecutiveBriefing)
def generate(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> ExecutiveBriefing:
    snap = analytics.build_snapshot(db)
    return briefing_service.generate(db, snap, user.id, user.organization_id)


@router.get("/markdown", response_class=PlainTextResponse)
def latest_markdown(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> str:
    snap = analytics.build_snapshot(db)
    briefing = briefing_service.generate(db, snap, user.id, user.organization_id)
    return briefing.markdown
