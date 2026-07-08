# API 测试文档

## 1. 测试目标

本项目的 API 测试用于验证以下核心能力：

- 健康检查接口是否可用
- 用户登录、Token 刷新与权限控制是否正确
- 技能列表、技能执行与文档生成接口是否稳定
- 订单管理技能相关接口是否满足业务预期
- 批次计数器查询接口的分页、汇总与日期统计逻辑是否正确
- Excel 文件上传与解析接口是否满足格式校验和数据提取要求

## 2. 当前测试套件

当前测试目录包含 3 组测试文件：

```text
tests/
├── conftest.py               # pytest 配置与共享 fixture
├── test_api.py               # API 基础接口测试（13 个）
├── test_batch_counter.py     # 批次计数器接口测试（19 个）
└── test_excel_import.py      # Excel 导入接口测试（2 个）
```

### 测试文件覆盖情况

- test_api.py：13 个测试
  - 健康检查
  - 技能列表
  - 用户登录与刷新
  - 受保护接口鉴权
  - 技能执行错误处理
  - 文档生成
  - 订单管理 5 大核心场景

- test_batch_counter.py：19 个测试
  - Mock 单元测试 14 个
  - 集成测试 5 个

- test_excel_import.py：2 个测试
  - Excel 上传与解析
  - 非 Excel 文件拒绝

### 当前总计

- 共 34 个测试用例
- 结果：全部通过

## 3. 运行方式

### 运行全部测试

```bash
pytest -q
```

### 运行单个测试文件

```bash
pytest tests/test_api.py -q
pytest tests/test_batch_counter.py -q
pytest tests/test_excel_import.py -q
```

### 运行指定测试类或方法

```bash
pytest tests/test_api.py::TestHealthAPI -q
pytest tests/test_batch_counter.py::TestBatchCounterIntegration -q
pytest tests/test_api.py::TestOrderManagementAPI::test_create_order -q
```

### 生成覆盖率报告

```bash
pytest --cov=. --cov-report=html
```

### 生成 JUnit XML 测试报告

```bash
pytest --junitxml=tests/reports/pytest-results.xml -q
```

## 4. 最新执行结果

已在当前环境中实际执行完成，结果如下：

```text
34 passed, 39 warnings in 10.56s
```

### 生成的报告文件

- 测试报告说明：[tests/API_TEST_REPORT.md](API_TEST_REPORT.md)
- JUnit XML 报告：[tests/reports/pytest-results.xml](reports/pytest-results.xml)

## 5. 说明与注意事项

1. 批次计数器集成测试会访问当前环境中的数据源，若相关依赖不可用，需检查数据库配置。
2. 认证测试会在临时目录下初始化 SQLite 数据库，默认不会污染正式环境。
3. Excel 测试会在临时目录写入上传文件，并在测试结束后由测试逻辑处理。
4. 当前测试输出中包含 39 条 warnings，属于非阻塞信息，建议后续逐项排查。

## 6. 建议的后续优化

- 将警告逐项收敛，减少测试输出噪音
- 为 CI/CD 增加自动执行步骤
- 补充针对失败场景的异常断言测试
- 增加接口性能与并发测试场景
