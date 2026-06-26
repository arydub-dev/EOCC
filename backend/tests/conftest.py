"""Shared test configuration.

Force a self-contained, development-mode environment (in-memory SQLite, no
seeding, no production secret enforcement) before the application package is
imported, so the suite never touches a real database or external service.
"""

from __future__ import annotations

import os

os.environ.setdefault("ENVIRONMENT", "development")
os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("SEED_ON_STARTUP", "false")
os.environ.setdefault("RATE_LIMIT_ENABLED", "false")
