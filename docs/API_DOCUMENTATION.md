# Skill API 接口文档

## 架构说明

本API按照 **Controller → Skill → Repository → DB** 架构设计：

```
Controller（API层，模块化设计）
   ├── HealthController（健康检查）
   ├── SkillController（技能管理）
   ├── WritingController（技术文档写作）
   └── BatchCounterController（批次计数器查询）
   ↓
Skill Executor Registry（执行器注册表，自动发现）
   ↓
Skill 1、Skill 2 ... Skill N（独立业务能力，插件式架构）
   ├── executor.py（独立执行器文件）
   ├── SKILL.md（技能定义）
   └── scripts/（可选脚本）
   ↓
Repository / DAO（数据访问封装）
   ├── data_repository.py（CSV数据访问）
   └── mssql_repository.py（SQL Server数据访问）
   ↓
DB / Data Files（数据存储）
```

### 架构特点

- **Controller层**：模块化设计，按功能划分多个控制器，只负责参数接收、调用Skill、返回结果
- **Skill层**：插件式架构，每个技能独立执行器文件，自动发现和注册
- **Repository层**：统一的数据访问接口，封装数据读取细节
- **数据层**：SQL Server数据库、CSV文件等数据存储

### 控制器结构

- **主控制器**：`api/controller.py` - 整合所有子控制器
- **子控制器**：`api/controllers/` - 按功能模块划分
  - `health_controller.py` - 健康检查
  - `skill_controller.py` - 技能管理
  - `writing_controller.py` - 技术文档写作
  - `batch_counter_controller.py` - 批次计数器查询

## 基础信息

- **Base URL**: `http://localhost:5000`
- **Content-Type**: `application/json`

## API 接口列表

### 1. 健康检查

**GET** `/health`

检查API服务是否正常运行。

**响应示例**:
```json
{
  "status": "ok",
  "message": "Skill API is running"
}
```

---

### 2. 获取所有技能列表

**GET** `/api/skills`

获取系统中所有可用的技能。

**响应示例**:
```json
{
  "success": true,
  "skills": [
    {
      "name": "technical-writing",
      "description": "专业技术文档写作助手，按固定规范生成Markdown格式的技术文档",
      "trigger_keywords": ["技术文档", "写文档", "Markdown写作", "文档规范"]
    },
    {
      "name": "batch-counter-query",
      "description": "批次计数器查询助手，支持对SQL Server数据库batch_counter表进行分页查询和按日期统计seq合计",
      "trigger_keywords": ["批次查询", "batch_counter", "批次计数", "seq统计", "按日期统计", "分页查询批次"]
    }
  ]
}
```

---

### 3. 执行技能（通用接口）

**POST** `/api/skills/<skill_name>/execute`

执行指定的技能。

**路径参数**:
- `skill_name`: 技能名称（如：`technical-writing`, `batch-counter-query`）

**请求体**:
```json
{
  "param1": "value1",
  "param2": "value2"
}
```

**响应示例**:
```json
{
  "success": true,
  "skill_name": "technical-writing",
  "result": {
    "success": true,
    "message": "文档已生成"
  }
}
```

**错误响应**（技能不存在）:
```json
{
  "success": false,
  "error": "技能 nonexistent-skill 执行失败或不存在"
}
```

---

## 技术文档写作接口

### 4. 生成技术文档

**POST** `/api/writing/generate`

使用技术文档写作技能生成文档。

**请求体**:
```json
{
  "title": "API使用指南",
  "content": "这是文档内容...",
  "save": true
}
```

**参数说明**:
- `title`: 文档标题（必需）
- `content`: 文档内容（必需）
- `save`: 是否保存文件（可选，默认false）

**响应示例**:
```json
{
  "success": true,
  "result": "文档已生成并保存：API使用指南.md，内容预览：..."
}
```

---

## 批次计数器查询接口

### 5. 分页查询batch_counter数据

**GET** `/api/batch-counter/page`

分页查询batch_counter表的原始数据，按时间倒序排列。

**查询参数**:
- `page`: 页码（默认1）
- `page_size`: 每页条数（默认10）
- `start_date`: 起始日期（可选，格式YYYY-MM-DD）
- `end_date`: 结束日期（可选，格式YYYY-MM-DD）


