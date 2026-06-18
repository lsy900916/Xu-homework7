"""
SQLite 用户仓库
负责用户表初始化与用户查询
"""
from __future__ import annotations

import hashlib
import os
import sqlite3
from typing import Optional, Dict, Any


class SqliteUserRepository:
    """SQLite 用户数据访问层"""

    def __init__(self, db_path: Optional[str] = None):
        default_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "auth.db"))
        self.db_path = db_path or os.getenv("AUTH_DB_PATH", default_path)
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def init_table(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT (datetime('now'))
                )
                """
            )
            conn.commit()

    def ensure_default_user(self) -> None:
        """
        确保存在默认用户，便于首次启动测试：
        username=admin, password=admin123
        """
        username = os.getenv("AUTH_DEFAULT_USERNAME", "admin")
        password = os.getenv("AUTH_DEFAULT_PASSWORD", "admin123")
        password_hash = self.hash_password(password)

        with self._connect() as conn:
            row = conn.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
            if row is None:
                conn.execute(
                    "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                    (username, password_hash),
                )
                conn.commit()

    def init_auth_db(self) -> None:
        self.init_table()
        self.ensure_default_user()

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT id, username, password_hash FROM users WHERE username = ?",
                (username,),
            ).fetchone()
            if row is None:
                return None
            return {"id": row["id"], "username": row["username"], "password_hash": row["password_hash"]}

