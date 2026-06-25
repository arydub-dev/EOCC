"""Alert Management endpoints."""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_manager
from app.database import get_db
from app.models import Alert, User, enums
from app.schemas.common import Page, PaginationParams
from app.schemas.ops import AlertActionRequest, AlertCreate, AlertOut
from app.services import alert_service, audit_service
from app.services.common import paginate

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("", response_model=Page[AlertOut])
def list_alerts(
    params: PaginationParams = Depends(),
    category: enums.AlertCategory | None = Query(None),
    severity: enums.AlertSeverity | None = Query(None),
    alert_status: enums.AlertStatus | None = Query(None, alias="status"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> Page[AlertOut]:
    stmt = select(Alert)
    if category:
        stmt = stmt.where(Alert.category == category)
    if severity:
        stmt = stmt.where(Alert.severity == severity)
    if alert_status:
        stmt = stmt.where(Alert.status == alert_status)
    items, total = paginate(db, stmt, Alert, params, ("title", "message", "region"), "triggered_at")
    return Page.create([AlertOut.model_validate(a) for a in items], total, params.page, params.page_size)


@router.post("/evaluate", response_model=list[AlertOut])
def evaluate(db: Session = Depends(get_db), user: User = Depends(require_manager)) -> list[Alert]:
    created = alert_service.evaluate_and_generate(db, user.organization_id)
    audit_service.log(db, actor=user, action="evaluate_alerts", detail={"created": len(created)})
    return created


@router.post("", response_model=AlertOut, status_code=status.HTTP_201_CREATED)
def create_alert(payload: AlertCreate, db: Session = Depends(get_db), user: User = Depends(require_manager)) -> Alert:
    alert = Alert(
        **payload.model_dump(),
        organization_id=user.organization_id,
        triggered_at=datetime.now(timezone.utc),
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    audit_service.log(db, actor=user, action="create_alert", entity_type="alert", entity_id=alert.id)
    return alert


@router.get("/{alert_id}", response_model=AlertOut)
def get_alert(alert_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> Alert:
    alert = db.get(Alert, alert_id)
    if not alert:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Alert not found")
    return alert


@router.post("/{alert_id}/acknowledge", response_model=AlertOut)
def acknowledge_alert(
    alert_id: int, payload: AlertActionRequest | None = None, db: Session = Depends(get_db),
    user: User = Depends(require_manager),
) -> Alert:
    alert = db.get(Alert, alert_id)
    if not alert:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Alert not found")
    notes = payload.notes if payload else None
    return alert_service.acknowledge(db, alert, user.id, notes)


@router.post("/{alert_id}/resolve", response_model=AlertOut)
def resolve_alert(
    alert_id: int, payload: AlertActionRequest | None = None, db: Session = Depends(get_db),
    user: User = Depends(require_manager),
) -> Alert:
    alert = db.get(Alert, alert_id)
    if not alert:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Alert not found")
    notes = payload.notes if payload else None
    return alert_service.resolve(db, alert, user.id, notes)


@router.post("/{alert_id}/actions", response_model=AlertOut)
def add_action(
    alert_id: int, payload: AlertActionRequest, db: Session = Depends(get_db),
    user: User = Depends(require_manager),
) -> Alert:
    alert = db.get(Alert, alert_id)
    if not alert:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Alert not found")
    return alert_service.add_action(db, alert, user.id, payload.action, payload.notes)
