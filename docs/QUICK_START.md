# 快速开始指南

## 安装依赖

```bash
pip install -r requirements.txt
```

## 启动API服务器

```bash
python api_server.py
```

服务器将在 `http://localhost:5000` 启动。

## 测试API

### 1. 健康检查

```bash
curl http://localhost:5000/health
```

### 2. 获取所有技能

```bash
curl http://localhost:5000/api/skills
```

### 3. 生成技术文档

```bash
curl -X POST http://localhost:5000/api/writing/generate \
  -H "Content-Type: application/json" \
  -d '{"title": "测试文档", "content": "这是测试内容", "save": false}'
```

### 4. 批次计数器 - 分页查询

```bash
curl "http://localhost:5000/api/batch-counter/page?page=1&page_size=10"
```

### 5. 批次计数器 - 按日期统计

```bash
curl "http://localhost:5000/api/batch-counter/date-summary?page=1&page_size=10"
```

### 6. 批次计数器 - 整体汇总

```bash
curl "http://localhost:5000/api/batch-counter/total-summary"
```

### 7. 批次计数器 - POST通用查询

```bash
curl -X POST http://localhost:5000/api/batch-counter/query \
  -H "Content-Type: application/json" \
  -d '{"action": "date_summary", "page": 1, "page_size": 10}'
```

## Python示例

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
```

## 项目结构

```
├── api/                    # API Controller层
│   ├── controller.py       # 主控制器
│   └── controllers/        # 子控制器（按功能模块划分）
│       ├── health_controller.py
│       ├── skill_controller.py
│       ├── writing_controller.py
│       └── batch_counter_controller.py
├── agent_core/             # 技能核心模块
│   ├── skill_manager.py    # 技能管理器
│   ├── skill_executor.py   # 技能执行器（主）
│   ├── skill_executor_base.py      # 执行器基类
│   ├── skill_executor_registry.py  # 执行器注册表
│   └── agent.py            # 智能Agent
├── repository/             # Repository/DAO层
│   ├── data_repository.py  # CSV数据访问层
│   └── mssql_repository.py # SQL Server数据访问层
├── skills/                 # 技能仓库（插件式架构）
│   ├── technical-writing/  # 技术文档写作技能
│   │   ├── SKILL.md
│   │   ├── executor.py
│   │   └── assets/
│   └── batch-counter-query/ # 批次计数器查询技能
│       ├── SKILL.md
│       ├── executor.py
│       └── scripts/
├── tests/                  # 测试模块
│   ├── test_api.py         # API测试
│   └── test_batch_counter.py # 批次计数器测试
├── docs/                   # 文档目录
│   ├── ARCHITECTURE.md     # 架构文档
│   ├── API_DOCUMENTATION.md # API文档
│   ├── QUICK_START.md      # 快速开始
│   ├── AGENT_GUIDE.md      # Agent指南
│   └── INDEX.md            # 文档索引
└── api_server.py           # API服务器启动脚本
```

## 运行测试

```bash
# 运行所有测试（23个测试用例）
pytest -v

# 运行API测试
pytest tests/test_api.py -v

# 运行批次计数器测试
pytest tests/test_batch_counter.py -v

# 显示测试覆盖率
pytest --cov=. --cov-report=html
```

## 架构说明

按照 **Controller → Skill → Repository → DB** 架构设计：

- **Controller层**：API接口，按功能模块划分多个控制器
- **Skill层**：业务逻辑，插件式架构，每个Skill独立执行器
- **Repository层**：数据访问，封装CSV读取和SQL Server数据库访问
- **Data层**：数据存储，SQL Server数据库、CSV文件等

### 架构特点

- ✅ **插件式技能架构**：新增技能无需修改核心代码
- ✅ **模块化控制器**：按功能划分，易于维护
- ✅ **自动发现机制**：技能执行器自动注册
- ✅ **完整测试覆盖**：23个单元测试和集成测试全部通过

详细架构说明请参考 `docs/ARCHITECTURE.md`

## 文档导航

- **ARCHITECTURE.md** - 系统架构文档（详细架构设计）
- **API_DOCUMENTATION.md** - API接口文档（完整API说明）
- **QUICK_START.md** - 快速开始指南（本文档）
- **AGENT_GUIDE.md** - Agent使用指南（智能对话功能）
- **INDEX.md** - 文档索引（快速导航）

## 常见问题

### Q: 如何添加新技能？

A: 只需3步：
1. 创建 `skills/my-skill/` 目录
2. 创建 `SKILL.md` 和 `executor.py` 文件
3. 完成！系统自动发现并注册

### Q: 如何添加新的API接口？

A: 只需2步：
1. 创建 `api/controllers/my_controller.py`
2. 在 `api/controller.py` 中注册

### Q: 如何运行测试？

A: 运行 `pytest -v` 命令即可，详细说明见 `tests/README.md`