**请求示例**:
```
GET /api/batch-counter/page?page=1&page_size=10
GET /api/batch-counter/page?page=1&page_size=5&start_date=2024-01-01&end_date=2024-12-31
```

**响应示例**:
```json
{
  "success": true,
  "action": "page_query",
  "data": [
    {"id": 1, "batch_date": "2024-01-01", "seq": 5},
    {"id": 2, "batch_date": "2024-01-02", "seq": 3}
  ],
  "pagination": {
    "page": 1,
    "page_size": 10,
    "total_count": 100,
    "total_pages": 10,
    "has_next": true,
    "has_prev": false
  },
  "filters": {
    "start_date": null,
    "end_date": null
  }
}
```

---

### 6. 按日期统计seq合计

**GET** `/api/batch-counter/date-summary`

按batch_date分组，统计每天的seq合计、最小值、最大值、平均值，支持分页。

**查询参数**:
- `page`: 页码（默认1）
- `page_size`: 每页条数（默认10）
- `start_date`: 起始日期（可选，格式YYYY-MM-DD）
- `end_date`: 结束日期（可选，格式YYYY-MM-DD）


**请求示例**:
```
GET /api/batch-counter/date-summary?page=1&page_size=10
GET /api/batch-counter/date-summary?start_date=2024-01-01&end_date=2024-06-30
```

**响应示例**:
```json
{
  "success": true,
  "action": "date_summary",
  "data": [
    {
      "batch_date": "2024-01-03",
      "record_count": 1,
      "seq_total": 8,
      "seq_min": 8,
      "seq_max": 8,
      "seq_avg": 8.0
    },
    {
      "batch_date": "2024-01-02",
      "record_count": 1,
      "seq_total": 3,
      "seq_min": 3,
      "seq_max": 3,
      "seq_avg": 3.0
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 10,
    "total_count": 3,
    "total_pages": 1,
    "has_next": false,
    "has_prev": false
  },
  "filters": {
    "start_date": null,
    "end_date": null
  }
}
```

---

### 7. 获取整体汇总统计

**GET** `/api/batch-counter/total-summary`

获取batch_counter表的整体汇总信息，包括总记录数、总日期数、seq总计等。

**查询参数**:
- `start_date`: 起始日期（可选，格式YYYY-MM-DD）
- `end_date`: 结束日期（可选，格式YYYY-MM-DD）


**请求示例**:
```
GET /api/batch-counter/total-summary
GET /api/batch-counter/total-summary?start_date=2024-01-01&end_date=2024-12-31
```

**响应示例**:
```json
{
  "success": true,
  "action": "total_summary",
  "summary": {
    "total_records": 100,
    "total_dates": 50,
    "seq_grand_total": 500,
    "seq_min": 1,
    "seq_max": 15,
    "seq_avg": 5.0,
    "earliest_date": "2024-01-01",
    "latest_date": "2024-06-30"
  },
  "filters": {
    "start_date": null,
    "end_date": null
  }
}
```

---

### 8. 通用查询接口（POST）

**POST** `/api/batch-counter/query`

支持POST方式的通用查询接口，可通过action参数指定查询类型。

**请求体**:
```json
{
  "action": "page_query",
  "page": 1,
  "page_size": 10,
  "start_date": "2024-01-01",
  "end_date": "2024-12-31"

}
```

**参数说明**:
- `action`: 操作类型（默认 `page_query`）
  - `page_query`: 分页查询原始数据
  - `date_summary`: 按日期统计seq合计
  - `total_summary`: 获取整体汇总统计
- `page`: 页码（默认1）
- `page_size`: 每页条数（默认10）
- `start_date`: 起始日期（可选）
- `end_date`: 结束日期（可选）


**响应**: 根据action返回对应格式的数据（同上述GET接口）

---

## 错误处理

所有接口在出错时返回以下格式：

```json
{
  "success": false,
  "error": "错误信息描述"
}
```

HTTP状态码：
- `200`: 成功
- `400`: 请求参数错误
- `500`: 服务器内部错误

---

## 使用示例

### cURL 示例

