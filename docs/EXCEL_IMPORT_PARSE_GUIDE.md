# Excel Import Parse 技能使用指南

## 📋 技能概述

**excel-import-parse** 是一个 Excel 文件解析技能，能够将上传的 Excel 文件（`.xlsx`/`.xls`）解析为 JSON 格式的数据，方便后续处理或展示。

---

## 🎯 使用时机

当您需要：
- ✅ 解析上传到 `upload/` 目录的 Excel 文件
- ✅ 将 Excel 数据转换为 JSON 格式
- ✅ 查看 Excel 文件的内容和结构
- ✅ 提取特定工作表的数据
- ✅ 限制返回的行数（避免大数据量）

---

## 📥 输入参数

### 必需参数

| 参数 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `file_path` | string | Excel 文件路径（通常在 `upload/` 目录） | `"upload/demo.xlsx"` |

---

### 可选参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `sheet_name` | string | `null` | 工作表名称；不传则解析所有工作表 |
| `max_rows` | integer | `200` | 每个工作表最多返回的行数（1-2000） |

---

## 📤 输出格式

### 成功响应

```json
{
  "success": true,
  "file_path": "upload/demo.xlsx",
  "max_rows": 200,
  "sheets": {
    "Sheet1": {
      "columns": ["姓名", "年龄", "城市"],
      "rows": [
        {"姓名": "张三", "年龄": 25, "城市": "北京"},
        {"姓名": "李四", "年龄": 30, "城市": "上海"}
      ]
    },
    "Sheet2": {
      "columns": ["产品", "价格"],
      "rows": [
        {"产品": "苹果", "价格": 5.5},
        {"产品": "香蕉", "价格": 3.2}
      ]
    }
  }
}
```

---

### 失败响应

```json
{
  "success": false,
  "error": "文件不存在: upload/missing.xlsx"
}
```

或者（工作表不存在时）：

```json
{
  "success": false,
  "error": "工作表不存在: Sheet3",
  "available_sheets": ["Sheet1", "Sheet2"]
}
```

---

## 💡 使用示例

### 示例1：通过 Agent 对话（最简单）

```
你: 帮我解析一下 upload/1773900209242_XLSX_.xlsx 文件

Agent: [执行 excel-import-parse 技能]
       已为您执行技能「excel-import-parse」：
       {'success': True, 'file_path': 'upload/demo.xlsx', ...}
```

---

### 示例2：解析所有工作表

**通过代码调用**:
```python
result = skill_executor.call_skill(
    "excel-import-parse",
    file_path="upload/demo.xlsx",
    max_rows=100  # 每个工作表最多100行
)

print(result)
```

**预期输出**:
```json
{
  "success": true,
  "file_path": "upload/demo.xlsx",
  "max_rows": 100,
  "sheets": {
    "Sheet1": {...},
    "Sheet2": {...}
  }
}
```

---

### 示例3：仅解析指定工作表

**通过代码调用**:
```python
result = skill_executor.call_skill(
    "excel-import-parse",
    file_path="upload/demo.xlsx",
    sheet_name="Sheet1",  # 只解析 Sheet1
    max_rows=50
)

print(result)
```

**预期输出**:
```json
{
  "success": true,
  "file_path": "upload/demo.xlsx",
  "max_rows": 50,
  "sheets": {
    "Sheet1": {
      "columns": [...],
      "rows": [...]
    }
  }
}
```

---

### 示例4：通过 API 调用

**HTTP POST 请求**:
```bash
curl -X POST http://localhost:5000/api/skills/excel-import-parse \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "upload/demo.xlsx",
    "sheet_name": "Sheet1",
    "max_rows": 100
  }'
```

---

### 示例5：先上传文件，再解析

**步骤1**: 上传 Excel 文件到 `upload/` 目录

**步骤2**: 解析文件
```
你: 我刚刚上传了一个 Excel 文件，帮我解析一下

Agent: [自动识别需要调用 excel-import-parse]
       请提供文件路径，例如：upload/filename.xlsx
       
你: upload/myfile.xlsx

Agent: [执行解析]
       文件解析完成！
       - 工作表数量: 2
       - Sheet1: 50 行数据
       - Sheet2: 30 行数据
```

