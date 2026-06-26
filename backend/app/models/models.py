"""Core ORM models for the EOCC platform.

All enum columns use non-native string enums so the schema stays portable
across PostgreSQL (production) and SQLite (lightweight local dev).
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy import (
    Enum as SAEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models import enums


def _enum(py_enum: type, length: int = 40):
    return SAEnum(py_enum, native_enum=False, length=length, validate_strings=True)


class Organization(Base):
    """Top-level tenant. Every operational entity belongs to an organization."""

    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    industry: Mapped[enums.Industry] = mapped_column(
        _enum(enums.Industry), default=enums.Industry.OTHER, nullable=False
    )
    mode: Mapped[enums.WorkspaceMode] = mapped_column(
        _enum(enums.WorkspaceMode), default=enums.WorkspaceMode.DEMO, nullable=False
    )
    plan: Mapped[enums.Plan] = mapped_column(
        _enum(enums.Plan), default=enums.Plan.STARTER, nullable=False
    )
    is_demo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    provisioned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    region: Mapped[str | None] = mapped_column(String(120))

    users: Mapped[list[User]] = relationship(back_populates="org")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[enums.UserRole] = mapped_column(
        _enum(enums.UserRole), default=enums.UserRole.ANALYST, nullable=False
    )
    organization_id: Mapped[int | None] = mapped_column(
        ForeignKey("organizations.id", ondelete="SET NULL"), index=True
    )
    organization: Mapped[str | None] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    email_verification_token: Mapped[str | None] = mapped_column(String(128))
    password_reset_token: Mapped[str | None] = mapped_column(String(128))
    password_reset_expires: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    password_changed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_login_ip: Mapped[str | None] = mapped_column(String(64))

    # Brute-force protection
    failed_login_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_failed_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # MFA (TOTP) — secret stored encrypted at rest
    mfa_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    mfa_secret_encrypted: Mapped[str | None] = mapped_column(Text)

    org: Mapped[Organization | None] = relationship(back_populates="users")
    sessions: Mapped[list[UserSession]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    assignments_created: Mapped[list[ResourceAssignment]] = relationship(
        back_populates="assigned_by", foreign_keys="ResourceAssignment.assigned_by_id"
    )
    simulations: Mapped[list[Simulation]] = relationship(back_populates="created_by")
    audit_logs: Mapped[list[AuditLog]] = relationship(back_populates="actor")


class UserSession(Base):
    """Server-side refresh-token session for rotation, revocation, and tracking.

    Only the *hash* of the refresh token is stored. Sessions form a rotation
    ``family``; reuse of a rotated (already-replaced) token invalidates the whole
    family, which is the standard refresh-token-theft detection pattern.
    """

    __tablename__ = "user_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    organization_id: Mapped[int | None] = mapped_column(Integer, index=True)
    family_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    refresh_token_hash: Mapped[str] = mapped_column(String(128), index=True, nullable=False)

    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    revoked_reason: Mapped[str | None] = mapped_column(String(120))
    replaced_by_id: Mapped[int | None] = mapped_column(Integer)

    ip_address: Mapped[str | None] = mapped_column(String(64))
    user_agent: Mapped[str | None] = mapped_column(String(400))
    device_label: Mapped[str | None] = mapped_column(String(160))

    user: Mapped[User] = relationship(back_populates="sessions")


class LoginAttempt(Base):
    """Append-only record of authentication attempts for the Security Center."""

    __tablename__ = "login_attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    user_id: Mapped[int | None] = mapped_column(Integer, index=True)
    organization_id: Mapped[int | None] = mapped_column(Integer, index=True)
    successful: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    reason: Mapped[str | None] = mapped_column(String(120))
    ip_address: Mapped[str | None] = mapped_column(String(64))
    user_agent: Mapped[str | None] = mapped_column(String(400))


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    organization_id: Mapped[int | None] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True
    )
    data_origin: Mapped[enums.DataOrigin] = mapped_column(
        _enum(enums.DataOrigin), default=enums.DataOrigin.MANUAL, nullable=False
    )
    data_classification: Mapped[enums.DataClassification] = mapped_column(
        _enum(enums.DataClassification),
        default=enums.DataClassification.CONFIDENTIAL,
        nullable=False,
    )
    # Optimistic concurrency control for critical updates.
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    # Soft delete
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    incident_type: Mapped[enums.IncidentType] = mapped_column(
        _enum(enums.IncidentType), nullable=False, index=True
    )
    status: Mapped[enums.IncidentStatus] = mapped_column(
        _enum(enums.IncidentStatus), default=enums.IncidentStatus.ACTIVE, nullable=False, index=True
    )
    description: Mapped[str | None] = mapped_column(Text)
    region: Mapped[str | None] = mapped_column(String(120), index=True)

    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    radius_km: Mapped[float] = mapped_column(Float, default=5.0, nullable=False)

    severity: Mapped[int] = mapped_column(Integer, default=3, nullable=False)  # 1-5 base severity
    severity_score: Mapped[float] = mapped_column(
        Float, default=0.0, nullable=False
    )  # computed 0-100
    population_impacted: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    estimated_duration_hours: Mapped[float | None] = mapped_column(Float)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    events: Mapped[list[IncidentEvent]] = relationship(
        back_populates="incident",
        cascade="all, delete-orphan",
        order_by="IncidentEvent.occurred_at",
    )
    alerts: Mapped[list[Alert]] = relationship(back_populates="incident")
    assignments: Mapped[list[ResourceAssignment]] = relationship(back_populates="incident")
    risk_assessments: Mapped[list[RiskAssessment]] = relationship(back_populates="incident")

    # Enable optimistic locking: concurrent updates to the same incident raise
    # StaleDataError instead of silently overwriting one another.
    __mapper_args__ = {"version_id_col": version}


class IncidentEvent(Base):
    __tablename__ = "incident_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    incident_id: Mapped[int] = mapped_column(
        ForeignKey("incidents.id", ondelete="CASCADE"), index=True
    )
    event_type: Mapped[str] = mapped_column(String(80), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    severity_delta: Mapped[float] = mapped_column(Float, default=0.0)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    payload: Mapped[dict | None] = mapped_column(JSON)

    incident: Mapped[Incident] = relationship(back_populates="events")


class Hospital(Base):
    __tablename__ = "hospitals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    organization_id: Mapped[int | None] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True
    )
    data_origin: Mapped[enums.DataOrigin] = mapped_column(
        _enum(enums.DataOrigin), default=enums.DataOrigin.MANUAL, nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    region: Mapped[str | None] = mapped_column(String(120), index=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)

    total_beds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    occupied_beds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    icu_beds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    icu_occupied: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    er_capacity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    er_patients: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    staff_on_duty: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    staff_required: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    ventilators_total: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    ventilators_in_use: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    status: Mapped[enums.HospitalStatus] = mapped_column(
        _enum(enums.HospitalStatus), default=enums.HospitalStatus.NORMAL, nullable=False, index=True
    )
    stress_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    accepts_diversions: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class Shelter(Base):
    __tablename__ = "shelters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    organization_id: Mapped[int | None] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True
    )
    data_origin: Mapped[enums.DataOrigin] = mapped_column(
        _enum(enums.DataOrigin), default=enums.DataOrigin.MANUAL, nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    region: Mapped[str | None] = mapped_column(String(120), index=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)

    capacity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    occupancy: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    food_supply_days: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    water_supply_days: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    medical_kits: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    medical_staff: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    status: Mapped[enums.ShelterStatus] = mapped_column(
        _enum(enums.ShelterStatus), default=enums.ShelterStatus.OPEN, nullable=False, index=True
    )
    utilization_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)


class Resource(Base):
    __tablename__ = "resources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    organization_id: Mapped[int | None] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True
    )
    data_origin: Mapped[enums.DataOrigin] = mapped_column(
        _enum(enums.DataOrigin), default=enums.DataOrigin.MANUAL, nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    resource_type: Mapped[enums.ResourceType] = mapped_column(
        _enum(enums.ResourceType), nullable=False, index=True
    )
    status: Mapped[enums.ResourceStatus] = mapped_column(
        _enum(enums.ResourceStatus),
        default=enums.ResourceStatus.AVAILABLE,
        nullable=False,
        index=True,
    )
    region: Mapped[str | None] = mapped_column(String(120), index=True)
    home_base: Mapped[str | None] = mapped_column(String(255))

    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)

    capacity: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    capacity_unit: Mapped[str | None] = mapped_column(String(40))
    quantity_available: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    readiness: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)  # 0-100

    assignments: Mapped[list[ResourceAssignment]] = relationship(back_populates="resource")


class ResourceAssignment(Base):
    __tablename__ = "resource_assignments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    organization_id: Mapped[int | None] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True
    )
    resource_id: Mapped[int] = mapped_column(
        ForeignKey("resources.id", ondelete="CASCADE"), index=True
    )
    incident_id: Mapped[int | None] = mapped_column(
        ForeignKey("incidents.id", ondelete="SET NULL"), index=True
    )
    assigned_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))

    quantity: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    role: Mapped[str | None] = mapped_column(String(120))
    notes: Mapped[str | None] = mapped_column(Text)
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    released_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    resource: Mapped[Resource] = relationship(back_populates="assignments")
    incident: Mapped[Incident | None] = relationship(back_populates="assignments")
    assigned_by: Mapped[User | None] = relationship(
        back_populates="assignments_created", foreign_keys=[assigned_by_id]
    )


class UtilityOutage(Base):
    __tablename__ = "utility_outages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    organization_id: Mapped[int | None] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True
    )
    data_origin: Mapped[enums.DataOrigin] = mapped_column(
        _enum(enums.DataOrigin), default=enums.DataOrigin.MANUAL, nullable=False
    )
    utility_type: Mapped[enums.UtilityType] = mapped_column(
        _enum(enums.UtilityType), nullable=False, index=True
    )
    status: Mapped[enums.UtilityOutageStatus] = mapped_column(
        _enum(enums.UtilityOutageStatus),
        default=enums.UtilityOutageStatus.REPORTED,
        nullable=False,
        index=True,
    )
    region: Mapped[str | None] = mapped_column(String(120), index=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    customers_affected: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    estimated_restoration: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    incident_id: Mapped[int | None] = mapped_column(ForeignKey("incidents.id", ondelete="SET NULL"))


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    organization_id: Mapped[int | None] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True
    )
    category: Mapped[enums.RiskCategory] = mapped_column(
        _enum(enums.RiskCategory), nullable=False, index=True
    )
    severity: Mapped[enums.RiskSeverity] = mapped_column(
        _enum(enums.RiskSeverity), nullable=False, index=True
    )
    score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)  # 0-100
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    recommendations: Mapped[list | None] = mapped_column(JSON)
    factors: Mapped[dict | None] = mapped_column(JSON)
    region: Mapped[str | None] = mapped_column(String(120), index=True)
    incident_id: Mapped[int | None] = mapped_column(ForeignKey("incidents.id", ondelete="SET NULL"))
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    incident: Mapped[Incident | None] = relationship(back_populates="risk_assessments")


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    organization_id: Mapped[int | None] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True
    )
    data_origin: Mapped[enums.DataOrigin] = mapped_column(
        _enum(enums.DataOrigin), default=enums.DataOrigin.MANUAL, nullable=False
    )
    category: Mapped[enums.AlertCategory] = mapped_column(
        _enum(enums.AlertCategory), nullable=False, index=True
    )
    severity: Mapped[enums.AlertSeverity] = mapped_column(
        _enum(enums.AlertSeverity), nullable=False, index=True
    )
    status: Mapped[enums.AlertStatus] = mapped_column(
        _enum(enums.AlertStatus), default=enums.AlertStatus.OPEN, nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    region: Mapped[str | None] = mapped_column(String(120), index=True)
    source: Mapped[str | None] = mapped_column(String(120))

    incident_id: Mapped[int | None] = mapped_column(ForeignKey("incidents.id", ondelete="SET NULL"))
    hospital_id: Mapped[int | None] = mapped_column(ForeignKey("hospitals.id", ondelete="SET NULL"))
    shelter_id: Mapped[int | None] = mapped_column(ForeignKey("shelters.id", ondelete="SET NULL"))

    acknowledged_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL")
    )
    acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    response_actions: Mapped[list | None] = mapped_column(JSON)
    triggered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )

    incident: Mapped[Incident | None] = relationship(back_populates="alerts")


class Simulation(Base):
    __tablename__ = "simulations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    organization_id: Mapped[int | None] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    simulation_type: Mapped[enums.SimulationType] = mapped_column(
        _enum(enums.SimulationType), nullable=False, index=True
    )
    status: Mapped[enums.SimulationStatus] = mapped_column(
        _enum(enums.SimulationStatus), default=enums.SimulationStatus.COMPLETED, nullable=False
    )
    parameters: Mapped[dict] = mapped_column(JSON, nullable=False)
    results: Mapped[dict | None] = mapped_column(JSON)
    recommendations: Mapped[list | None] = mapped_column(JSON)
    operational_risk: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))

    created_by: Mapped[User | None] = relationship(back_populates="simulations")


class AIReport(Base):
    __tablename__ = "ai_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    organization_id: Mapped[int | None] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True
    )
    report_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    prompt: Mapped[str | None] = mapped_column(Text)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    structured: Mapped[dict | None] = mapped_column(JSON)
    grounding: Mapped[dict | None] = mapped_column(JSON)
    engine: Mapped[str] = mapped_column(String(40), default="deterministic", nullable=False)
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))


class DataSource(Base):
    __tablename__ = "data_sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    organization_id: Mapped[int | None] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type: Mapped[enums.DataSourceType] = mapped_column(
        _enum(enums.DataSourceType), nullable=False, index=True
    )
    status: Mapped[enums.DataSourceStatus] = mapped_column(
        _enum(enums.DataSourceStatus), default=enums.DataSourceStatus.HEALTHY, nullable=False
    )
    endpoint: Mapped[str | None] = mapped_column(String(512))
    description: Mapped[str | None] = mapped_column(Text)
    # Connector credentials are encrypted at rest (Fernet) and never serialized.
    auth_type: Mapped[str | None] = mapped_column(String(40))
    secret_encrypted: Mapped[str | None] = mapped_column(Text)
    last_sync_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    sync_interval_minutes: Mapped[int] = mapped_column(Integer, default=15, nullable=False)
    records_synced: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    health_score: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    import_jobs: Mapped[list[ImportJob]] = relationship(back_populates="data_source")

    @property
    def has_secret(self) -> bool:
        return bool(self.secret_encrypted)


class ImportJob(Base):
    __tablename__ = "import_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    organization_id: Mapped[int | None] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True
    )
    data_source_id: Mapped[int | None] = mapped_column(
        ForeignKey("data_sources.id", ondelete="SET NULL")
    )
    source_type: Mapped[enums.DataSourceType] = mapped_column(
        _enum(enums.DataSourceType), nullable=False
    )
    target_entity: Mapped[str] = mapped_column(String(80), nullable=False)
    status: Mapped[enums.ImportJobStatus] = mapped_column(
        _enum(enums.ImportJobStatus),
        default=enums.ImportJobStatus.PENDING,
        nullable=False,
        index=True,
    )
    filename: Mapped[str | None] = mapped_column(String(512))
    records_total: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    records_processed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    records_failed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    duration_ms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    errors: Mapped[list | None] = mapped_column(JSON)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    data_source: Mapped[DataSource | None] = relationship(back_populates="import_jobs")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    organization_id: Mapped[int | None] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True
    )
    actor_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    actor_email: Mapped[str | None] = mapped_column(String(255))
    action: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(40), default="general", nullable=False, index=True)
    entity_type: Mapped[str | None] = mapped_column(String(80), index=True)
    entity_id: Mapped[str | None] = mapped_column(String(80))
    detail: Mapped[dict | None] = mapped_column(JSON)
    old_value: Mapped[dict | None] = mapped_column(JSON)
    new_value: Mapped[dict | None] = mapped_column(JSON)
    ip_address: Mapped[str | None] = mapped_column(String(64))
    user_agent: Mapped[str | None] = mapped_column(String(400))
    correlation_id: Mapped[str | None] = mapped_column(String(64), index=True)

    actor: Mapped[User | None] = relationship(back_populates="audit_logs")


class AppSetting(Base):
    __tablename__ = "app_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    key: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    value: Mapped[dict | None] = mapped_column(JSON)
    description: Mapped[str | None] = mapped_column(Text)
