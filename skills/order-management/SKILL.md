---
name: order-management
description: 订单管理助手，支持订单的查询、创建、状态更新和统计分析。当用户要查询订单(list_orders)、创建订单(create_order)、查看订单详情(get_order_detail)、更新订单状态(update_order_status)、统计订单数据(order_statistics)时调用。
trigger_keywords: [
    "查询订单",
    "帮我查订单",
    "查看订单",
    "我的订单",
    "最近的订单",
    "订单列表",
    "创建订单",
    "新建订单",
    "生成订单",
    "新增订单",
    "订单详情",
    "查看订单详情",
    "更新订单状态",
    "修改订单状态",
    "订单状态改为",
    "改成",
    "变为",
    "统计订单",
    "订单统计",
    "分析订单",
    "订单情况",
    "order",
    "订单管理",
    # 英文触发关键词
    "check order",
    "view order",
    "my orders",
    "order list",
    "create order",
    "new order",
    "add order",
    "order details",
    "view order details",
    "update order status",
    "change order status",
    "mark order as",
    "set order status to",
    "order statistics",
    "analyze orders",
    "order info",
    "orders",
    "order management",
    "get order",
    "list orders",
    "order detail",
  ]
---

# 订单管理技能使用规范

## 使用时机

当用户需要查询、创建、更新或统计订单数据时触发本技能，支持通过自然语言交互自动识别和调用。

## 数据库信息

- 支持SQLite本地数据库和SQL Server云端数据库
- 表名：orders
- 表结构：
  - id: int (自增主键)
  - order_no: varchar(32) NOT NULL UNIQUE (订单号，如ORD20240115001)
  - customer_name: varchar(100) NOT NULL (客户姓名)
  - customer_phone: varchar(20) NOT NULL (客户电话)
  - order_date: date NOT NULL (订单日期)
  - total_amount: decimal(12,2) NOT NULL (订单总金额)
  - status: varchar(20) NOT NULL DEFAULT 'pending' (订单状态：pending-待支付, paid-已支付, shipping-发货中, completed-已完成)
  - category: varchar(50) (商品类别)
  - items: json (商品明细JSON)
  - created_at: datetime NOT NULL DEFAULT CURRENT_TIMESTAMP
  - updated_at: datetime NOT NULL DEFAULT CURRENT_TIMESTAMP

## 功能说明

1. **list_orders**: 分页查询订单列表，支持状态、日期、商品类别等多条件筛选
2. **get_order_detail**: 根据订单ID或订单号查询完整的订单详情
3. **create_order**: 创建新订单，自动生成订单号
4. **update_order_status**: 更新订单状态，支持状态流转验证（pending→paid→shipping→completed）
5. **order_statistics**: 按日期、状态、商品类别等维度进行订单统计分析

## 数据库配置

- 默认使用SQLite本地数据库，配置文件位置：data/orders.db
- 如需使用SQL Server，修改.env文件中的USE_SQLITE=false并配置MSSQL连接参数

## 输入要求

- action: 操作类型（必需）
  - "list_orders": 分页查询订单列表
  - "get_order_detail": 获取订单详情
  - "create_order": 创建新订单
  - "update_order_status": 更新订单状态
  - "order_statistics": 订单统计分析

### list_orders 参数

- page: 页码，从1开始（默认值：1）
- page_size: 每页记录数（默认值：10）
- status: 订单状态筛选（可选）
- start_date: 起始日期筛选（可选，格式：YYYY-MM-DD）
- end_date: 结束日期筛选（可选，格式：YYYY-MM-DD）
- category: 商品类别筛选（可选）

### get_order_detail 参数

- order_id: 订单ID（可选，与order_no二选一）
- order_no: 订单号（可选，与order_id二选一）

### create_order 参数

- customer_name: 客户姓名（必需）
- customer_phone: 客户电话（必需）
- items: 商品列表（必需，格式：[{"name":"商品名","quantity":数量,"price":单价,"category":"类别"}]）
- order_date: 订单日期（可选，默认今天）

### update_order_status 参数

- order_id: 订单ID（必需）
- new_status: 新状态（必需，必须是合法的状态流转）

### order_statistics 参数

- start_date: 起始日期（可选）
- end_date: 结束日期（可选）
- group_by: 分组维度，支持date, status, category（默认：date）

## 输出说明

### list_orders 输出

- data: 订单列表
- pagination: 分页信息
- filters: 筛选条件

### get_order_detail 输出

- order: 完整的订单详情，包括商品明细
- success: 是否成功
- error: 错误信息（如果有）

### create_order 输出

- success: 是否成功
- order_no: 生成的订单号
- message: 提示信息

### update_order_status 输出

- success: 是否成功
- old_status: 原状态
- new_status: 新状态
- message: 提示信息

### order_statistics 输出

- statistics: 统计数据
- period: 统计时间段
- group_by: 分组维度
