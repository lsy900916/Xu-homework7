"""
初始化订单数据库，创建必要的表
"""
import sqlite3
import os
from datetime import datetime

# 确保数据库目录存在
db_path = os.path.join(os.path.dirname(__file__), "orders.db")
print(f"📁 数据库文件路径: {db_path}")

# 连接数据库（如果不存在会自动创建）
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 创建orders表
create_table_sql = """
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_no VARCHAR(50) NOT NULL UNIQUE,
    customer_name VARCHAR(100) NOT NULL,
    customer_phone VARCHAR(20) NOT NULL,
    order_date DATE NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL DEFAULT 0,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    category VARCHAR(50) NOT NULL DEFAULT '未分类',
    items TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);
"""

cursor.execute(create_table_sql)
conn.commit()
print("✅ orders表创建成功！")

# 创建索引
create_index_sql = """
CREATE INDEX IF NOT EXISTS idx_order_date ON orders(order_date);
CREATE INDEX IF NOT EXISTS idx_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_customer_phone ON orders(customer_phone);
"""
cursor.executescript(create_index_sql)
conn.commit()
print("✅ 索引创建成功！")

# 检查表是否创建成功
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='orders';")
table_exists = cursor.fetchone()
if table_exists:
    print("\n📋 数据库表结构验证：")
    cursor.execute("PRAGMA table_info(orders);")
    columns = cursor.fetchall()
    print(f"{'列名':<20} {'类型':<15} {'非空'}")
    print("-"*50)
    for col in columns:
        print(f"{col[1]:<20} {col[2]:<15} {col[3]}")

# 插入一些测试数据
print("\n🧪 插入测试数据...")
test_orders = [
    {
        "order_no": "ORD20240115001",
        "customer_name": "张三",
        "customer_phone": "13800138001",
        "order_date": "2024-01-15",
        "total_amount": 299.00,
        "status": "completed",
        "category": "电子产品",
        "items": '[{"name":"无线鼠标","quantity":1,"price":299.0}]',
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    },
    {
        "order_no": "ORD20240116001",
        "customer_name": "李四",
        "customer_phone": "13800138002",
        "order_date": "2024-01-16",
        "total_amount": 599.00,
        "status": "shipping",
        "category": "电子产品",
        "items": '[{"name":"蓝牙耳机","quantity":1,"price":599.0}]',
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
]

# 检查是否已有数据
cursor.execute("SELECT COUNT(*) FROM orders")
count = cursor.fetchone()[0]
if count == 0:
    for order in test_orders:
        cursor.execute("""
            INSERT INTO orders (order_no, customer_name, customer_phone, order_date, 
                             total_amount, status, category, items, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            order["order_no"], order["customer_name"], order["customer_phone"], order["order_date"],
            order["total_amount"], order["status"], order["category"], order["items"],
            order["created_at"], order["updated_at"]
        ))
    conn.commit()
    print(f"✅ 插入了{len(test_orders)}条测试数据")
else:
    print(f"📊 数据库中已有{count}条记录，跳过测试数据插入")

# 验证创建订单功能
print("\n🚀 测试创建余富贵的订单...")
# 动态导入order_management模块
import sys
import importlib.util
project_root = os.path.dirname(__file__)
sys.path.insert(0, project_root)
script_path = os.path.join(project_root, "skills", "order-management", "scripts", "order_management.py")
spec = importlib.util.spec_from_file_location("order_management", script_path)
order_management = importlib.util.module_from_spec(spec)
spec.loader.exec_module(order_management)
handle_order_operation = order_management.handle_order_operation

result = handle_order_operation(
    action="create_order",
    customer_name="余富贵",
    customer_phone="13800138003",
    items=[{
        "name": "机械键盘",
        "quantity": 1,
        "price": 3399.00
    }]
)

if result["success"]:
    print(f"✅ 余富贵的订单创建成功！")
    print(f"   订单号: {result['order_no']}")
    print(f"   总金额: ¥{3399.00}")
else:
    print(f"❌ 创建失败: {result.get('error')}")

# 最后查询所有订单
print("\n📈 最终数据库中的所有订单:")
cursor.execute("SELECT id, order_no, customer_name, customer_phone, total_amount, status FROM orders ORDER BY id DESC")
rows = cursor.fetchall()
print(f"{'ID':<5} {'订单号':<18} {'客户':<8} {'电话':<15} {'金额':<10} {'状态'}")
print("-"*70)
for row in rows:
    print(f"{row[0]:<5} {row[1]:<18} {row[2]:<8} {row[3]:<15} ¥{row[4]:<8.2f} {row[5]}")

conn.close()
print("\n🎉 数据库初始化完成！")