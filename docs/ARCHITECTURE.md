# 系统架构文档

## 架构概述

本系统采用 **Controller → Skill → Repository → DB** 四层架构设计，实现了技能化、模块化的业务能力管理。

## 架构图

```
┌─────────────────────────────────────────────────────────┐
│              API Controller 层（主控制器）                 │
│  (api/controller.py)                                     │
│  - 整合所有子控制器                                       │
│  - 注册所有路由                                           │
└────────────────────┬──────────────────────────────────────┘
                     │
        ┌────────────┼────────────┬────────────┐
        ↓            ↓            ↓            ↓
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐
│ Health   │  │ Skill    │  │ Writing  │  │ BatchCounter │
│ Controller│ │ Controller│ │ Controller│ │ Controller   │
│          │  │          │  │          │  │              │
│ 健康检查 │  │ 技能管理 │  │ 文档写作 │  │ 批次计数查询 │
└──────────┘  └──────────┘  └──────────┘  └──────────────┘
        │            │            │            │
        └────────────┴────────────┴────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────┐
│              Skill 执行层（插件式架构）                    │
│  (agent_core/skill_executor.py)                         │
│  - 技能执行器注册表（自动发现）                           │
│  - 动态加载技能执行器                                     │
│  - 技能执行与组合                                         │
└────────────────────┬──────────────────────────────────────┘
                     │
              ┌──────┴──────┐
              ↓             ↓
       ┌──────────┐  ┌──────────────┐
       │ Executor1│  │ Executor2    │
       │          │  │              │
       │ 技术文档 │  │ 批次计数器   │
       │ 写作     │  │ 查询         │
       │          │  │              │
       │ executor │  │ executor     │
       │ .py      │  │ .py          │
       └────┬─────┘  └────┬────────┘
            │              │
            └──────┬───────┘
                   │
                   ↓
┌─────────────────────────────────────────────────────────┐
│              Repository / DAO 层                         │
│  - data_repository.py（CSV数据访问）                     │
│  - mssql_repository.py（SQL Server数据访问）             │
│  - 统一数据访问接口                                       │
└────────────────────┬──────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────┐
│                    Data 层                               │
│  - SQL Server数据库（batch_counter表）                   │
│  - CSV文件（可选）                                       │
│  - 数据库（未来扩展）                                     │
└─────────────────────────────────────────────────────────┘
```

## 目录结构

```
├── api/                          # API Controller层
│   ├── __init__.py
│   ├── controller.py             # 主控制器（整合所有子控制器）
│   └── controllers/              # 子控制器（按功能模块划分）
│       ├── __init__.py
│       ├── base_controller.py    # 基础控制器类
│       ├── health_controller.py  # 健康检查控制器
│       ├── skill_controller.py   # 技能管理控制器
│       ├── writing_controller.py # 技术文档写作控制器
│       └── batch_counter_controller.py # 批次计数器查询控制器
│
├── agent_core/                   # 智能体核心模块
│   ├── __init__.py
│   ├── skill_manager.py          # 技能管理器（发现、加载、管理）
│   ├── skill_executor.py         # 技能执行器（主执行器）
│   ├── skill_executor_base.py    # 技能执行器基类
│   ├── skill_executor_registry.py # 技能执行器注册表（自动发现）
│   └── agent.py                  # 智能Agent（对话式技能识别）
│
├── repository/                   # Repository/DAO层
│   ├── __init__.py
│   ├── data_repository.py        # CSV数据访问层
│   └── mssql_repository.py       # SQL Server数据访问层
│
├── skills/                       # 技能仓库（插件式架构）
│   ├── technical-writing/        # 技术文档写作技能
│   │   ├── SKILL.md
│   │   ├── executor.py           # 技能执行器
│   │   └── assets/
│   │       └── tech_doc_template.md
│   └── batch-counter-query/      # 批次计数器查询技能
│       ├── SKILL.md
│       ├── executor.py           # 技能执行器
│       └── scripts/
│           └── batch_counter_query.py
│
├── tests/                        # 测试模块
│   ├── __init__.py
│   ├── conftest.py               # pytest配置
│   ├── test_api.py               # API接口测试
│   └── test_batch_counter.py     # 批次计数器查询测试
│
├── docs/                         # 文档目录
│   ├── ARCHITECTURE.md           # 系统架构文档
│   ├── API_DOCUMENTATION.md      # API接口文档
│   ├── QUICK_START.md            # 快速开始指南
│   ├── AGENT_GUIDE.md            # Agent使用指南
│   └── INDEX.md                  # 文档索引
│
├── api_server.py                 # API服务器启动脚本
├── pytest.ini                    # pytest配置文件
├── requirements.txt              # 依赖清单
└── README.md                     # 项目说明文档
```