```bash
# 健康检查
curl http://localhost:5000/health

# 获取所有技能
curl http://localhost:5000/api/skills

# 生成技术文档
curl -X POST http://localhost:5000/api/writing/generate \
  -H "Content-Type: application/json" \
  -d '{"title": "测试文档", "content": "这是测试内容", "save": false}'

# 批次计数器 - 分页查询
curl "http://localhost:5000/api/batch-counter/page?page=1&page_size=10"

# 批次计数器 - 带日期过滤的分页查询
curl "http://localhost:5000/api/batch-counter/page?page=1&page_size=5&start_date=2024-01-01&end_date=2024-12-31"

# 批次计数器 - 按日期统计
curl "http://localhost:5000/api/batch-counter/date-summary?page=1&page_size=10"

# 批次计数器 - 整体汇总
curl "http://localhost:5000/api/batch-counter/total-summary"

# 批次计数器 - POST通用查询
curl -X POST http://localhost:5000/api/batch-counter/query \
  -H "Content-Type: application/json" \
  -d '{"action": "date_summary", "page": 1, "page_size": 10}'

# 执行技能（通用接口）
curl -X POST http://localhost:5000/api/skills/technical-writing/execute \
  -H "Content-Type: application/json" \
  -d '{"title": "我的文档", "content": "文档内容"}'
```

### Python 示例

```python
import requests

base_url = "http://localhost:5000"

# 获取技能列表
response = requests.get(f"{base_url}/api/skills")
print(response.json())

# 生成技术文档
response = requests.post(
    f"{base_url}/api/writing/generate",
    json={"title": "测试文档", "content": "这是测试内容", "save": False}
)
print(response.json())

# 批次计数器 - 分页查询
response = requests.get(
    f"{base_url}/api/batch-counter/page",
    params={"page": 1, "page_size": 10}
)
print(response.json())

# 批次计数器 - 按日期统计
response = requests.get(
    f"{base_url}/api/batch-counter/date-summary",
    params={"page": 1, "page_size": 10}
)
print(response.json())

# 批次计数器 - 整体汇总
response = requests.get(f"{base_url}/api/batch-counter/total-summary")
print(response.json())

# 批次计数器 - POST通用查询
response = requests.post(
    f"{base_url}/api/batch-counter/query",
    json={
        "action": "date_summary",
        "page": 1,
        "page_size": 10,
        "start_date": "2024-01-01",
        "end_date": "2024-12-31"
    }
)
print(response.json())
```

---

## 启动服务

```bash
python api_server.py
```

服务将在 `http://localhost:5000` 启动。

---

## 测试

运行单元测试：

```bash
# 运行所有测试（23个测试用例）
pytest -v

# 运行API基础测试
pytest tests/test_api.py -v

# 运行批次计数器测试
pytest tests/test_batch_counter.py -v

# 显示测试覆盖率
pytest --cov=. --cov-report=html
```

### 测试覆盖

- **test_api.py**: 健康检查、技能列表、技能执行、技术文档生成（4个测试）
- **test_batch_counter.py**: 分页查询、日期统计、整体汇总、POST查询、集成测试（19个测试）

详细测试说明请参考 `tests/README.md`

---

## 架构优势

### 1. 模块化控制器设计

- ✅ 每个控制器职责单一，只负责一类接口
- ✅ 易于维护和扩展
- ✅ 添加新接口类型只需创建新控制器文件

### 2. 插件式技能架构

- ✅ 每个技能独立执行器文件（`executor.py`）
- ✅ 自动发现和注册机制
- ✅ 新增技能无需修改核心代码
- ✅ 支持100+技能，架构依然清晰

### 3. 完整测试覆盖

- ✅ API接口测试（`tests/test_api.py`）
- ✅ 批次计数器查询测试（`tests/test_batch_counter.py`）
- ✅ 单元测试（Mock）和集成测试（真实数据库）
- ✅ 23个测试用例全部通过

---

## 相关文档

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - 系统架构文档（详细架构设计）
- **[QUICK_START.md](QUICK_START.md)** - 快速开始指南（快速上手）
- **[AGENT_GUIDE.md](AGENT_GUIDE.md)** - Agent使用指南（智能对话功能）
- **[INDEX.md](INDEX.md)** - 文档索引（快速导航）
