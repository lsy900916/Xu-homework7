# Agent Skills 系统

这是一个基于 Python 的 Agent Skills 功能演示项目，实现了渐进式加载、技能定义与调用、技能组合等核心功能。

## ✨ 核心特性

- 🚀 **插件式技能架构** - 支持无限扩展，新增技能无需修改核心代码
- 🏗️ **模块化控制器设计** - 按功能模块划分，易于维护和扩展
- 🔍 **自动发现机制** - 技能执行器自动注册，无需手动配置
- 📡 **RESTful API** - 提供完整的API接口，支持多种调用方式
- 🤖 **智能Agent** - 通过对话自动识别并执行技能
- ✅ **完整测试覆盖** - 单元测试和集成测试（23个测试用例全部通过）

## 项目结构

```
├── agent_core/              # 智能体核心模块
│   ├── __init__.py
│   ├── skill_manager.py     # 技能发现、加载、管理核心逻辑
│   ├── skill_executor.py    # 技能执行、组合、触发逻辑（主执行器）
│   ├── skill_executor_base.py      # 技能执行器基类
│   ├── skill_executor_registry.py  # 技能执行器注册表（自动发现）
│   └── agent.py             # 智能Agent（对话式技能识别）
│
├── api/                     # API Controller层
│   ├── __init__.py
│   ├── controller.py        # 主控制器（整合所有子控制器）
│   └── controllers/         # 子控制器（按功能模块划分）
│       ├── __init__.py
│       ├── base_controller.py      # 基础控制器类
│       ├── health_controller.py    # 健康检查控制器
│       ├── skill_controller.py     # 技能管理控制器
│       ├── writing_controller.py   # 技术文档写作控制器
│       ├── batch_counter_controller.py # 批次计数器查询控制器
│       └── order_management_controller.py # 订单管理API控制器
│
├── repository/              # Repository/DAO层
│   ├── __init__.py
│   ├── data_repository.py   # CSV数据访问层
│   └── mssql_repository.py  # SQL Server数据访问层
│
├── skills/                  # 技能仓库（插件式架构）
│   ├── technical-writing/   # 技术文档写作技能
│   │   ├── SKILL.md
│   │   ├── executor.py     # 技能执行器
│   │   └── assets/
│   ├── batch-counter-query/ # 批次计数器查询技能
│   │   ├── SKILL.md
│   │   ├── executor.py      # 技能执行器
│   │   └── scripts/
│   │       └── batch_counter_query.py
│   └── order-management/    # 订单管理技能
│       ├── SKILL.md         # 技能元数据和使用规范
│       ├── executor.py      # 技能执行器
│       └── scripts/
│           └── order_management.py # 核心业务逻辑实现
│
├── tests/                   # 测试模块
│   ├── __init__.py
│   ├── conftest.py          # pytest配置
│   ├── test_api.py          # API接口测试（健康检查、技能管理、文档写作）
│   └── test_batch_counter.py # 批次计数器查询API测试（Mock+集成测试）
│
├── docs/                    # 文档目录
│   ├── ARCHITECTURE.md      # 系统架构文档
│   ├── API_DOCUMENTATION.md # API接口文档
│   ├── QUICK_START.md       # 快速开始指南
│   ├── AGENT_GUIDE.md       # Agent使用指南
│   └── INDEX.md             # 文档索引
│
├── api_server.py            # API服务器启动脚本
├── pytest.ini              # pytest配置文件
├── requirements.txt         # 依赖清单
└── README.md                # 项目说明文档
```

## 快速开始

### 1. 安装依赖

创建虚拟环境

```
python 3.11以上
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

backend中 生成一个.env文件

```

```bash
pip install -r requirements.txt
```

### 2. 启动API服务器

```bash
python api_server.py
```

### 3. 运行测试

```bash
pytest -v
```

## 功能说明

### 核心功能

1. **三层渐进式加载**
   - 第一层：发现阶段（仅加载元数据）
   - 第二层：激活阶段（加载完整指令）
   - 第三层：执行阶段（加载资源/脚本）

2. **技能定义与调用**
   - 显式调用：直接指定技能名执行
   - 自动触发：根据用户查询自动匹配技能

3. **技能组合**
   - 支持多个技能按顺序执行
   - 支持数据在技能间流转

### 当前技能

- **technical-writing**: 技术文档写作助手（按固定规范生成Markdown格式的技术文档）
- **batch-counter-query**: 批次计数器查询助手（支持对SQL Server数据库batch_counter表进行分页查询和按日期统计seq合计）
- **order-management**: 订单管理助手，支持订单的查询、创建、状态更新和统计分析。当用户要查询订单(list_orders)、创建订单(create_order)、查看订单详情(get_order_detail)、更新订单状态(update_order_status)、统计订单数据(order_statistics)时调用。

### 架构特点