---

## 🔧 完整工作流程

### 流程图

```
用户上传 Excel 文件
    ↓
文件保存到 upload/ 目录
    ↓
用户请求解析文件
    ↓
Agent 识别意图 → 调用 excel-import-parse 技能
    ↓
技能执行器加载脚本
    ↓
执行 excel_import_parse.py
    ↓
返回 JSON 格式数据
    ↓
展示给用户或用于后续处理
```

---

### 实际案例

**场景**: 用户上传员工信息表，需要查看内容

**步骤1**: 上传文件
```
文件: employees.xlsx
位置: upload/employees.xlsx
```

**步骤2**: 请求解析
```
你: 帮我看看 employees.xlsx 的内容
```

**步骤3**: Agent 执行
```python
result = skill_executor.call_skill(
    "excel-import-parse",
    file_path="upload/employees.xlsx",
    max_rows=100
)
```

**步骤4**: 返回结果
```json
{
  "success": true,
  "file_path": "upload/employees.xlsx",
  "max_rows": 100,
  "sheets": {
    "员工信息": {
      "columns": ["工号", "姓名", "部门", "职位", "入职日期"],
      "rows": [
        {"工号": "E001", "姓名": "张三", "部门": "技术部", "职位": "工程师", "入职日期": "2020-01-15"},
        {"工号": "E002", "姓名": "李四", "部门": "市场部", "职位": "经理", "入职日期": "2019-06-20"},
        ...
      ]
    }
  }
}
```

**步骤5**: 展示给用户
```
Agent: 文件解析完成！

工作表: 员工信息
列名: 工号, 姓名, 部门, 职位, 入职日期
数据行数: 100 行（共 250 行）

前几条数据:
- E001, 张三, 技术部, 工程师, 2020-01-15
- E002, 李四, 市场部, 经理, 2019-06-20
...
```

---

## ⚙️ 技术细节

### 核心脚本

**文件**: `skills/excel-import-parse/scripts/excel_import_parse.py`

**主要函数**:
```python
def parse_excel(
    file_path: str,
    sheet_name: Optional[str] = None,
    max_rows: Any = 200,
) -> Dict[str, Any]:
    """
    解析 Excel 文件并返回 JSON 可序列化内容。
    - 默认解析所有工作表
    - 每张表最多返回 max_rows 行
    """
```

---

### 依赖库

- **pandas** - 用于读取和处理 Excel 文件
- **openpyxl** - pandas 读取 `.xlsx` 文件的后端引擎
- **xlrd** - pandas 读取 `.xls` 文件的后端引擎（可选）

**安装依赖**:
```bash
pip install pandas openpyxl xlrd
```

---

### 数据处理

1. **空值处理**: `None` 替换 NaN
   ```python
   df = df.where(pd.notnull(df), None)
   ```

2. **行数限制**: 使用 `head()` 限制返回行数
   ```python
   df = df.head(max_rows_int)
   ```

3. **列名转换**: 确保列名为字符串
   ```python
   "columns": [str(c) for c in df.columns.tolist()]
   ```

4. **数据格式**: 转换为记录列表
   ```python
   "rows": df.to_dict(orient="records")
   ```

---

## 🛡️ 错误处理

### 常见错误及解决方案

#### 错误1: 文件不存在

**错误信息**:
```json
{"success": false, "error": "文件不存在: upload/missing.xlsx"}
```

**原因**: 文件路径不正确或文件未上传

**解决**:
1. 确认文件已上传到 `upload/` 目录
2. 检查文件路径是否正确
3. 注意路径是相对于项目根目录的

---

#### 错误2: 不支持的文件格式

**错误信息**:
```json
{"success": false, "error": "仅支持 .xlsx / .xls 文件"}
```

**原因**: 文件格式不是 Excel

