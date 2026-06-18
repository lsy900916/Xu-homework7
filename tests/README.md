# 测试文档

## 运行测试

### 运行所有测试

```bash
pytest -v
```

### 运行特定测试文件

```bash
pytest tests/test_api.py -v
pytest tests/test_batch_counter.py -v
```

### 运行特定测试类

```bash
pytest tests/test_api.py::TestHealthAPI
pytest tests/test_batch_counter.py::TestBatchCounterPageAPI
```

### 运行特定测试方法

```bash
pytest tests/test_api.py::TestHealthAPI::test_health_check
pytest tests/test_batch_counter.py::TestBatchCounterIntegration::test_real_page_query
```

### 显示详细输出

```bash
pytest -v
```

### 显示覆盖率

```bash
pytest --cov=. --cov-report=html
```

## 测试结构

```
tests/
├── __init__.py
├── conftest.py                  # pytest配置和共享fixtures
├── test_api.py                  # API基础接口测试（健康检查、认证、技能管理）
├── test_batch_counter.py        # 批次计数器查询API测试（Mock+集成测试）
└── test_excel_import.py         # Excel导入解析测试
```

## 测试覆盖

### API基础测试 (test_api.py) - 7个测试

- ✅ 健康检查接口 (`TestHealthAPI::test_health_check`)
- ✅ 技能列表接口 (`TestSkillsAPI::test_list_skills`)
- ✅ 用户登录成功 (`TestAuthAPI::test_login_success`)
- ✅ Token刷新成功 (`TestAuthAPI::test_refresh_success`)
- ✅ 无Token访问受保护API (`TestAuthAPI::test_protected_api_without_token`)
- ✅ 技能执行接口 - 不存在的技能错误处理 (`TestSkillExecuteAPI::test_execute_nonexistent_skill`)
- ✅ 技术文档写作接口 (`TestTechnicalWritingAPI::test_generate_document`)

### 批次计数器查询测试 (test_batch_counter.py) - 19个测试

**分页查询测试 (`TestBatchCounterPageAPI`) - Mock**
- ✅ 默认分页查询 (`test_page_query_default`)
- ✅ 指定页码和每页条数 (`test_page_query_with_pagination`)
- ✅ 带日期过滤的分页查询 (`test_page_query_with_date_filter`)
- ✅ 分页信息结构完整性 (`test_page_query_pagination_info`)

**按日期统计测试 (`TestBatchCounterDateSummaryAPI`) - Mock**
- ✅ 默认日期统计 (`test_date_summary_default`)
- ✅ 日期统计数据结构验证 (`test_date_summary_data_structure`)
- ✅ 带日期过滤的统计 (`test_date_summary_with_date_filter`)

**整体汇总测试 (`TestBatchCounterTotalSummaryAPI`) - Mock**
- ✅ 默认整体汇总 (`test_total_summary_default`)
- ✅ 汇总数据结构验证 (`test_total_summary_structure`)
- ✅ 带日期过滤的整体汇总 (`test_total_summary_with_date_filter`)

**POST通用查询测试 (`TestBatchCounterPostAPI`) - Mock**
- ✅ POST方式分页查询 (`test_post_page_query`)
- ✅ POST方式日期统计 (`test_post_date_summary`)
- ✅ POST方式整体汇总 (`test_post_total_summary`)
- ✅ 不指定action时默认为page_query (`test_post_default_action`)

**集成测试 (`TestBatchCounterIntegration`) - 真实数据库**
- ✅ 分页查询真实数据 (`test_real_page_query`)
- ✅ 按日期统计真实数据 (`test_real_date_summary`)
- ✅ 整体汇总真实数据 (`test_real_total_summary`)
- ✅ 带日期过滤的分页查询 (`test_real_page_query_with_date_filter`)
- ✅ POST通用查询 (`test_real_post_query`)

### Excel导入测试 (test_excel_import.py) - 2个测试

- ✅ Excel文件上传和解析 (`test_excel_import_upload_and_parse`)
- ✅ 拒绝非Excel文件 (`test_excel_import_rejects_non_excel`)

## 测试总计

- **总计：28个测试用例，全部通过** ✅
- API基础测试：7个
  - 健康检查：1个
  - 技能管理：1个
  - 认证授权：3个（登录、刷新、权限验证）
  - 技能执行：2个
- 批次计数器查询测试：19个
  - 单元测试（Mock）：14个
  - 集成测试（真实数据库）：5个
- Excel导入测试：2个

**最新测试结果** (2026年5月):
```
28 passed, 46 warnings in 20.90s
```

### 测试分类统计

| 测试文件 | 测试数量 | 类型 | 说明 |
|---------|---------|------|------|
| test_api.py | 7 | API测试 | 健康检查、认证、技能管理 |
| test_batch_counter.py | 19 | Mock + 集成 | 批次计数器查询（14个Mock + 5个真实DB） |
| test_excel_import.py | 2 | API测试 | Excel文件上传和解析 |
| **总计** | **28** | - | **全部通过** ✅ |

### 测试覆盖的功能模块

- ✅ **健康检查** - API服务状态监控
- ✅ **用户认证** - 登录、Token刷新、权限验证
- ✅ **技能管理** - 技能列表、技能执行
- ✅ **技术文档写作** - Markdown文档生成
- ✅ **批次计数器查询** - 分页查询、日期统计、整体汇总
- ✅ **Excel导入解析** - 文件上传、内容解析、格式验证

## 注意事项

1. **批次计数器集成测试**需要能够连接到SQL Server数据库
2. **单元测试使用Mock**，不依赖真实数据库连接
3. **测试使用Flask的测试客户端**，不会启动实际服务器
4. **Excel导入测试**需要上传测试文件，会自动清理临时文件
5. **认证测试**使用SQLite用户数据库，首次运行会自动初始化默认用户

## CI/CD集成

可以在CI/CD流程中运行测试：

```yaml
# 示例 GitHub Actions
- name: Run tests
  run: |
    pip install -r requirements.txt
    pytest -v --cov=. --cov-report=xml
```