- **插件式技能架构**：每个技能独立文件，支持无限扩展
- **分层控制器设计**：按功能模块划分，易于维护
- **自动发现机制**：技能执行器自动注册，无需手动配置
- **RESTful API**：提供完整的API接口，支持多种调用方式

## 使用示例

### 基础使用（显式调用技能）

```python
from agent_core.skill_manager import SkillManager
from agent_core.skill_executor import SkillExecutor

# 初始化
skill_manager = SkillManager()
skill_executor = SkillExecutor(skill_manager)

# 发现技能
skill_manager.discover_skills()

# 显式调用技能 - 生成技术文档
skill_executor.call_skill(
    "technical-writing",
    title="我的文档",
    content="文档内容",
    save=True
)

# 显式调用技能 - 批次计数器查询
skill_executor.call_skill(
    "batch-counter-query",
    action="page_query",
    page=1,
    page_size=10
)

# 自动触发技能
skill_executor.auto_trigger_skill("帮我写一份技术文档")

# 技能组合
skill_executor.call_skill_chain(
    ["batch-counter-query", "technical-writing"],
    action="date_summary",
    title="批次统计报告",
    save=True
)
```

### 智能Agent对话（推荐）

使用大模型自动识别技能并执行：

```python
from agent_core.skill_manager import SkillManager
from agent_core.skill_executor import SkillExecutor
from agent_core.agent import Agent

# 初始化
skill_manager = SkillManager()
skill_executor = SkillExecutor(skill_manager)
skill_manager.discover_skills()

# 创建Agent（配置从 .env 文件自动读取）
agent = Agent(
    skill_manager=skill_manager,
    skill_executor=skill_executor
    # api_url, model, use_thought, temperature 等参数从 .env 文件自动读取
)

# 也可以手动指定参数覆盖环境变量
# agent = Agent(
#     skill_manager=skill_manager,
#     skill_executor=skill_executor,
#     api_url="http://localhost:11434/v1/chat/completions",
#     model="qwen2.5:3b",
#     use_thought=False,
#     temperature=0.7
# )

# 通过对话自动识别并执行技能
response = agent.chat("帮我查询一下批次计数器的数据")
print(response)
```

### API接口调用

启动API服务器：

```bash
python api_server.py
```

然后可以通过HTTP请求调用技能：

```bash
# 获取所有技能
curl http://localhost:5000/api/skills

# 执行技能（通用接口）
curl -X POST http://localhost:5000/api/skills/technical-writing/execute \
  -H "Content-Type: application/json" \
  -d '{"title": "测试文档", "content": "文档内容"}'

# 生成技术文档
curl -X POST http://localhost:5000/api/writing/generate \
  -H "Content-Type: application/json" \
  -d '{"title": "API使用指南", "content": "这是文档内容..."}'

# 批次计数器分页查询
curl "http://localhost:5000/api/batch-counter/page?page=1&page_size=10"

# 批次计数器按日期统计
curl "http://localhost:5000/api/batch-counter/date-summary?page=1&page_size=10"

# 批次计数器整体汇总
curl "http://localhost:5000/api/batch-counter/total-summary"

# 批次计数器通用POST查询
curl -X POST http://localhost:5000/api/batch-counter/query \
  -H "Content-Type: application/json" \
  -d '{"action": "date_summary", "page": 1, "page_size": 10}'

# 订单管理：查询订单列表
curl "http://localhost:5000/api/orders/list?page=1&page_size=10"

# 订单管理：获取订单详情
curl "http://localhost:5000/api/orders/detail/ORD20260623006"

# 订单管理：创建新订单
curl -X POST http://localhost:5000/api/orders/create \
  -H "Content-Type: application/json" \
  -d '{"customer_name": "测试用户", "customer_phone": "13800138000", "items": [{"name": "测试商品", "quantity": 1, "price": 99.0}]}'

# 订单管理：更新订单状态
curl -X PUT http://localhost:5000/api/orders/update-status/ORD20260623006 \
  -H "Content-Type: application/json" \
  -d '{"new_status": "paid"}'

# 订单管理：订单统计分析
curl "http://localhost:5000/api/orders/statistics?group_by=status"
```

详细API文档请参考 `docs/API_DOCUMENTATION.md`

## Agent 功能说明

### 智能技能识别

Agent 使用两种方式识别技能：

1. **快速匹配**：基于关键词的快速匹配（优先使用）
2. **AI 识别**：使用大模型进行语义理解和意图识别

### Agent 配置

Agent 支持两种大模型提供商：**Ollama**（本地）和 **DeepSeek**（云端）。

#### 配置参数

从 `.env` 文件中自动读取以下配置：

