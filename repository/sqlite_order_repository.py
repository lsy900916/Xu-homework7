"""
SQLite 订单数据仓库
兼容MssqlRepository的接口，用于本地测试和开发
无需依赖外部SQL Server，使用本地SQLite数据库
"""
from __future__ import annotations

import os
import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple


class SqliteOrderRepository:
    """SQLite订单数据仓库类，兼容MssqlRepository的接口"""

    # 合法的订单状态流转
    VALID_STATUS_TRANSITIONS = {
        "pending": ["paid"],
        "paid": ["shipping"],
        "shipping": ["completed"],
        "completed": []  # 已完成的订单不能再变更状态
    }
    
    # 状态中文映射
    STATUS_MAPPING = {
        "pending": "待支付",
        "paid": "已支付",
        "shipping": "发货中",
        "completed": "已完成"
    }

    def __init__(
        self,
        db_path: Optional[str] = None,
    ):
        """
        初始化SQLite订单数据仓库
        参数优先使用传入值，未传入时从环境变量读取
        """
        # 使用data目录下的orders.db，保持项目结构整洁
        default_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "orders.db"))
        self.db_path = db_path or os.getenv("SQLITE_ORDERS_DB_PATH", default_path)
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
        """初始化数据库和orders表"""
        with self._connect() as conn:
            # 创建订单表
            conn.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_no TEXT NOT NULL UNIQUE,
                    customer_name TEXT NOT NULL,
                    customer_phone TEXT NOT NULL,
                    order_date TEXT NOT NULL,
                    total_amount REAL NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    category TEXT,
                    items TEXT,  -- JSON存储商品明细
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            # 创建索引
            conn.execute("CREATE INDEX IF NOT EXISTS idx_order_date ON orders(order_date)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_status ON orders(status)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_category ON orders(category)")
            
            # 检查是否已有数据
            cursor = conn.execute("SELECT COUNT(*) FROM orders")
            count = cursor.fetchone()[0]
            
            # 如果没有数据，插入测试数据
            if count == 0:
                test_orders = self._generate_test_data()
                conn.executemany(
                    """INSERT INTO orders (
                        order_no, customer_name, customer_phone, order_date, 
                        total_amount, status, category, items, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    test_orders
                )
                conn.commit()
                print(f"已初始化orders数据库，插入{len(test_orders)}条测试数据")

    def _generate_test_data(self) -> List[tuple]:
        """生成测试订单数据"""
        current_time = datetime.now().isoformat()
        test_customers = [
            ("徐十七", "13800138001", "电子产品"),
            ("朱十六", "13800138002", "服装鞋帽"),
            ("张三", "13800138003", "家居用品"),
            ("李四", "13800138004", "电子产品"),
            ("王五", "13800138005", "食品饮料"),
            ("赵六", "13800138006", "电子产品"),
            ("钱七", "13800138007", "服装鞋帽"),
            ("孙八", "13800138008", "家居用品"),
        ]
        
        sample_items = [
            [
                {"name": "iPhone手机壳", "quantity": 2, "price": 49.5},
                {"name": "钢化膜", "quantity": 1, "price": 29.9}
            ],
            [
                {"name": "蓝牙耳机", "quantity": 1, "price": 599.0}
            ],
            [
                {"name": "机械键盘", "quantity": 1, "price": 1299.0},
                {"name": "鼠标垫", "quantity": 1, "price": 39.9}
            ],
            [
                {"name": "Nike运动鞋", "quantity": 1, "price": 899.0}
            ],
            [
                {"name": "坚果礼盒", "quantity": 2, "price": 168.0}
            ]
        ]
        
        test_orders = []
        order_counter = 1
        
        for i in range(20):  # 生成20条测试订单
            customer_idx = i % len(test_customers)
            items_idx = i % len(sample_items)
            customer = test_customers[customer_idx]
            items = sample_items[items_idx]
            
            # 计算总金额
            total = sum(item["price"] * item["quantity"] for item in items)
            
            # 生成订单号
            order_date_str = f"2024-{(i//30)+1:02d}-{(i%28)+1:02d}"
            order_no = f"ORD{order_date_str.replace('-', '')}{order_counter:03d}"
            order_counter += 1
            
            # 随机状态
            statuses = ["pending", "paid", "shipping", "completed"]
            status = statuses[i % len(statuses)]
            
            # 将items转换为JSON字符串
            items_json = json.dumps(items, ensure_ascii=False)
            
            test_orders.append((
                order_no,
                customer[0],
                customer[1],
                order_date_str,
                total,
                status,
                customer[2],
                items_json,
                current_time,
                current_time
            ))
            
        return test_orders

    def execute_query(self, sql: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """
        执行查询SQL，返回字典列表（兼容MssqlRepository的接口）
        SQLite不支持OFFSET...FETCH的语法和SQL Server完全一样，所以需要转换
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
                    # 解析items字段的JSON
                    if col == "items" and row_dict[col]:
                        try:
                            row_dict[col] = json.loads(row_dict[col])
                        except:
                            pass
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

    def execute_non_query(self, sql: str, params: Optional[tuple] = None) -> int:
        """执行非查询SQL，返回受影响的行数"""
        conn = self._connect()
        try:
            cursor = conn.cursor()
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            conn.commit()
            return cursor.rowcount
        finally:
            conn.close()

    def validate_status_transition(self, current_status: str, new_status: str) -> bool:
        """验证状态流转是否合法"""
        if current_status not in self.VALID_STATUS_TRANSITIONS:
            return False
        return new_status in self.VALID_STATUS_TRANSITIONS[current_status]

    def generate_order_no(self, order_date: str) -> str:
        """生成订单号"""
        date_part = order_date.replace("-", "")
        # 查询当天已有多少订单
        count = self.execute_scalar(
            "SELECT COUNT(*) FROM orders WHERE order_date = ?",
            (order_date,)
        )
        sequence = count + 1
        return f"ORD{date_part}{sequence:03d}"