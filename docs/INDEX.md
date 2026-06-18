# 文档索引

欢迎使用 Agent Skills 系统！本文档索引帮助您快速找到所需信息。

## 📚 文档导航

### 🚀 快速开始

- **[QUICK_START.md](QUICK_START.md)** - 快速开始指南
  - 安装依赖
  - 启动API服务器
  - 测试API接口
  - 运行测试

### 🏗️ 架构设计

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - 系统架构文档
  - 架构概述和架构图
  - 四层架构设计（Controller → Skill → Repository → DB）
  - 技能执行器插件式架构
  - 控制器模块化设计
  - 数据流示例
  - 技术栈和部署说明

### 📡 API接口

- **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** - API接口文档
  - 完整的API接口列表（8个接口）
  - 技术文档写作接口
  - 批次计数器查询接口（分页查询、日期统计、整体汇总、通用POST查询）
  - 请求/响应示例
  - 错误处理说明
  - 使用示例（cURL和Python）

### 🤖 Agent功能

- **[AGENT_GUIDE.md](AGENT_GUIDE.md)** - Agent使用指南
  - 智能对话功能
  - 技能自动识别（technical-writing、batch-counter-query）
  - Agent配置说明
  - 对话示例

## 🎯 按需查找

### 我想...

**快速上手**
→ 阅读 [QUICK_START.md](QUICK_START.md)

**了解系统架构**
→ 阅读 [ARCHITECTURE.md](ARCHITECTURE.md)

**调用API接口**
→ 阅读 [API_DOCUMENTATION.md](API_DOCUMENTATION.md)

**使用智能对话**
→ 阅读 [AGENT_GUIDE.md](AGENT_GUIDE.md)

**添加新技能**
→ 参考 [ARCHITECTURE.md](ARCHITECTURE.md) 中的"技能执行器机制"部分

**添加新API接口**
→ 参考 [ARCHITECTURE.md](ARCHITECTURE.md) 中的"Controller层"部分

**运行测试**
→ 参考 [QUICK_START.md](QUICK_START.md) 中的"运行测试"部分

## 📖 核心概念

### 架构层次

1. **Controller层** - API接口层，按功能模块划分
2. **Skill层** - 业务能力层，插件式架构
3. **Repository层** - 数据访问层，统一接口
4. **Data层** - 数据存储层，SQL Server数据库/CSV文件

### 当前技能

1. **technical-writing** - 技术文档写作助手
2. **batch-counter-query** - 批次计数器查询助手（SQL Server数据库）

### 核心机制

- **三层渐进式加载**：发现 → 激活 → 执行
- **插件式技能架构**：自动发现和注册
- **模块化控制器**：按功能划分，易于维护

## 🔗 相关资源

- **项目根目录** - `README.md` - 项目总览
- **测试文档** - `tests/README.md` - 测试说明

## 📝 文档更新

文档会随着项目发展持续更新，请定期查看最新版本。

---

**提示**：建议按以下顺序阅读：
1. QUICK_START.md（快速上手）
2. ARCHITECTURE.md（理解架构）
3. API_DOCUMENTATION.md（使用API）
4. AGENT_GUIDE.md（高级功能）