- `LLM_PROVIDER`: 大模型提供商（ollama 或 deepseek，默认: ollama）
- `LLM_API_URL`: Ollama API地址（当 LLM_PROVIDER=ollama 时）
- `LLM_MODEL`: Ollama 模型名称（当 LLM_PROVIDER=ollama 时）
- `DEEPSEEK_API_KEY`: DeepSeek API密钥（当 LLM_PROVIDER=deepseek 时）
- `DEEPSEEK_API_URL`: DeepSeek API地址（当 LLM_PROVIDER=deepseek 时）
- `DEEPSEEK_MODEL`: DeepSeek 模型名称（当 LLM_PROVIDER=deepseek 时）
- `LLM_TEMPERATURE`: 温度参数（0-1，越低越确定）
- `LLM_USE_THOUGHT`: 是否启用思考过程

#### 快速切换提供商

只需修改 `.env` 文件中的一行配置：

```env
# 使用 Ollama（本地，免费）
LLM_PROVIDER=ollama
LLM_MODEL=qwen2.5:3b

# 或使用 DeepSeek（云端，高性能）
LLM_PROVIDER=deepseek
DEEPSEEK_MODEL=deepseek-v4-pro
```

详见 [DeepSeek 集成指南](DEEPSEEK_INTEGRATION.md)

```python
# 方式1：使用默认配置（从 .env 文件读取）
agent = Agent(
    skill_manager=skill_manager,
    skill_executor=skill_executor
)

# 方式2：手动指定参数（覆盖 .env 配置）
agent = Agent(
    skill_manager=skill_manager,
    skill_executor=skill_executor,
    api_url="http://localhost:11434/v1/chat/completions",
    model="qwen2.5:3b",
    use_thought=False,
    temperature=0.7
)
```

### 对话示例

启动chat_agent服务：

```bash
python chat_agent.py
```

```
你: 帮我查询一下批次计数器的数据
Agent: 已为您执行技能「batch-counter-query」：...

你: 帮我写一份技术文档
Agent: 已为您执行技能「technical-writing」：...

你: 介绍一下德国
Agent: 德国是位于中欧的国家...

你: 帮我解析一下 upload/demo.xlsx 文件

Agent: [执行 excel-import-parse 技能]
       已为您执行技能「excel-import-parse」：
       {'success': True, 'file_path': 'upload/demo.xlsx', ...}

你: 查询所有已支付的订单
Agent: 已为您执行技能「order-management」：查询到3条已支付的订单...

你: 查看订单ORD20260618006的详情
Agent: 已为您执行技能「order-management」：订单详情如下...

你: 将订单ORD20260618006的状态改为已支付
Agent: 已为您执行技能「order-management」：订单状态已更新：待支付 → 已支付

你: 统计一下本月的订单数据
Agent: 已为您执行技能「order-management」：本月共创建订单15个，总金额¥15,000.00...


```

## 测试

运行单元测试：

```bash
# 运行所有测试（23个测试用例）
pytest -v

# 运行API测试
pytest tests/test_api.py -v

# 运行批次计数器测试
pytest tests/test_batch_counter.py -v

# 显示覆盖率
pytest --cov=. --cov-report=html
```

### 测试覆盖

- `tests/test_api.py` - API基础测试（健康检查、技能列表、技能执行、文档生成）
- `tests/test_batch_counter.py` - 批次计数器查询测试（分页查询、日期统计、整体汇总、POST查询、集成测试）

详细测试说明请参考 `tests/README.md`

- `tests/test_api.py` 中的TestOrderManagementAPI类包含了订单管理模块的完整API测试（创建订单、查询列表、获取详情、更新状态、统计分析、参数兜底逻辑共6个测试用例）

## 文档

所有文档位于 `docs/` 目录：

- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** - 系统架构文档（详细架构设计）
- **[docs/API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md)** - API接口文档（完整API说明）
- **[docs/QUICK_START.md](docs/QUICK_START.md)** - 快速开始指南（快速上手）
- **[docs/AGENT_GUIDE.md](docs/AGENT_GUIDE.md)** - Agent使用指南（智能对话功能）
- **[docs/INDEX.md](docs/INDEX.md)** - 文档索引（快速导航）

## 注意事项

- 确保已安装所有依赖包（包括 `requests`、`flask`、`pytest`、`pyodbc`）
- 批次计数器查询技能需要能够连接到SQL Server数据库
- 技能目录结构必须包含 SKILL.md 文件（包含 YAML 元数据）
- 每个技能需要实现 `executor.py` 文件（继承 `SkillExecutorBase`）
- 使用 Agent 功能需要确保大模型 API 可访问
- 如果 API 不可用，可以使用基础的关键词匹配功能

## 架构优势

- ✅ **插件式设计**：新增技能无需修改核心代码
- ✅ **自动发现**：技能执行器自动注册
- ✅ **分层清晰**：Controller → Skill → Repository → DB
- ✅ **易于测试**：完整的单元测试覆盖（23个测试用例全部通过）
- ✅ **易于扩展**：支持100+技能，架构依然清晰
