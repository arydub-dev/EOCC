"""Fine-grained, role-based permission registry.

Authorization is permission-first: endpoints declare the *permission* they
require, and roles are mapped to permission sets here. This keeps least-privilege
explicit and makes it trivial to audit who can do what. The frontend may read a
user's permissions to shape the UI, but the server is the only enforcement point.
"""
from __future__ import annotations

from app.models.enums import UserRole


class Permission:
    # Incidents
    INCIDENT_READ = "Incident.Read"
    INCIDENT_UPDATE = "Incident.Update"
    INCIDENT_MANAGE = "Incident.Manage"
    # Hospitals / Shelters / Resources / Utilities
    HOSPITAL_READ = "Hospital.Read"
    HOSPITAL_MANAGE = "Hospital.Manage"
    SHELTER_READ = "Shelter.Read"
    SHELTER_MANAGE = "Shelter.Manage"
    RESOURCE_READ = "Resource.Read"
    RESOURCE_MANAGE = "Resource.Manage"
    RESOURCE_ASSIGN = "Resource.Assign"
    UTILITY_READ = "Utility.Read"
    UTILITY_MANAGE = "Utility.Manage"
    # Intelligence
    RISK_READ = "Risk.Read"
    RISK_RUN = "Risk.Run"
    ALERT_READ = "Alert.Read"
    ALERT_MANAGE = "Alert.Manage"
    SIMULATION_READ = "Simulation.Read"
    SIMULATION_RUN = "Simulation.Run"
    COPILOT_USE = "Copilot.Use"
    # Reporting / integration
    REPORT_READ = "Report.Read"
    REPORT_EXPORT = "Report.Export"
    INTEGRATION_READ = "Integration.Read"
    INTEGRATION_CONFIGURE = "Integration.Configure"
    INTEGRATION_IMPORT = "Integration.Import"
    # Administration / security
    USER_MANAGE = "User.Manage"
    ROLE_MANAGE = "Role.Manage"
    AUDIT_VIEW = "Audit.View"
    SECURITY_VIEW = "Security.View"
    SECURITY_MANAGE = "Security.Manage"


ALL_PERMISSIONS: list[str] = [
    v for k, v in vars(Permission).items() if not k.startswith("_") and isinstance(v, str)
]

# Read-only set, shared by every authenticated role (incl. Viewer & Executive).
_READ: set[str] = {
    Permission.INCIDENT_READ,
    Permission.HOSPITAL_READ,
    Permission.SHELTER_READ,
    Permission.RESOURCE_READ,
    Permission.UTILITY_READ,
    Permission.RISK_READ,
    Permission.ALERT_READ,
    Permission.SIMULATION_READ,
    Permission.REPORT_READ,
    Permission.INTEGRATION_READ,
}

_ANALYST: set[str] = _READ | {
    Permission.INCIDENT_UPDATE,
    Permission.RISK_RUN,
    Permission.SIMULATION_RUN,
    Permission.COPILOT_USE,
    Permission.REPORT_EXPORT,
}

_MANAGER: set[str] = _ANALYST | {
    Permission.INCIDENT_MANAGE,
    Permission.HOSPITAL_MANAGE,
    Permission.SHELTER_MANAGE,
    Permission.RESOURCE_MANAGE,
    Permission.RESOURCE_ASSIGN,
    Permission.UTILITY_MANAGE,
    Permission.ALERT_MANAGE,
    Permission.INTEGRATION_IMPORT,
}

_EXECUTIVE: set[str] = _READ | {
    Permission.COPILOT_USE,
    Permission.REPORT_EXPORT,
    Permission.SECURITY_VIEW,
}

ROLE_PERMISSIONS: dict[UserRole, set[str]] = {
    UserRole.VIEWER: set(_READ),
    UserRole.EXECUTIVE: _EXECUTIVE,
    UserRole.ANALYST: _ANALYST,
    UserRole.EMERGENCY_MANAGER: _MANAGER,
    # Admin holds every permission, including configuration and security.
    UserRole.ADMIN: set(ALL_PERMISSIONS),
}


def permissions_for(role: UserRole) -> set[str]:
    return ROLE_PERMISSIONS.get(role, set())


def has_permission(role: UserRole, permission: str) -> bool:
    return permission in permissions_for(role)
