"""Schemas for risk, alerts and simulations."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models import enums


# ──────────────────────────── Risk ────────────────────────────
class RiskAssessmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category: enums.RiskCategory
    severity: enums.RiskSeverity
    score: float
    title: str
    explanation: str
    recommendations: list[str] | None = None
    factors: dict | None = None
    region: str | None = None
    incident_id: int | None = None
    generated_at: datetime


# ──────────────────────────── Alerts ────────────────────────────
class AlertOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category: enums.AlertCategory
    severity: enums.AlertSeverity
    status: enums.AlertStatus
    title: str
    message: str
    region: str | None = None
    source: str | None = None
    incident_id: int | None = None
    hospital_id: int | None = None
    shelter_id: int | None = None
    acknowledged_at: datetime | None = None
    resolved_at: datetime | None = None
    response_actions: list[dict] | None = None
    triggered_at: datetime


class AlertCreate(BaseModel):
    category: enums.AlertCategory
    severity: enums.AlertSeverity = enums.AlertSeverity.WARNING
    title: str
    message: str
    region: str | None = None
    source: str | None = "manual"
    incident_id: int | None = None
    hospital_id: int | None = None
    shelter_id: int | None = None


class AlertActionRequest(BaseModel):
    action: str
    notes: str | None = None


# ──────────────────────────── Simulations ────────────────────────────
class SimulationCreate(BaseModel):
    name: str
    simulation_type: enums.SimulationType
    parameters: dict


class SimulationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    simulation_type: enums.SimulationType
    status: enums.SimulationStatus
    parameters: dict
    results: dict | None = None
    recommendations: list[str] | None = None
    operational_risk: float
    created_by_id: int | None = None
    created_at: datetime
