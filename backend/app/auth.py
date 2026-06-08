from __future__ import annotations

import hashlib
import hmac
import os

from .config import Settings


def hash_password(password: str, salt: bytes | None = None) -> str:
    salt = salt or os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120_000)
    return f"pbkdf2_sha256${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        algorithm, salt_hex, expected_hex = stored_hash.split("$", 2)
    except ValueError:
        return False
    if algorithm != "pbkdf2_sha256":
        return False
    actual = hash_password(password, bytes.fromhex(salt_hex)).split("$", 2)[2]
    return hmac.compare_digest(actual, expected_hex)


def admin_password_hash(settings: Settings) -> str:
    configured_hash = os.environ.get("ARMARIUM_ADMIN_PASSWORD_HASH")
    if configured_hash:
        return configured_hash
    return hash_password(settings.admin_password, b"armarium-local-salt")


def authenticate(username: str, password: str, settings: Settings) -> bool:
    return username == settings.admin_username and verify_password(password, admin_password_hash(settings))