## 架构层次说明

### 1. Controller 层（API层）

**职责**：
- 接收HTTP请求
- 参数验证与转换
- 调用Skill执行器
- 返回JSON响应

**特点**：
- 极薄，不包含业务逻辑
- 只负责请求/响应的转换
- 统一的错误处理
- **模块化设计**：按功能划分多个控制器文件

**文件结构**：
- `api/controller.py` - 主控制器（整合所有子控制器）
- `api/controllers/` - 子控制器目录
  - `base_controller.py` - 基础控制器类
  - `health_controller.py` - 健康检查
  - `skill_controller.py` - 技能管理
  - `writing_controller.py` - 技术文档写作
  - `batch_counter_controller.py` - 批次计数器查询

**优势**：
- 每个控制器职责单一
- 易于维护和扩展
- 添加新接口类型只需创建新控制器文件

### 2. Skill 层（业务能力层）

**职责**：
- 实现具体的业务逻辑
- 调用Repository层获取数据
- 处理业务规则和计算

**特点**：
- 每个Skill是独立的业务单元
- 可单独测试、升级、监控
- 可被Controller、定时任务、AI Agent调用
- **插件式架构**：每个技能有独立的执行器文件

**技能列表**：
1. **technical-writing**: 技术文档写作（按固定规范生成Markdown格式的技术文档）
2. **batch-counter-query**: 批次计数器查询（SQL Server数据库分页查询、日期统计、整体汇总）

**文件结构**：
- `skills/<skill-name>/SKILL.md` - 技能定义（元数据+指令）
- `skills/<skill-name>/executor.py` - 技能执行器（继承SkillExecutorBase）
- `skills/<skill-name>/scripts/` - 技能脚本（可选）
- `skills/<skill-name>/assets/` - 技能资源（可选）

**技能执行器架构**：
- **基类**：`agent_core/skill_executor_base.py` - 定义统一接口
- **注册表**：`agent_core/skill_executor_registry.py` - 自动发现和注册
- **主执行器**：`agent_core/skill_executor.py` - 通过注册表调用执行器

**优势**：
- 新增技能无需修改核心代码
- 自动发现机制，无需手动注册
- 支持100+技能，架构依然清晰

### 3. Repository 层（数据访问层）

**职责**：
- 封装数据访问细节
- 提供统一的数据访问接口
- 处理数据读取、查询、过滤

**特点**：
- Skill只调用Repository，不直接操作文件/数据库
- 便于切换数据源（CSV → 数据库）
- 便于添加缓存、事务等

**文件**：
- `repository/data_repository.py` - CSV数据访问
- `repository/mssql_repository.py` - SQL Server数据访问（ODBC Driver 17）

### 4. Data 层（数据存储层）

**当前**：
- SQL Server数据库（Azure SQL，batch_counter表）
- CSV文件（可选）

**未来扩展**：
- 更多数据库表
- 数据仓库
- 对象存储

## 数据流示例

### 示例：批次计数器分页查询

```
1. 客户端请求
   GET /api/batch-counter/page?page=1&page_size=10
   
2. Controller层（BatchCounterController）
   - 接收请求
   - 提取查询参数（page, page_size, start_date, end_date）
   - 调用 skill_executor.call_skill("batch-counter-query", ...)
   
3. Skill执行层（SkillExecutor）
   - 从注册表获取 BatchCounterQueryExecutor
   - 激活batch-counter-query技能（加载SKILL.md）
   - 获取技能资源
   
4. Skill执行器（BatchCounterQueryExecutor）
   - 调用 executor.execute()
   - 加载技能脚本 batch_counter_query.py
   - 根据action调用相应查询函数
   
5. Repository层（MssqlRepository）
   - MssqlRepository.execute_query(sql, params)
   - 使用ODBC连接SQL Server
   - 执行分页查询SQL
   - 返回结果列表
   
6. 数据层
   - SQL Server数据库 batch_counter表
   - 返回原始数据
   
7. 响应返回
   Repository → Skill Executor → SkillExecutor → Controller → JSON响应
```

