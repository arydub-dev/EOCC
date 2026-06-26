"""Unit tests for the cryptography and password-policy primitives."""

from __future__ import annotations

from app.core import security


def test_password_hash_roundtrip():
    hashed = security.hash_password("Str0ng-Passw0rd!")
    assert hashed != "Str0ng-Passw0rd!"
    assert security.verify_password("Str0ng-Passw0rd!", hashed)
    assert not security.verify_password("wrong-password", hashed)


def test_verify_password_handles_invalid_hash():
    assert security.verify_password("anything", "not-a-valid-hash") is False


def test_access_token_roundtrip():
    token = security.create_access_token("42", "admin", organization_id=7)
    payload = security.decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == "42"
    assert payload["role"] == "admin"
    assert payload["org"] == 7
    assert payload["type"] == "access"


def test_decode_rejects_garbage_token():
    assert security.decode_access_token("garbage.token.value") is None


def test_refresh_token_hash_is_deterministic_and_opaque():
    token = security.generate_refresh_token()
    assert security.hash_refresh_token(token) == security.hash_refresh_token(token)
    assert security.hash_refresh_token(token) != token


def test_field_encryption_roundtrip():
    ciphertext = security.encrypt_value("super-secret")
    assert ciphertext is not None
    assert ciphertext != "super-secret"
    assert security.decrypt_value(ciphertext) == "super-secret"
    assert security.encrypt_value(None) is None
    assert security.decrypt_value(None) is None


def test_totp_verifies_current_code():
    secret = security.generate_totp_secret()
    import pyotp

    code = pyotp.TOTP(secret).now()
    assert security.verify_totp(secret, code)
    assert not security.verify_totp(secret, "000000")


def test_password_policy_flags_weak_passwords():
    assert security.validate_password_policy("short") != []
    assert security.validate_password_policy("Str0ng-Passw0rd!") == []
