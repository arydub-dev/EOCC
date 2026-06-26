"""Executive Briefing Center service."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.engines import briefing
from app.engines.snapshot import OperationalSnapshot
from app.models import AIReport
from app.schemas.ai import BriefingSection, ExecutiveBriefing


def generate(
    db: Session, snap: OperationalSnapshot, user_id: int | None, org_id: int | None = None
) -> ExecutiveBriefing:
    data = briefing.build_briefing(snap)
    report = AIReport(
        organization_id=org_id,
        report_type="executive_briefing",
        title=data["title"],
        content=data["markdown"],
        structured={"sections": data["sections"], "summary": data["executive_summary"]},
        engine="deterministic",
        created_by_id=user_id,
    )
    db.add(report)
    db.commit()

    return ExecutiveBriefing(
        title=data["title"],
        generated_at=data["generated_at"],
        engine="deterministic",
        executive_summary=data["executive_summary"],
        sections=[BriefingSection(**s) for s in data["sections"]],
        markdown=data["markdown"],
    )