**解决**:
- 确保文件扩展名是 `.xlsx` 或 `.xls`
- CSV 文件需要使用其他方法处理

---

#### 错误3: 工作表不存在

**错误信息**:
```json
{
  "success": false,
  "error": "工作表不存在: Sheet3",
  "available_sheets": ["Sheet1", "Sheet2"]
}
```

**原因**: 指定的工作表名称不存在

**解决**:
1. 使用返回的 `available_sheets` 查看可用的工作表
2. 使用正确的工作表名称
3. 或者不传 `sheet_name` 参数，解析所有工作表

---

#### 错误4: 缺少必需参数

**错误信息**:
```json
{"success": false, "error": "缺少必需参数: file_path"}
```

**原因**: 没有提供 `file_path` 参数

**解决**:
```python
# ❌ 错误
skill_executor.call_skill("excel-import-parse")

# ✅ 正确
skill_executor.call_skill(
    "excel-import-parse",
    file_path="upload/demo.xlsx"
)
```

---

#### 错误5: Excel 解析失败

**错误信息**:
```json
{"success": false, "error": "具体的错误信息..."}
```

**可能原因**:
- 文件损坏
- 加密的 Excel 文件
- 超大文件导致内存不足

**解决**:
1. 检查文件是否可以正常打开
2. 尝试减小 `max_rows` 参数
3. 检查文件是否加密

---

## 📊 性能优化

### 1. 限制返回行数

对于大文件，务必设置合理的 `max_rows`：

```python
# ❌ 不推荐：可能返回大量数据
result = skill_executor.call_skill(
    "excel-import-parse",
    file_path="upload/large_file.xlsx"
)

# ✅ 推荐：限制行数
result = skill_executor.call_skill(
    "excel-import-parse",
    file_path="upload/large_file.xlsx",
    max_rows=100  # 只返回前100行
)
```

---

### 2. 只解析需要的工作表

如果只需要某个特定工作表，明确指定：

```python
# ❌ 不推荐：解析所有工作表
result = skill_executor.call_skill(
    "excel-import-parse",
    file_path="upload/multi_sheet.xlsx"
)

# ✅ 推荐：只解析需要的工作表
result = skill_executor.call_skill(
    "excel-import-parse",
    file_path="upload/multi_sheet.xlsx",
    sheet_name="Sheet1"
)
```

---

### 3. 行数范围

`max_rows` 的有效范围是 **1-2000**：

```python
# 自动调整到有效范围
max_rows = kwargs.get("max_rows", 200)
max_rows_int = max(1, min(int(max_rows), 2000))
```

| 输入值 | 实际值 | 说明 |
|--------|--------|------|
| `0` | `1` | 最小值为1 |
| `-5` | `1` | 负数调整为1 |
| `100` | `100` | 正常值 |
| `3000` | `2000` | 超过最大值，调整为2000 |
| `"abc"` | `200` | 无效值，使用默认值 |

---

## 🔗 与其他技能的组合

### 组合1: Excel 导入 + 数据分析

```
你: 帮我分析 upload/sales.xlsx 的销售数据

Agent: [技能链执行]
1. excel-import-parse: 解析 Excel 文件
2. data-analysis: 分析销售数据
```

---

### 组合2: Excel 导入 + 数据库导入

```
你: 把 upload/customers.xlsx 导入到数据库

Agent: [技能链执行]
1. excel-import-parse: 解析 Excel 文件
2. db-import: 将数据导入数据库
```

---

### 组合3: Excel 导入 + 生成报告

```
你: 基于 upload/report_data.xlsx 生成一份报告

Agent: [技能链执行]
1. excel-import-parse: 解析 Excel 文件
2. technical-writing: 生成技术报告
```

---

## 📝 最佳实践

### 1. 文件命名规范

使用清晰的文件名：
```
✅ 推荐:
- upload/sales_2024_Q1.xlsx
- upload/employee_list.xlsx
- upload/product_catalog.xlsx

❌ 避免:
- upload/file1.xlsx
- upload/data.xlsx
- upload/新建 Microsoft Excel 工作表.xlsx
```

