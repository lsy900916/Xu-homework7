# Agent 使用指南

## 概述

Agent 是一个智能对话系统，能够通过自然语言对话自动识别用户意图并调用相应的技能。

## 核心特性

1. **双重识别机制**
   - 快速关键词匹配（优先）
   - AI 语义理解（备用）

2. **自动参数提取**
   - 从用户输入中智能提取技能所需参数
   - 支持文件路径、数值等参数识别

3. **对话上下文**
   - 保留最近5轮对话历史
   - 支持多轮对话交互

## 当前支持的技能

1. **technical-writing**（技术文档写作）
   - 关键词：技术文档、写文档、Markdown写作、文档规范
   - 按固定规范生成Markdown格式的技术文档

2. **batch-counter-query**（批次计数器查询）
   - 关键词：批次查询、batch_counter、批次计数、seq统计、按日期统计
   - 支持分页查询、按日期统计、整体汇总

## 快速开始

### 1. 基础使用

```python
from agent_core.skill_manager import SkillManager
from agent_core.skill_executor import SkillExecutor
from agent_core.agent import Agent

# 初始化技能系统
skill_manager = SkillManager()
skill_executor = SkillExecutor(skill_manager)
skill_manager.discover_skills()

# 创建Agent（配置从 .env 文件自动读取）
agent = Agent(
    skill_manager=skill_manager,
    skill_executor=skill_executor
)

# 开始对话
response = agent.chat("帮我查询一下批次计数器的数据")
print(response)
```

### 2. 交互式对话

```bash
python chat_agent.py
```

运行后会进入交互模式，直接输入自然语言即可。

### 3. 测试Agent

```bash
python test_agent.py
```

## 配置说明

### API 配置

Agent 的配置参数从 `.env` 文件中自动读取：

```python
# 方式1：使用默认配置（推荐）
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

**环境变量配置（.env 文件）：**
```env
LLM_API_URL=http://localhost:11434/v1/chat/completions
LLM_MODEL=qwen2.5:3b
LLM_TEMPERATURE=0.7
LLM_USE_THOUGHT=false
```

**参数说明：**
- `api_url`: 大模型API地址
- `model`: 使用的模型名称
- `use_thought`: 
  - `True`: 启用思考过程（有思考过程）
  - `False`: 禁用思考过程（无思考过程，更快）
- `temperature`: 0-1之间的浮点数，控制回复的随机性
  - 较低值（0.1-0.3）：更确定、更一致
  - 较高值（0.7-1.0）：更随机、更有创造性

### 思考过程模式

根据你的API支持情况选择：

**有思考过程（use_thought=True）**
```bash
curl http://localhost:11434/api/chat \
  -d '{
    "model": "qwen3.5:9b",
    "messages": [{"role": "user", "content": "介绍一下德国!"}]
  }'
```

**无思考过程（use_thought=False，推荐）**
```bash
curl http://localhost:11434/api/chat \
  -d '{
    "model": "qwen3.5:9b",
    "messages": [{"role": "user", "content": "介绍一下德国!"}],
    "stream": false,
    "temperature": 0,
    "skip_thought": true
  }'
```

## 使用示例

### 示例1：查询批次数据

```
你: 帮我查询一下批次计数器的数据

Agent: 已为您执行技能「batch-counter-query」：
共100条记录，当前第1页...
```

### 示例2：写技术文档

```
你: 帮我写一份技术文档，标题是API使用指南

Agent: 已为您执行技能「technical-writing」：
文档已生成...
```

### 示例3：普通对话

```
你: 介绍一下德国

Agent: 德国是位于中欧的国家，是欧盟最大的经济体之一...
```

### 示例4：技能组合

```
你: 先查询批次数据，然后生成一份技术文档

Agent: [自动执行技能链]
```

## 技能识别流程

1. **快速匹配**（优先）
   - 检查用户输入中的关键词
   - 匹配技能名称、描述、触发关键词
   - 如果匹配成功，立即执行

2. **AI识别**（备用）
   - 调用大模型API
   - 分析用户意图
   - 解析返回的JSON指令
   - 执行相应技能或普通对话

## 参数提取规则

Agent 会自动从用户输入中提取参数：

- **文件路径**：识别 `.xlsx`、`.csv` 等文件扩展名
- **数值参数**：识别"每小时20元"等数值
- **文本参数**：识别"标题：xxx"等格式

## 故障排除

### API 连接失败

如果大模型API不可用，Agent会自动降级到关键词匹配模式。

### 技能识别不准确

1. 检查技能的关键词配置
2. 调整 `temperature` 参数
3. 在用户输入中使用更明确的关键词

### 参数提取失败

在用户输入中明确指定参数，例如：
- "标题是 我的文档"
- "查询第2页，每页5条"

## 高级功能

### 重置对话历史

```python
agent.reset_conversation()
```

### 自定义系统提示词

修改 `agent_core/agent.py` 中的 `_build_system_prompt()` 方法。

### 扩展参数提取

修改 `agent_core/agent.py` 中的 `_extract_skill_params()` 方法。

## 注意事项

1. 确保大模型API可访问
2. 技能必须在 `discover_skills()` 之后才能被识别
3. 文件路径建议使用绝对路径
4. 对话历史会保留最近5轮，避免上下文过长
