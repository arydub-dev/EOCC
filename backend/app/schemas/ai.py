"""Schemas for AI Copilot and Executive Briefing."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CopilotQuery(BaseModel):
    question: str
    context_hint: str | None = None


class CopilotResponse(BaseModel):
    answer: str
    engine: str
    confidence: float
    grounding: dict
    suggested_actions: list[str] = []
    citations: list[str] = []
    follow_ups: list[str] = []


class BriefingSection(BaseModel):
    heading: str
    body: str
    bullets: list[str] = []


class ExecutiveBriefing(BaseModel):
    title: str
    generated_at: datetime
    engine: str
    executive_summary: str
    sections: list[BriefingSection]
    markdown: str


class AIReportOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    report_type: str
    title: str
    content: str
    structured: dict | None = None
    engine: str
    created_at: datetime
