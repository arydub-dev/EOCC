"""Schemas for the Data Integration Center."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models import enums


class DataSourceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    source_type: enums.DataSourceType
    status: enums.DataSourceStatus
    endpoint: str | None = None
    description: str | None = None
    auth_type: str | None = None
    # Whether a secret/credential is configured — the secret itself is never returned.
    has_secret: bool = False
    last_sync_at: datetime | None = None
    sync_interval_minutes: int
    records_synced: int
    health_score: float
    enabled: bool


class DataSourceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    source_type: enums.DataSourceType
    endpoint: str | None = Field(default=None, max_length=512)
    description: str | None = Field(default=None, max_length=2000)
    sync_interval_minutes: int = Field(default=15, ge=1, le=10080)
    auth_type: str | None = Field(default=None, max_length=40)
    # Plaintext secret accepted on input only; stored encrypted, never serialized.
    secret: str | None = Field(default=None, max_length=4000)


class ImportJobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    data_source_id: int | None = None
    source_type: enums.DataSourceType
    target_entity: str
    status: enums.ImportJobStatus
    filename: str | None = None
    records_total: int
    records_processed: int
    records_failed: int
    duration_ms: int
    errors: list[dict] | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
    created_at: datetime


class IntegrationOverview(BaseModel):
    connected_systems: int
    healthy: int
    degraded: int
    offline: int
    total_records_synced: int
    avg_health_score: float
    last_sync_at: datetime | None = None
    sources: list[DataSourceOut]


class PipelineMonitor(BaseModel):
    total_jobs: int
    completed: int
    failed: int
    partial: int
    records_processed: int
    records_failed: int
    avg_duration_ms: float
    pipeline_health: float
    recent_jobs: list[ImportJobOut]


class CSVImportRequest(BaseModel):
    target_entity: str
    content: str
    filename: str | None = None
