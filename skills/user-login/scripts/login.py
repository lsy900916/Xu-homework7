"""
用户名密码登录脚本
"""
from __future__ import annotations

import os
from typing import Dict, Any

from agent_core.auth_token import create_access_token, create_refresh_token
from repository.sqlite_user_repository import SqliteUserRepository


def login_with_username_password(username: str, password: str) -> Dict[str, Any]:
    if not username or not password:
        return {"success": False, "error": "username 和 password 不能为空"}

    repo = SqliteUserRepository()
    repo.init_auth_db()
    user = repo.get_user_by_username(username)
    if user is None:
        return {"success": False, "error": "用户名或密码错误"}

    password_hash = repo.hash_password(password)
    if password_hash != user["password_hash"]:
        return {"success": False, "error": "用户名或密码错误"}

    access_expires_in = int(os.getenv("AUTH_ACCESS_EXPIRES_IN", "7200"))
    refresh_expires_in = int(os.getenv("AUTH_REFRESH_EXPIRES_IN", str(7 * 24 * 3600)))
    access_token = create_access_token(
        uid=user["id"],
        username=user["username"],
        expires_in_seconds=access_expires_in,
    )
    refresh_token = create_refresh_token(
        uid=user["id"],
        username=user["username"],
        expires_in_seconds=refresh_expires_in,
    )
    return {
        "success": True,
        "token": access_token,  # 兼容旧字段
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer",
        "expires_in": access_expires_in,
        "uid": user["id"],
        "username": user["username"],
    }

