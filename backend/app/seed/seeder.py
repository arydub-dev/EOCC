"""Initial database seeding.

Creates a demo organization with four role-based demo users and provisions a
full synthetic operational workspace for it (via the provisioning service), so
the platform feels alive immediately after deployment.
"""
from __future__ import annotations

import random

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import settings
from app.core.security import hash_password
from app.models import Organization, User, enums
from app.services import provisioning

RNG = random.Random(2024)

DEMO_ORG_SLUG = "metro-regional-eoc"

DEMO_USERS = [
    ("admin@eocc.gov", "Alex Rivera", enums.UserRole.ADMIN, "admin123"),
    ("manager@eocc.gov", "Morgan Chen", enums.UserRole.EMERGENCY_MANAGER, "manager123"),
    ("analyst@eocc.gov", "Jordan Patel", enums.UserRole.ANALYST, "analyst123"),
    ("exec@eocc.gov", "Taylor Brooks", enums.UserRole.EXECUTIVE, "exec123"),
]


def seed_database(db: Session, force: bool = False) -> dict:
    """Seed a demo organization + users + workspace if none exists."""
    existing = db.scalar(select(Organization).where(Organization.slug == DEMO_ORG_SLUG))
    if existing and not force:
        return {"seeded": False, "reason": "demo organization already present"}

    org = Organization(
        name="Metro Regional Emergency Operations Center",
        slug=DEMO_ORG_SLUG,
        industry=enums.Industry.GOVERNMENT,
        mode=enums.WorkspaceMode.DEMO,
        plan=enums.Plan.ENTERPRISE,
        is_demo=True,
        region="Gulf Coast",
    )
    db.add(org)
    db.flush()

    for email, name, role, pw in DEMO_USERS:
        if db.scalar(select(User).where(User.email == email)):
            continue
        db.add(
            User(
                email=email,
                full_name=name,
                role=role,
                organization_id=org.id,
                organization=org.name,
                hashed_password=hash_password(pw),
                is_active=True,
                is_verified=True,
            )
        )
    db.commit()

    counts = provisioning.provision_demo_workspace(
        db,
        org,
        rng=RNG,
        incidents=settings.SEED_INCIDENTS,
        hospitals=settings.SEED_HOSPITALS,
        shelters=settings.SEED_SHELTERS,
        resources=settings.SEED_RESOURCES,
        utility_outages=settings.SEED_UTILITY_OUTAGES,
        alerts=settings.SEED_ALERTS,
    )
    return {"seeded": True, "organization": org.name, **counts}
