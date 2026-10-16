"""
Security helpers for HealthCare AI
===================================
Signed session tokens, per-user access checks, admin/debug guards, and
application-level encryption for stored Google refresh tokens.

Environment:
  SESSION_SECRET       Secret used to sign session tokens and derive the token
                       encryption key. Falls back to GOOGLE_CLIENT_SECRET so
                       existing deployments keep working; set it in production.
  TOKEN_ENCRYPTION_KEY Optional Fernet key (urlsafe base64, 32 bytes) used instead
                       of the key derived from SESSION_SECRET.
  ADMIN_API_KEY        Enables the admin routes (/rag/ingest, /rag/stats, ...) when set.
  ENABLE_DEBUG_ENDPOINTS  Set to "1" to enable /debug/* routes (never in production).
"""

import base64
import hashlib
import hmac
import json
import os
import time
from typing import Optional

from cryptography.fernet import Fernet, InvalidToken
from fastapi import Depends, Header, HTTPException

SESSION_TTL_SECONDS = 30 * 24 * 60 * 60  # 30 days
_ENC_PREFIX = "enc:v1:"


def _signing_secret() -> bytes:
    secret = os.getenv("SESSION_SECRET") or os.getenv("GOOGLE_CLIENT_SECRET")
    if not secret:
        raise RuntimeError("SESSION_SECRET (or GOOGLE_CLIENT_SECRET) must be set")
    return secret.encode("utf-8")


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _unb64(text: str) -> bytes:
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


# ── Session tokens ─────────────────────────────────────────────

def create_session_token(user_id: int) -> str:
    """Return a signed token proving the holder logged in as `user_id`."""
    payload = _b64(json.dumps({"uid": user_id, "exp": int(time.time()) + SESSION_TTL_SECONDS}).encode())
    signature = _b64(hmac.new(_signing_secret(), payload.encode(), hashlib.sha256).digest())
    return f"{payload}.{signature}"


def verify_session_token(token: str) -> Optional[int]:
    """Return the user id inside a valid, unexpired token, otherwise None."""
    try:
        payload, signature = token.split(".", 1)
        expected = _b64(hmac.new(_signing_secret(), payload.encode(), hashlib.sha256).digest())
        if not hmac.compare_digest(signature, expected):
            return None
        data = json.loads(_unb64(payload))
        if int(data["exp"]) < time.time():
            return None
        return int(data["uid"])
    except Exception:
        return None


def current_user_id(authorization: Optional[str] = Header(default=None)) -> int:
    """FastAPI dependency: the user id from the `Authorization: Bearer <token>` header."""
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Please log in to continue.")
    uid = verify_session_token(authorization[7:].strip())
    if uid is None:
        raise HTTPException(status_code=401, detail="Your session has expired. Please log in again.")
    return uid


def require_user(user_id: int, uid: int = Depends(current_user_id)) -> int:
    """FastAPI dependency for routes with a `{user_id}` path parameter: callers may only touch their own data."""
    if uid != user_id:
        raise HTTPException(status_code=403, detail="You can only access your own data.")
    return uid


# ── Admin and debug guards ─────────────────────────────────────

def require_admin(x_admin_key: Optional[str] = Header(default=None)) -> None:
    expected = os.getenv("ADMIN_API_KEY")
    if not expected or not x_admin_key or not hmac.compare_digest(x_admin_key, expected):
        raise HTTPException(status_code=403, detail="Not allowed.")


def require_debug() -> None:
    if os.getenv("ENABLE_DEBUG_ENDPOINTS") != "1":
        raise HTTPException(status_code=404, detail="Not found.")


# ── Encryption of stored secrets ───────────────────────────────

def _fernet() -> Fernet:
    key = os.getenv("TOKEN_ENCRYPTION_KEY")
    if key:
        return Fernet(key.encode("utf-8"))
    derived = hashlib.sha256(b"healthagent-token-encryption:" + _signing_secret()).digest()
    return Fernet(base64.urlsafe_b64encode(derived))


def encrypt_secret(plain: Optional[str]) -> Optional[str]:
    if not plain:
        return plain
    if plain.startswith(_ENC_PREFIX):
        return plain
    return _ENC_PREFIX + _fernet().encrypt(plain.encode("utf-8")).decode("ascii")


def decrypt_secret(stored: Optional[str]) -> Optional[str]:
    """Decrypt a stored secret. Legacy plaintext values pass through unchanged."""
    if not stored or not stored.startswith(_ENC_PREFIX):
        return stored
    try:
        return _fernet().decrypt(stored[len(_ENC_PREFIX):].encode("ascii")).decode("utf-8")
    except InvalidToken:
        return None
