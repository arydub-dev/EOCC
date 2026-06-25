"""Schemas for incidents, hospitals, shelters, resources and utility outages."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models import enums


# ──────────────────────────── Incidents ────────────────────────────
class IncidentEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    event_type: str
    description: str
    severity_delta: float
    occurred_at: datetime
    payload: dict | None = None


class IncidentBase(BaseModel):
    name: str
    incident_type: enums.IncidentType
    status: enums.IncidentStatus = enums.IncidentStatus.ACTIVE
    description: str | None = None
    region: str | None = None
    latitude: float
    longitude: float
    radius_km: float = 5.0
    severity: int = Field(3, ge=1, le=5)
    population_impacted: int = 0
    started_at: datetime
    estimated_duration_hours: float | None = None


class IncidentCreate(IncidentBase):
    pass


class IncidentUpdate(BaseModel):
    name: str | None = None
    status: enums.IncidentStatus | None = None
    description: str | None = None
    region: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    radius_km: float | None = None
    severity: int | None = Field(default=None, ge=1, le=5)
    population_impacted: int | None = None
    estimated_duration_hours: float | None = None
    # Optimistic concurrency: pass the version you last read to detect conflicts.
    expected_version: int | None = None


class IncidentOut(IncidentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    severity_score: float
    version: int = 1
    resolved_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class IncidentDetail(IncidentOut):
    events: list[IncidentEventOut] = []


# ──────────────────────────── Hospitals ────────────────────────────
class HospitalBase(BaseModel):
    name: str
    region: str | None = None
    latitude: float
    longitude: float
    total_beds: int = 0
    occupied_beds: int = 0
    icu_beds: int = 0
    icu_occupied: int = 0
    er_capacity: int = 0
    er_patients: int = 0
    staff_on_duty: int = 0
    staff_required: int = 0
    ventilators_total: int = 0
    ventilators_in_use: int = 0
    accepts_diversions: bool = True


class HospitalCreate(HospitalBase):
    pass


class HospitalUpdate(BaseModel):
    occupied_beds: int | None = None
    icu_occupied: int | None = None
    er_patients: int | None = None
    staff_on_duty: int | None = None
    ventilators_in_use: int | None = None
    accepts_diversions: bool | None = None


class HospitalOut(HospitalBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: enums.HospitalStatus
    stress_score: float
    bed_occupancy_pct: float = 0.0
    icu_occupancy_pct: float = 0.0
    er_load_pct: float = 0.0
    updated_at: datetime


# ──────────────────────────── Shelters ────────────────────────────
class ShelterBase(BaseModel):
    name: str
    region: str | None = None
    latitude: float
    longitude: float
    capacity: int = 0
    occupancy: int = 0
    food_supply_days: float = 0.0
    water_supply_days: float = 0.0
    medical_kits: int = 0
    medical_staff: int = 0


class ShelterCreate(ShelterBase):
    pass


class ShelterUpdate(BaseModel):
    occupancy: int | None = None
    food_supply_days: float | None = None
    water_supply_days: float | None = None
    medical_kits: int | None = None
    medical_staff: int | None = None
    status: enums.ShelterStatus | None = None


class ShelterOut(ShelterBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: enums.ShelterStatus
    utilization_score: float
    occupancy_pct: float = 0.0
    updated_at: datetime


# ──────────────────────────── Resources ────────────────────────────
class ResourceBase(BaseModel):
    name: str
    resource_type: enums.ResourceType
    status: enums.ResourceStatus = enums.ResourceStatus.AVAILABLE
    region: str | None = None
    home_base: str | None = None
    latitude: float
    longitude: float
    capacity: float = 0.0
    capacity_unit: str | None = None
    quantity_available: float = 0.0
    readiness: float = 100.0


class ResourceCreate(ResourceBase):
    pass


class ResourceUpdate(BaseModel):
    status: enums.ResourceStatus | None = None
    latitude: float | None = None
    longitude: float | None = None
    quantity_available: float | None = None
    readiness: float | None = None


class ResourceOut(ResourceBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class ResourceAssignmentCreate(BaseModel):
    resource_id: int
    incident_id: int | None = None
    quantity: float = 1.0
    role: str | None = None
    notes: str | None = None


class ResourceAssignmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    resource_id: int
    incident_id: int | None = None
    quantity: float
    role: str | None = None
    notes: str | None = None
    assigned_at: datetime
    released_at: datetime | None = None
    active: bool


# ──────────────────────────── Utility Outages ────────────────────────────
class UtilityOutageBase(BaseModel):
    utility_type: enums.UtilityType
    status: enums.UtilityOutageStatus = enums.UtilityOutageStatus.REPORTED
    region: str | None = None
    latitude: float
    longitude: float
    customers_affected: int = 0
    description: str | None = None
    started_at: datetime
    estimated_restoration: datetime | None = None
    incident_id: int | None = None


class UtilityOutageCreate(UtilityOutageBase):
    pass


class UtilityOutageUpdate(BaseModel):
    status: enums.UtilityOutageStatus | None = None
    customers_affected: int | None = None
    estimated_restoration: datetime | None = None


class UtilityOutageOut(UtilityOutageBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