## 架构优势

### 1. 清晰的职责分离

- **Controller**: 只处理HTTP请求/响应
- **Skill**: 只处理业务逻辑
- **Repository**: 只处理数据访问
- **Data**: 只存储数据

### 2. 高可扩展性

- 新增Skill：只需在`skills/`目录下添加新技能
- 切换数据源：只需修改Repository层
- 添加API：只需在Controller中添加路由

### 3. 易于测试

- 每层可独立测试
- Skill可单独单元测试
- Repository可Mock测试
- 当前23个测试用例全部通过

### 4. 便于维护

- 修改一个Skill不影响其他Skill
- 修改数据访问不影响业务逻辑
- 修改API不影响业务逻辑

### 5. 支持未来扩展

- **工作流引擎**：编排多个Skill
- **AI Agent**：自动调用Skill
- **低代码平台**：可视化配置Skill
- **微服务拆分**：每个Skill可独立部署

## 技能管理机制

### 技能发现（三层渐进式加载）

1. **发现阶段**：扫描`skills/`目录，加载元数据（name、description、keywords）
2. **激活阶段**：按需加载完整指令（SKILL.md内容）
3. **执行阶段**：加载资源/脚本，执行具体逻辑

### 技能调用方式

1. **显式调用**：直接指定技能名
2. **自动触发**：根据关键词匹配
3. **AI识别**：使用大模型语义理解

### 技能执行器机制（插件式架构）

**自动发现流程**：
1. `SkillExecutorRegistry` 扫描 `skills/` 目录
2. 查找每个技能目录下的 `executor.py` 文件
3. 动态加载执行器类（继承自 `SkillExecutorBase`）
4. 注册到执行器注册表
5. `SkillExecutor.call_skill()` 通过注册表获取执行器并调用

**优势**：
- ✅ 新增技能：只需创建 `executor.py` 文件
- ✅ 无需修改核心代码
- ✅ 支持100+技能，架构依然清晰
- ✅ 每个技能独立开发和测试

## API设计原则

### RESTful风格

- 使用HTTP方法（GET、POST）
- 资源化URL设计
- 统一的JSON响应格式

### 错误处理

- 统一的错误响应格式
- 适当的HTTP状态码
- 清晰的错误信息

### 扩展性

- 通用技能执行接口：`/api/skills/<name>/execute`
- 专用接口：针对常用技能提供便捷接口

## 技术栈

- **Web框架**: Flask
- **数据处理**: Pandas
- **数据库**: SQL Server（通过 pyodbc + ODBC Driver 17）
- **文件处理**: openpyxl, csv
- **配置解析**: PyYAML
- **文档处理**: python-markdown
- **测试框架**: pytest, pytest-cov
- **HTTP客户端**: requests

## 部署说明

### 开发环境

```bash
# 安装依赖
pip install -r requirements.txt

# 启动API服务器
python api_server.py
```

### 生产环境

- 使用Gunicorn或uWSGI部署
- 配置Nginx反向代理
- 添加日志和监控
- 配置HTTPS

## 未来扩展方向

1. **更多技能**：在`skills/`目录下添加新技能即可
2. **缓存层**：添加Redis缓存
3. **认证授权**：添加JWT认证
4. **限流熔断**：添加API限流和熔断机制
5. **监控告警**：添加Prometheus监控
6. **工作流引擎**：支持Skill编排
7. **GraphQL支持**：提供更灵活的查询接口

## 总结

本架构遵循**单一职责原则**和**依赖倒置原则**，实现了：

- ✅ Controller层极薄，只负责请求/响应
- ✅ Skill层独立，可单独测试和升级
- ✅ Repository层统一，便于切换数据源
- ✅ 高内聚、低耦合
- ✅ 易于扩展和维护
- ✅ 支持未来向微服务、AI Agent等方向演进

这是一个**现代化、面向未来**的架构设计。
