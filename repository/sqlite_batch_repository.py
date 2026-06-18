"""
SQLite 批次计数器仓库
兼容MssqlRepository的接口，用于本地测试和开发
无需依赖外部SQL Server，使用本地SQLite数据库
"""
from __future__ import annotations

import os
import sqlite3
from typing import Dict, List, Optional, Any, Tuple


class SqliteBatchRepository:
    """SQLite批次计数器数据仓库类，兼容MssqlRepository的接口"""

    def __init__(
        self,
        db_path: Optional[str] = None,
    ):
        """
        初始化SQLite数据仓库
        参数优先使用传入值，未传入时从环境变量读取
        """
        default_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "batch_counter.db"))
        self.db_path = db_path or os.getenv("SQLITE_DB_PATH", default_path)
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        
        # 初始化数据库和表
        self._init_database()

    def _connect(self) -> sqlite3.Connection:
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_database(self) -> None:
        """初始化数据库和batch_counter表"""
        with self._connect() as conn:
            # 创建表
            conn.execute("""
                CREATE TABLE IF NOT EXISTS batch_counter (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    batch_date TEXT NOT NULL UNIQUE,
                    seq INTEGER NOT NULL DEFAULT 1
                )
            """)
            
            # 检查是否已有数据
            cursor = conn.execute("SELECT COUNT(*) FROM batch_counter")
            count = cursor.fetchone()[0]
            
            # 如果没有数据，插入测试数据
            if count == 0:
                test_data = [
                    ('2026-04-08', 11),
                    ('2026-04-09', 4),
                    ('2026-04-10', 2),
                    ('2026-04-14', 2),
                    ('2026-04-15', 4),
                    ('2026-04-16', 8),
                    ('2026-04-17', 7),
                    ('2026-04-18', 3),
                    ('2026-04-21', 1),
                    ('2026-04-22', 5),
                    ('2026-04-23', 3),
                    ('2026-04-24', 4),
                    ('2026-04-25', 1),
                    ('2026-04-27', 1),
                    ('2026-04-28', 1),
                    ('2026-05-01', 6),
                    ('2026-05-02', 15),
                    ('2026-05-03', 8),
                    ('2026-05-04', 11),
                    ('2026-05-05', 7),
                    ('2026-05-07', 4),
                    ('2026-05-08', 5),
                ]
                conn.executemany(
                    "INSERT INTO batch_counter (batch_date, seq) VALUES (?, ?)",
                    test_data
                )
                conn.commit()
                print(f"已初始化batch_counter数据库，插入{len(test_data)}条测试数据")

    def execute_query(self, sql: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """
        执行查询SQL，返回字典列表（兼容MssqlRepository的接口）
        SQLite不支持OFFSET...FETCH的语法和SQL Server完全一样，所以可以直接使用
        """
        # 将SQL Server的语法转换为SQLite兼容的语法
        sql = sql.replace("OFFSET ? ROWS FETCH NEXT ? ROWS ONLY", "LIMIT ? OFFSET ?")
        # 调整参数顺序，因为SQLite的LIMIT是先数量再偏移，和SQL Server的参数顺序相反
        if "LIMIT ? OFFSET ?" in sql and params and len(params) >= 2:
            params = list(params)
            # 交换最后两个参数：原来的(offset, page_size)变为(page_size, offset)
            params[-1], params[-2] = params[-2], params[-1]
            params = tuple(params)

        conn = self._connect()
        try:
            cursor = conn.cursor()
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)

            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
            result = []
            for row in rows:
                row_dict = {}
                for i, col in enumerate(columns):
                    row_dict[col] = row[i]
                result.append(row_dict)
            return result
        finally:
            conn.close()

    def execute_scalar(self, sql: str, params: Optional[tuple] = None) -> Any:
        """执行查询SQL，返回单个值（兼容MssqlRepository的接口）"""
        conn = self._connect()
        try:
            cursor = conn.cursor()
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            row = cursor.fetchone()
            return row[0] if row else None
        finally:
            conn.close()