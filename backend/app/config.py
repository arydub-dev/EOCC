"""Application configuration loaded from environment variables.

Security posture:
- No secret is hardcoded; every sensitive value comes from the environment.
- In production (``ENVIRONMENT=production``) the app refuses to start with
  default/insecure secrets (fail-closed, secure by default).
- Encryption keys are derived deterministically from ``SECRET_KEY`` only as a
  development convenience; production deployments must supply explicit keys.
"""
from __future__ import annotations

import base64
import hashlib
import logging
from functools import lru_cache
from typing import Annotated

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

logger = logging.getLogger("eocc.config")

_INSECURE_DEFAULT_SECRET = "change-me-in-production-please-use-a-long-random-string"  # noqa: S105


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    # ── App ──
    PROJECT_NAME: str = "Emergency Operations Command Center"
    ENVIRONMENT: str = "development"
    API_V1_PREFIX: str = "/api/v1"
    VERSION: str = "1.0.0"

    # ── Database ──
    DATABASE_URL: str = "sqlite:///./eocc.db"

    # ── Cryptographic secrets (NEVER hardcode in production) ──
    SECRET_KEY: str = _INSECURE_DEFAULT_SECRET
    REFRESH_TOKEN_SECRET: str = ""  # falls back to a derivation of SECRET_KEY
    ENCRYPTION_KEY: str = ""  # Fernet key (urlsafe b64, 32 bytes); derived if blank
    ALGORITHM: str = "HS256"

    # ── Token lifetimes ──
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 14
    REMEMBER_ME_EXPIRE_DAYS: int = 30

    # ── Session cookies (used when USE_AUTH_COOKIES=true, recommended behind TLS) ──
    USE_AUTH_COOKIES: bool = True
    COOKIE_SECURE: bool = False  # set true in production (HTTPS only)
    COOKIE_SAMESITE: str = "lax"  # lax | strict | none
    COOKIE_DOMAIN: str | None = None
    REFRESH_COOKIE_NAME: str = "eocc_refresh"

    # ── Password policy ──
    PASSWORD_MIN_LENGTH: int = 12
    PASSWORD_REQUIRE_UPPER: bool = True
    PASSWORD_REQUIRE_LOWER: bool = True
    PASSWORD_REQUIRE_DIGIT: bool = True
    PASSWORD_REQUIRE_SYMBOL: bool = True

    # ── Account lockout (brute-force mitigation) ──
    MAX_FAILED_LOGINS: int = 5
    LOCKOUT_MINUTES: int = 15

    # ── MFA ──
    MFA_ISSUER: str = "EOCC"

    # ── Rate limiting (in-memory fixed window; use Redis in multi-instance prod) ──
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_DEFAULT_PER_MINUTE: int = 300
    RATE_LIMIT_AUTH_PER_MINUTE: int = 20

    # ── Request / upload limits ──
    MAX_REQUEST_BYTES: int = 2_000_000  # 2 MB general request cap
    MAX_UPLOAD_BYTES: int = 10_000_000  # 10 MB file cap
    MAX_IMPORT_ROWS: int = 50_000

    # ── CORS — NoDecode lets the validator accept a comma-separated string ──
    BACKEND_CORS_ORIGINS: Annotated[list[str], NoDecode] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    # ── Seeding ──
    SEED_ON_STARTUP: bool = True
    SEED_INCIDENTS: int = 100
    SEED_HOSPITALS: int = 50
    SEED_SHELTERS: int = 200
    SEED_RESOURCES: int = 1000
    SEED_UTILITY_OUTAGES: int = 500
    SEED_ALERTS: int = 1000

    # ── AI ──
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def _split_cors(cls, value: object) -> object:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @model_validator(mode="after")
    def _enforce_secure_production(self) -> "Settings":
        if self.is_production:
            if self.SECRET_KEY == _INSECURE_DEFAULT_SECRET or len(self.SECRET_KEY) < 32:
                raise ValueError(
                    "SECRET_KEY must be set to a strong (>=32 char) value in production."
                )
            if not self.ENCRYPTION_KEY:
                raise ValueError("ENCRYPTION_KEY must be explicitly set in production.")
            if self.COOKIE_SECURE is False:
                logger.warning("COOKIE_SECURE is false in production — cookies should be HTTPS-only.")
        elif self.SECRET_KEY == _INSECURE_DEFAULT_SECRET:
            logger.warning(
                "Using the INSECURE default SECRET_KEY — acceptable for local dev only."
            )
        return self

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() in {"production", "prod"}

    @property
    def ai_enabled(self) -> bool:
        return bool(self.OPENAI_API_KEY.strip())

    @property
    def refresh_secret(self) -> str:
        return self.REFRESH_TOKEN_SECRET or hashlib.sha256(
            (self.SECRET_KEY + ":refresh").encode()
        ).hexdigest()

    @property
    def fernet_key(self) -> bytes:
        """Return a valid 32-byte urlsafe-base64 Fernet key.

        Uses ENCRYPTION_KEY when provided, otherwise derives one from SECRET_KEY
        (dev convenience). Production requires ENCRYPTION_KEY (enforced above).
        """
        if self.ENCRYPTION_KEY:
            return self.ENCRYPTION_KEY.encode()
        digest = hashlib.sha256((self.SECRET_KEY + ":fernet").encode()).digest()
        return base64.urlsafe_b64encode(digest)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
