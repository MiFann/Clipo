from __future__ import annotations

import hashlib
import hmac
import secrets
from typing import Annotated

from fastapi import Depends, Header, HTTPException, status


_TOKENS: dict[str, str] = {}


def hash_password(password: str, salt: str | None = None) -> str:
    safe_salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), safe_salt.encode("utf-8"), 120_000)
    return f"pbkdf2_sha256${safe_salt}${digest.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        algorithm, salt, digest = stored_hash.split("$", 2)
    except ValueError:
        return False

    if algorithm != "pbkdf2_sha256":
        return False

    candidate = hash_password(password, salt)
    return hmac.compare_digest(candidate, stored_hash)


def create_token(username: str) -> str:
    token = secrets.token_urlsafe(32)
    _TOKENS[token] = username
    return token


def clear_tokens() -> None:
    _TOKENS.clear()


def require_admin(authorization: Annotated[str | None, Header()] = None) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing admin token")

    token = authorization.removeprefix("Bearer ").strip()
    username = _TOKENS.get(token)
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid admin token")

    return username
