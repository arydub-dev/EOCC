"""Schemas for Mission Control aggregate views."""
from __future__ import annotations

from pydantic import BaseModel

from app.schemas.ops import AlertOut


class MetricCard(BaseModel):
    key: str
    label: str
    value: float
    unit: str | None = None
    trend: float | None = None  # percent change vs baseline
    status: str = "normal"  # normal | watch | warning | critical
    detail: str | None = None


class RecommendedAction(BaseModel):
    priority: int
    title: str
    rationale: str
    category: str
    impact: str
    confidence: float


class MissionControlSummary(BaseModel):
    overall_health_score: float
    health_status: str
    incident_severity_score: float
    population_impacted: int
    active_incidents: int
    escalating_incidents: int
    hospital_capacity_pct: float
    hospitals_at_risk: int
    shelter_utilization_pct: float
    shelters_overcrowded: int
    resource_availability_pct: float
    resource_readiness_pct: float
    open_alerts: int
    critical_alerts: int
    metrics: list[MetricCard]
    critical_alerts_list: list[AlertOut]
    recommended_actions: list[RecommendedAction]
    situation_report: str


class HealthBreakdown(BaseModel):
    overall_health_score: float
    health_status: str
    components: dict[str, float]
    explanation: str