---

### 2. 先预览再处理

对于不熟悉的文件，先少量预览：

```python
# 第一步：预览前10行
result = skill_executor.call_skill(
    "excel-import-parse",
    file_path="upload/unknown.xlsx",
    max_rows=10
)

# 第二步：确认数据结构后，再加载更多
if result["success"]:
    full_result = skill_executor.call_skill(
        "excel-import-parse",
        file_path="upload/unknown.xlsx",
        max_rows=200
    )
```

---

### 3. 检查工作表名称

在解析之前，先查看所有工作表：

```python
# 不传 sheet_name，获取所有工作表的结构
result = skill_executor.call_skill(
    "excel-import-parse",
    file_path="upload/multi_sheet.xlsx",
    max_rows=1  # 只取1行，快速查看结构
)

# 查看可用的工作表
print(result["sheets"].keys())
# dict_keys(['Sheet1', 'Sheet2', 'Summary'])
```

---

### 4. 错误重试机制

```python
import time

def parse_with_retry(file_path, max_retries=3):
    for attempt in range(max_retries):
        result = skill_executor.call_skill(
            "excel-import-parse",
            file_path=file_path,
            max_rows=100
        )
        
        if result["success"]:
            return result
        
        print(f"第 {attempt + 1} 次尝试失败: {result['error']}")
        time.sleep(1)  # 等待1秒后重试
    
    return {"success": False, "error": "多次尝试后仍失败"}
```

---

## 🧪 测试用例

### 测试1: 基本功能

```python
# 准备测试文件
test_file = "upload/test_basic.xlsx"

# 执行解析
result = skill_executor.call_skill(
    "excel-import-parse",
    file_path=test_file
)

# 验证结果
assert result["success"] == True
assert "sheets" in result
assert len(result["sheets"]) > 0
```

---

### 测试2: 指定工作表

```python
result = skill_executor.call_skill(
    "excel-import-parse",
    file_path="upload/test.xlsx",
    sheet_name="Sheet1",
    max_rows=50
)

assert result["success"] == True
assert "Sheet1" in result["sheets"]
assert len(result["sheets"]["Sheet1"]["rows"]) <= 50
```

---

### 测试3: 错误处理

```python
# 测试文件不存在
result = skill_executor.call_skill(
    "excel-import-parse",
    file_path="upload/nonexistent.xlsx"
)

assert result["success"] == False
assert "文件不存在" in result["error"]
```

---

## 📚 相关文档

- [SKILL.md](file://d:/1.German_project/0.Kühne项目/case1_skill/skills/excel-import-parse/SKILL.md) - 技能定义
- [executor.py](file://d:/1.German_project/0.Kühne项目/case1_skill/skills/excel-import-parse/executor.py) - 执行器代码
- [excel_import_parse.py](file://d:/1.German_project/0.Kühne项目/case1_skill/skills/excel-import-parse/scripts/excel_import_parse.py) - 核心解析脚本

---

## ✨ 总结

### 核心功能

✅ **解析 Excel 文件** - 支持 `.xlsx` 和 `.xls`  
✅ **灵活配置** - 可选择工作表和行数  
✅ **JSON 输出** - 易于后续处理  
✅ **错误处理** - 清晰的错误提示  

---

### 快速开始

```python
# 最简单的用法
result = skill_executor.call_skill(
    "excel-import-parse",
    file_path="upload/your_file.xlsx"
)

if result["success"]:
    print("解析成功！")
    print(f"工作表: {list(result['sheets'].keys())}")
else:
    print(f"解析失败: {result['error']}")
```

---

### 关键要点

1. **文件位置** - 必须在 `upload/` 目录
2. **必需参数** - `file_path` 不能省略
3. **行数限制** - 默认200行，可调整1-2000
4. **工作表选择** - 不传则解析所有工作表
5. **错误处理** - 始终检查 `success` 字段

---

**更新日期**: 2026年5月  
**状态**: ✅ 已完成  
**版本**: v1.0
