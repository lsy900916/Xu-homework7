"""
标准 JWT 生成与校验（PyJWT）
"""
from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

import jwt
from jwt import InvalidTokenError, ExpiredSignatureError


def _secret() -> str:
    return os.getenv("AUTH_TOKEN_SECRET", "change-this-secret")


def _algorithm() -> str:
    return os.getenv("AUTH_TOKEN_ALGORITHM", "HS256")


def create_access_token(uid: int, username: str, expires_in_seconds: int = 7200) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "uid": uid,
        "username": username,
        "type": "access",
        "iat": now,
        "exp": now + timedelta(seconds=int(expires_in_seconds)),
    }
    return jwt.encode(payload, _secret(), algorithm=_algorithm())


def create_refresh_token(uid: int, username: str, expires_in_seconds: int = 7 * 24 * 3600) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "uid": uid,
        "username": username,
        "type": "refresh",
        "iat": now,
        "exp": now + timedelta(seconds=int(expires_in_seconds)),
    }
    return jwt.encode(payload, _secret(), algorithm=_algorithm())


def verify_token(token: str, expected_type: Optional[str] = None) -> Optional[Dict[str, Any]]:
    try:
        payload = jwt.decode(token, _secret(), algorithms=[_algorithm()])
        if expected_type and payload.get("type") != expected_type:
            return None
        return payload
    except (InvalidTokenError, ExpiredSignatureError):
        return None

