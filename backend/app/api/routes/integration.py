"""Data Integration Center endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_permission
from app.core.permissions import Permission
from app.core.security import encrypt_value
from app.database import get_db
from app.models import DataSource, ImportJob, User
from app.schemas.integration import (
    CSVImportRequest,
    DataSourceCreate,
    DataSourceOut,
    ImportJobOut,
    IntegrationOverview,
    PipelineMonitor,
)
from app.services import audit_service, file_security, integration_service
from app.services.file_security import FileSecurityError

router = APIRouter(prefix="/integration", tags=["Data Integration"])


@router.get("/overview", response_model=IntegrationOverview)
def overview(
    db: Session = Depends(get_db), _: User = Depends(get_current_user)
) -> IntegrationOverview:
    return integration_service.overview(db)


@router.get("/sources", response_model=list[DataSourceOut])
def list_sources(
    db: Session = Depends(get_db), _: User = Depends(get_current_user)
) -> list[DataSource]:
    return list(db.scalars(select(DataSource).order_by(DataSource.name)).all())


@router.post("/sources", response_model=DataSourceOut, status_code=status.HTTP_201_CREATED)
def create_source(
    payload: DataSourceCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission(Permission.INTEGRATION_CONFIGURE)),
) -> DataSource:
    data = payload.model_dump()
    secret = data.pop("secret", None)
    source = DataSource(
        **data,
        organization_id=user.organization_id,
        secret_encrypted=encrypt_value(secret),
    )
    db.add(source)
    db.commit()
    db.refresh(source)
    audit_service.log(
        db,
        actor=user,
        action="create_data_source",
        category="configuration",
        entity_type="data_source",
        entity_id=source.id,
        new_value={
            "name": source.name,
            "type": source.source_type.value,
            "has_secret": source.has_secret,
        },
    )
    return source


@router.get("/pipeline", response_model=PipelineMonitor)
def pipeline(db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> PipelineMonitor:
    return integration_service.pipeline_monitor(db)


@router.get("/jobs", response_model=list[ImportJobOut])
def list_jobs(
    db: Session = Depends(get_db), _: User = Depends(get_current_user)
) -> list[ImportJob]:
    return list(
        db.scalars(select(ImportJob).order_by(ImportJob.created_at.desc()).limit(100)).all()
    )


@router.post("/import/csv", response_model=ImportJobOut)
def import_csv(
    payload: CSVImportRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission(Permission.INTEGRATION_IMPORT)),
) -> ImportJob:
    if not file_security.allowed_target(payload.target_entity):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Unsupported import target.")
    try:
        text = file_security.validate_csv_upload(payload.filename, payload.content, "text/csv")
    except FileSecurityError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc
    job = integration_service.run_csv_import(
        db, payload.target_entity, text, payload.filename, org_id=user.organization_id
    )
    audit_service.log(
        db,
        actor=user,
        action="import_csv",
        category="data_import",
        entity_type="import_job",
        entity_id=job.id,
        detail={
            "target": payload.target_entity,
            "status": job.status.value,
            "rows": job.records_processed,
        },
    )
    return job


@router.post("/import/excel", response_model=ImportJobOut)
async def import_excel(
    target_entity: str = Form(..., max_length=80),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(require_permission(Permission.INTEGRATION_IMPORT)),
) -> ImportJob:
    if not file_security.allowed_target(target_entity):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Unsupported import target.")
    content = await file.read()
    try:
        content = file_security.validate_excel_upload(file.filename, content, file.content_type)
    except FileSecurityError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc
    job = integration_service.run_excel_import(
        db, target_entity, content, file.filename, org_id=user.organization_id
    )
    audit_service.log(
        db,
        actor=user,
        action="import_excel",
        category="data_import",
        entity_type="import_job",
        entity_id=job.id,
        detail={"target": target_entity, "status": job.status.value, "rows": job.records_processed},
    )
    return job
