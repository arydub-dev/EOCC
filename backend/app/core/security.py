"""Cryptography: password hashing, JWT access tokens, field encryption, TOTP.

- Passwords are hashed with **Argon2id** (memory-hard); legacy bcrypt hashes are
  still verified and transparently upgraded on next login.
- Access tokens are short-lived JWTs carrying a unique ``jti`` so they can be
  correlated with server-side sessions and revoked.
- Refresh tokens are opaque random strings; only their SHA-256 hash is stored.
- Sensitive fields (e.g. connector secrets, MFA seeds) are encrypted at rest
  with Fernet (AES-128-CBC + HMAC).
"""

from __future__ import annotations

import hashlib
import hmac
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

import pyotp
from cryptography.fernet import Fernet, InvalidToken
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

# Argon2id preferred; bcrypt retained for verifying/ upgrading legacy hashes.
pwd_context = CryptContext(
    schemes=["argon2", "bcrypt"],
    deprecated="auto",
    argon2__type="ID",
    argon2__memory_cost=65536,  # 64 MiB
    argon2__time_cost=3,
    argon2__parallelism=2,
)

_fernet = Fernet(settings.fernet_key)


# ── Passwords ──
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except ValueError:
        return False


def needs_rehash(hashed_password: str) -> bool:
    return pwd_context.needs_update(hashed_password)


# ── Access tokens (JWT) ──
def create_access_token(
    subject: str,
    role: str,
    *,
    organization_id: int | None = None,
    expires_minutes: int | None = None,
    extra: dict[str, Any] | None = None,
) -> str:
    now = datetime.now(UTC)
    expire = now + timedelta(minutes=expires_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload: dict[str, Any] = {
        "sub": subject,
        "role": role,
        "org": organization_id,
        "type": "access",
        "iat": now,
        "nbf": now,
        "exp": expire,
        "jti": secrets.token_urlsafe(16),
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any] | None:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None
    if payload.get("type") != "access":
        return None
    return payload


# ── Refresh tokens (opaque) ──
def generate_refresh_token() -> str:
    return secrets.token_urlsafe(48)


def hash_refresh_token(token: str) -> str:
    """Keyed hash so DB compromise alone cannot validate stolen refresh tokens."""
    return hmac.new(settings.refresh_secret.encode(), token.encode(), hashlib.sha256).hexdigest()


def constant_time_equals(a: str, b: str) -> bool:
    return hmac.compare_digest(a, b)


# ── Field encryption (at rest) ──
def encrypt_value(plaintext: str | None) -> str | None:
    if plaintext is None or plaintext == "":
        return None
    return _fernet.encrypt(plaintext.encode()).decode()


def decrypt_value(ciphertext: str | None) -> str | None:
    if not ciphertext:
        return None
    try:
        return _fernet.decrypt(ciphertext.encode()).decode()
    except InvalidToken:
        return None


# ── TOTP / MFA ──
def generate_totp_secret() -> str:
    return pyotp.random_base32()


def totp_provisioning_uri(secret: str, account: str) -> str:
    return pyotp.TOTP(secret).provisioning_uri(name=account, issuer_name=settings.MFA_ISSUER)


def verify_totp(secret: str, code: str) -> bool:
    if not secret or not code:
        return False
    return pyotp.TOTP(secret).verify(code.strip(), valid_window=1)


# ── Password policy ──
def validate_password_policy(password: str) -> list[str]:
    """Return a list of human-readable policy violations (empty = compliant)."""
    errors: list[str] = []
    if len(password) < settings.PASSWORD_MIN_LENGTH:
        errors.append(f"Must be at least {settings.PASSWORD_MIN_LENGTH} characters.")
    if settings.PASSWORD_REQUIRE_UPPER and not any(c.isupper() for c in password):
        errors.append("Must contain an uppercase letter.")
    if settings.PASSWORD_REQUIRE_LOWER and not any(c.islower() for c in password):
        errors.append("Must contain a lowercase letter.")
    if settings.PASSWORD_REQUIRE_DIGIT and not any(c.isdigit() for c in password):
        errors.append("Must contain a digit.")
    if settings.PASSWORD_REQUIRE_SYMBOL and password.isalnum():
        errors.append("Must contain a symbol.")
    return errors
