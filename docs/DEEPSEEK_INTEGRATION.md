# DeepSeek 模型集成指南

## 📋 概述

本项目现已支持两种大模型提供商：
- **Ollama**（本地部署，免费）
- **DeepSeek**（云端API，需要API密钥）

可以通过 `.env` 文件轻松切换。

---

## 🔧 配置步骤

### 1. 安装依赖

```bash
pip install openai
```

> OpenAI SDK 已安装，用于调用 DeepSeek API

---

### 2. 获取 DeepSeek API Key

1. 访问 [DeepSeek 开放平台](https://platform.deepseek.com)
2. 注册/登录账号
3. 在控制台创建 API Key
4. 复制 API Key

---

### 3. 配置 .env 文件

打开项目根目录的 `.env` 文件，修改以下配置：

#### 切换到 DeepSeek

```env
# 设置提供商为 deepseek
LLM_PROVIDER=deepseek

# DeepSeek 配置
DEEPSEEK_API_KEY=sk-your-api-key-here  # 替换为你的真实API Key
DEEPSEEK_API_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-v4-pro

# Ollama 配置（此时可以注释掉或保留）
# LLM_API_URL=http://localhost:11434/v1/chat/completions
# LLM_MODEL=qwen2.5:3b

# 通用配置
LLM_TEMPERATURE=0.7
LLM_USE_THOUGHT=false
```

#### 切换回 Ollama

```env
# 设置提供商为 ollama
LLM_PROVIDER=ollama

# Ollama 配置
LLM_API_URL=http://localhost:11434/v1/chat/completions
LLM_MODEL=qwen2.5:3b

# DeepSeek 配置（此时可以注释掉）
# DEEPSEEK_API_KEY=sk-your-api-key-here
# DEEPSEEK_API_URL=https://api.deepseek.com
# DEEPSEEK_MODEL=deepseek-v4-pro

# 通用配置
LLM_TEMPERATURE=0.7
LLM_USE_THOUGHT=false
```

---

## 🚀 使用方法

### 方法1：通过 chat_agent.py 测试

```bash
python chat_agent.py
```

启动后会显示当前使用的提供商：

**使用 DeepSeek 时**：
```
正在初始化Agent...
提供商: DeepSeek
API地址: https://api.deepseek.com
模型名称: deepseek-v4-pro
```

**使用 Ollama 时**：
```
正在初始化Agent...
提供商: Ollama
API地址: http://localhost:11434/v1/chat/completions
模型名称: qwen2.5:3b
```

---

### 方法2：通过代码指定

```python
from agent_core.skill_manager import SkillManager
from agent_core.skill_executor import SkillExecutor
from agent_core.agent import Agent

skill_manager = SkillManager()
skill_executor = SkillExecutor(skill_manager)
skill_manager.discover_skills()

# 方式1：从环境变量读取（推荐）
agent = Agent(
    skill_manager=skill_manager,
    skill_executor=skill_executor
)

# 方式2：显式指定提供商
agent = Agent(
    skill_manager=skill_manager,
    skill_executor=skill_executor,
    provider="deepseek"  # 或 "ollama"
)
```

---

## 📊 两种提供商对比

| 特性 | Ollama | DeepSeek |
|------|--------|----------|
| **部署方式** | 本地部署 | 云端API |
| **费用** | 免费 | 按用量付费 |
| **速度** | 取决于本地硬件 | 通常较快 |
| **隐私** | 数据完全本地 | 数据发送到云端 |
| **模型选择** | 开源模型 | DeepSeek官方模型 |
| **网络要求** | 无需外网 | 需要外网 |
| **配置复杂度** | 简单 | 需要API Key |
| **适用场景** | 开发/测试/内网 | 生产环境/高性能需求 |

---

## ⚙️ 高级配置

### DeepSeek 思考过程

DeepSeek 支持推理增强模式，可以在 `.env` 中启用：

```env
LLM_USE_THOUGHT=true
```

启用后，代码会自动添加以下参数：
```python
kwargs["reasoning_effort"] = "high"
kwargs["extra_body"] = {"thinking": {"type": "enabled"}}
```

### 温度参数调整

```env
# 更确定的回答（适合精确任务）
LLM_TEMPERATURE=0.3

# 更有创造性的回答（适合创意任务）
LLM_TEMPERATURE=0.9
```

---

## 🧪 测试示例

### 测试1：单技能调用

```
你: 帮我查询批次数据

[AI分析] 正在分析用户意图...
[技能调用] batch-counter-query - 根据回复内容识别
Agent: 已为您执行技能「batch-counter-query」：
{'success': True, 'action': 'page_query', ...}
```

### 测试2：技能链调用

```
你: 我想看看最近的数据情况，最好能有个报告

[AI分析] 正在分析用户意图...
[技能链执行] 准备执行 2 个技能
[原因] 用户想查看数据并生成报告，需要查询和文档生成两个技能配合
Agent: 已为您执行技能链（2个技能）：

1. ✅ batch-counter-query: 查询最近的数据
   结果: {'success': True, ...}

2. ✅ technical-writing: 生成数据报告
   结果: # 数据报告
   ...
```

---

## ❗ 常见问题

### Q1: 提示 "DeepSeek 需要 openai SDK"

**解决方案**：
```bash
pip install openai
```

---

### Q2: 提示 "使用 DeepSeek 需要设置 DEEPSEEK_API_KEY 环境变量"

**解决方案**：
1. 检查 `.env` 文件中是否设置了 `DEEPSEEK_API_KEY`
2. 确保没有多余的空格或引号
3. 重启程序使配置生效

---

### Q3: API Key 验证失败

**可能原因**：
- API Key 错误
- API Key 已过期
- 账户余额不足

**解决方案**：
1. 登录 DeepSeek 平台检查 API Key
2. 确认账户有足够的余额
3. 重新生成 API Key

---

### Q4: 调用超时

**可能原因**：
- 网络连接问题
- DeepSeek 服务繁忙

**解决方案**：
1. 检查网络连接
2. 稍后再试
3. 考虑切换到 Ollama（本地运行）

---

### Q5: 如何在运行时动态切换？

目前不支持运行时动态切换，需要：
1. 修改 `.env` 文件中的 `LLM_PROVIDER`
2. 重启程序

未来可以考虑添加命令支持：
```
你: /switch deepseek
系统: 已切换到 DeepSeek 提供商
```

---

## 🔐 安全建议

### 1. 保护 API Key

**不要**将 API Key 提交到 Git：
```bash
# .gitignore 中应包含
.env
```

**不要**在代码中硬编码：
```python
# ❌ 错误做法
api_key = "sk-123456789"

# ✅ 正确做法
api_key = os.getenv("DEEPSEEK_API_KEY")
```

---

### 2. 定期轮换 API Key

建议每 3-6 个月更换一次 API Key：
1. 在 DeepSeek 平台生成新 Key
2. 更新 `.env` 文件
3. 删除旧 Key

---

### 3. 限制 API 使用量

在 DeepSeek 平台设置：
- 每日预算上限
- 单次请求最大 token 数
- IP 白名单（如果支持）

---

## 📝 代码实现细节

### Agent 类改动

#### 1. 导入 OpenAI SDK

```python
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
```

---

#### 2. 初始化时选择提供商

```python
self.provider = (provider or os.getenv("LLM_PROVIDER", "ollama")).lower()

if self.provider == "deepseek":
    # 初始化 DeepSeek 客户端
    self.api_key = os.getenv("DEEPSEEK_API_KEY")
    self.client = OpenAI(api_key=self.api_key, base_url=self.api_url)
else:
    # 使用 Ollama
    self.client = None
```

---

#### 3. 调用时路由到不同方法

```python
def _call_llm(self, user_message: str) -> str:
    if self.provider == "deepseek":
        return self._call_deepseek(messages)
    else:
        return self._call_ollama(messages)
```

---

#### 4. DeepSeek 专用调用方法

```python
def _call_deepseek(self, messages: List[Dict[str, str]]) -> str:
    kwargs = {
        "model": self.model,
        "messages": messages,
        "stream": False,
        "temperature": self.temperature
    }
    
    if self.use_thought:
        kwargs["reasoning_effort"] = "high"
        kwargs["extra_body"] = {"thinking": {"type": "enabled"}}
    
    response = self.client.chat.completions.create(**kwargs)
    return response.choices[0].message.content.strip()
```

---

## 🎯 最佳实践

### 开发环境

**推荐使用 Ollama**：
- 免费
- 快速迭代
- 无需网络
- 隐私安全

```env
LLM_PROVIDER=ollama
LLM_MODEL=qwen2.5:3b
```

---

### 生产环境

**推荐使用 DeepSeek**：
- 性能更好
- 稳定性高
- 专业支持
- 可扩展性强

```env
LLM_PROVIDER=deepseek
DEEPSEEK_MODEL=deepseek-v4-pro
```

---

### 混合使用

可以根据场景切换：

```python
# 日常对话使用 Ollama
agent_ollama = Agent(..., provider="ollama")

# 复杂任务使用 DeepSeek
agent_deepseek = Agent(..., provider="deepseek")
```

---

## 📈 性能优化建议

### 1. 缓存常用响应

对于重复的问题，可以缓存响应：
```python
cache = {}
if user_message in cache:
    return cache[user_message]
```

---

### 2. 批量处理

如果需要处理多个请求，考虑批量调用：
```python
responses = []
for message in messages:
    response = agent.chat(message)
    responses.append(response)
```

---

### 3. 异步调用

对于高并发场景，使用异步：
```python
import asyncio

async def chat_async(message):
    # 异步调用逻辑
    pass
```

---

## 🔮 未来规划

### 短期（1-2周）

- [ ] 添加更多模型提供商支持（如 OpenAI、Claude）
- [ ] 支持运行时动态切换提供商
- [ ] 添加提供商健康检查

---

### 中期（1-2月）

- [ ] 智能路由：根据任务复杂度自动选择提供商
- [ ] 负载均衡：多个提供商之间分配请求
- [ ] 成本优化：自动选择性价比最高的提供商

---

### 长期（3-6月）

- [ ] 模型微调：针对特定任务优化模型
- [ ] 多模型融合：结合多个模型的输出
- [ ] 自定义模型：训练专属模型

---

## ✨ 总结

### 核心优势

✅ **灵活切换** - 一行配置即可切换提供商  
✅ **透明使用** - 上层代码无需修改  
✅ **易于扩展** - 可轻松添加新的提供商  
✅ **向后兼容** - 默认使用 Ollama，不影响现有功能  

---

### 关键文件

- `.env` - 配置文件
- `.env.example` - 配置模板
- `agent_core/agent.py` - Agent 核心逻辑
- `chat_agent.py` - 交互式对话程序

---

### 快速开始

1. **安装依赖**：`pip install openai`
2. **配置 .env**：设置 `LLM_PROVIDER=deepseek` 和 `DEEPSEEK_API_KEY`
3. **运行测试**：`python chat_agent.py`
4. **开始对话**：输入你的问题

---

**更新日期**: 2026年5月  
**状态**: ✅ 已完成  
**版本**: v1.0
