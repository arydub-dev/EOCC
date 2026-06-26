"""Enumerations used across EOCC domain models."""

from __future__ import annotations

import enum


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    EMERGENCY_MANAGER = "emergency_manager"
    ANALYST = "analyst"
    EXECUTIVE = "executive"
    VIEWER = "viewer"


class DataClassification(str, enum.Enum):
    """Data sensitivity classification for handling rules."""

    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


class Industry(str, enum.Enum):
    GOVERNMENT = "government"
    EMERGENCY_SERVICES = "emergency_services"
    HEALTHCARE = "healthcare"
    UTILITIES = "utilities"
    DISASTER_RESPONSE = "disaster_response"
    NGO = "ngo"
    CRITICAL_INFRASTRUCTURE = "critical_infrastructure"
    OTHER = "other"


class WorkspaceMode(str, enum.Enum):
    DEMO = "demo"
    CONNECTED = "connected"


class Plan(str, enum.Enum):
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class DataOrigin(str, enum.Enum):
    DEMO = "demo"
    MANUAL = "manual"
    CSV = "csv"
    EXCEL = "excel"
    API = "api"
    GIS = "gis"
    WEATHER_FEED = "weather_feed"
    HOSPITAL_SYSTEM = "hospital_system"


class IncidentType(str, enum.Enum):
    WILDFIRE = "wildfire"
    FLOOD = "flood"
    HURRICANE = "hurricane"
    EARTHQUAKE = "earthquake"
    INDUSTRIAL_ACCIDENT = "industrial_accident"
    DISEASE_OUTBREAK = "disease_outbreak"
    INFRASTRUCTURE_FAILURE = "infrastructure_failure"
    SEVERE_STORM = "severe_storm"


class IncidentStatus(str, enum.Enum):
    MONITORING = "monitoring"
    ACTIVE = "active"
    ESCALATING = "escalating"
    CONTAINED = "contained"
    RESOLVED = "resolved"


class HospitalStatus(str, enum.Enum):
    NORMAL = "normal"
    ELEVATED = "elevated"
    STRAINED = "strained"
    CRITICAL = "critical"
    DIVERSION = "diversion"


class ShelterStatus(str, enum.Enum):
    OPEN = "open"
    NEAR_CAPACITY = "near_capacity"
    FULL = "full"
    CLOSED = "closed"


class ResourceType(str, enum.Enum):
    AMBULANCE = "ambulance"
    FIRE_TRUCK = "fire_truck"
    MEDICAL_TEAM = "medical_team"
    RESCUE_TEAM = "rescue_team"
    HELICOPTER = "helicopter"
    FOOD_SUPPLY = "food_supply"
    WATER_SUPPLY = "water_supply"
    FUEL_SUPPLY = "fuel_supply"
    GENERATOR = "generator"


class ResourceStatus(str, enum.Enum):
    AVAILABLE = "available"
    ASSIGNED = "assigned"
    EN_ROUTE = "en_route"
    ON_SCENE = "on_scene"
    MAINTENANCE = "maintenance"
    DEPLETED = "depleted"


class UtilityType(str, enum.Enum):
    POWER = "power"
    WATER = "water"
    GAS = "gas"
    TELECOM = "telecom"
    INTERNET = "internet"


class UtilityOutageStatus(str, enum.Enum):
    REPORTED = "reported"
    INVESTIGATING = "investigating"
    REPAIRING = "repairing"
    RESTORED = "restored"


class RiskCategory(str, enum.Enum):
    POPULATION = "population"
    INFRASTRUCTURE = "infrastructure"
    HEALTHCARE = "healthcare"
    RESOURCE = "resource"
    ENVIRONMENTAL = "environmental"


class RiskSeverity(str, enum.Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    SEVERE = "severe"
    CRITICAL = "critical"


class AlertCategory(str, enum.Enum):
    HOSPITAL_OVERLOAD = "hospital_overload"
    SHELTER_CAPACITY = "shelter_capacity"
    RESOURCE_SHORTAGE = "resource_shortage"
    INCIDENT_ESCALATION = "incident_escalation"
    UTILITY_FAILURE = "utility_failure"
    ENVIRONMENTAL = "environmental"


class AlertSeverity(str, enum.Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class AlertStatus(str, enum.Enum):
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


class SimulationType(str, enum.Enum):
    HURRICANE_PATH = "hurricane_path"
    FLOOD_EXPANSION = "flood_expansion"
    SHELTER_CLOSURE = "shelter_closure"
    HOSPITAL_OUTAGE = "hospital_outage"
    RESOURCE_DEPLETION = "resource_depletion"
    UTILITY_GRID_FAILURE = "utility_grid_failure"


class SimulationStatus(str, enum.Enum):
    DRAFT = "draft"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class DataSourceType(str, enum.Enum):
    WEATHER_API = "weather_api"
    GIS_FEED = "gis_feed"
    HOSPITAL_SYSTEM = "hospital_system"
    EMERGENCY_CALL_SYSTEM = "emergency_call_system"
    RESOURCE_SYSTEM = "resource_system"
    CSV_IMPORT = "csv_import"
    EXCEL_IMPORT = "excel_import"


class DataSourceStatus(str, enum.Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    OFFLINE = "offline"
    DISCONNECTED = "disconnected"


class ImportJobStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"
