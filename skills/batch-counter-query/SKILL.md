---
name: batch-counter-query
description: 批次计数器查询助手，支持对SQL Server数据库batch_counter表进行分页查询和按日期统计seq合计
trigger_keywords: ["批次查询", "batch_counter", "批次计数", "seq统计", "按日期统计", "分页查询批次"]
---
# 批次计数器查询技能使用规范

## 使用时机
当需要查询SQL Server数据库中batch_counter表的数据时触发本技能，包括分页查询原始数据、按日期统计seq合计、获取整体汇总等。

## 数据库信息
- 服务器：xu-kuhne-projects-test.database.windows.net
- 驱动：ODBC Driver 17 for SQL Server
- 表名：dbo.batch_counter
- 表结构：
  - id: int (自增主键)
  - batch_date: date (批次日期，唯一约束)
  - seq: int (序列号，默认值1)

## 功能说明
1. **分页查询原始数据（page_query）**：按时间倒序分页查询batch_counter表的所有记录
2. **按日期统计seq合计（date_summary）**：按batch_date分组，统计每天的seq合计、最小值、最大值、平均值，支持分页
3. **整体汇总统计（total_summary）**：获取总记录数、总日期数、seq总计、最早/最晚日期等汇总信息

## 数据库配置
- 数据库名称由环境变量 **MSSQL_DATABASE** 指定（须在 .env 或运行环境中配置），不可通过参数传入。

## 输入要求
- action: 操作类型（必需）
  - "page_query": 分页查询原始数据
  - "date_summary": 按日期统计seq合计（分页）
  - "total_summary": 获取整体汇总统计
- page: 页码，从1开始（默认值：1）
- page_size: 每页记录数（默认值：10）
- start_date: 起始日期过滤（可选，格式：YYYY-MM-DD）
- end_date: 结束日期过滤（可选，格式：YYYY-MM-DD）


## 输出说明

### page_query 输出
- data: 记录列表，每条包含 id, batch_date, seq
- pagination: 分页信息（page, page_size, total_count, total_pages, has_next, has_prev）
- filters: 筛选条件

### date_summary 输出
- data: 按日期统计列表，每条包含 batch_date, record_count, seq_total, seq_min, seq_max, seq_avg
- pagination: 分页信息
- filters: 筛选条件

### total_summary 输出
- summary: 汇总信息（total_records, total_dates, seq_grand_total, seq_min, seq_max, seq_avg, earliest_date, latest_date）
- filters: 筛选条件

## 使用示例

### 示例1：分页查询第1页，每页10条
```json
{
  "action": "page_query",
  "page": 1,
  "page_size": 10
}
```

### 示例2：按日期统计seq合计，筛选2024年数据
```json
{
  "action": "date_summary",
  "page": 1,
  "page_size": 10,
  "start_date": "2024-01-01",
  "end_date": "2024-12-31"
}
```

### 示例3：获取整体汇总
```json
{
  "action": "total_summary"
}
```
