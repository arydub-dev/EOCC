"""Aggregate API router mounting every module."""
from __future__ import annotations

from fastapi import APIRouter

from app.api.routes import (
    alerts,
    audit,
    auth,
    briefing,
    copilot,
    geo,
    hospitals,
    incidents,
    integration,
    mission,
    resources,
    risk,
    security,
    shelters,
    simulations,
    utilities,
    workspace,
)

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(auth.router_users)
api_router.include_router(workspace.router)
api_router.include_router(mission.router)
api_router.include_router(incidents.router)
api_router.include_router(hospitals.router)
api_router.include_router(shelters.router)
api_router.include_router(resources.router)
api_router.include_router(utilities.router)
api_router.include_router(geo.router)
api_router.include_router(risk.router)
api_router.include_router(alerts.router)
api_router.include_router(simulations.router)
api_router.include_router(copilot.router)
api_router.include_router(briefing.router)
api_router.include_router(integration.router)
api_router.include_router(audit.router)
api_router.include_router(security.router)
