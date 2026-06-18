---
name: excel-import-parse
description: Excel导入解析助手：接收Excel文件路径，解析工作表并输出内容（JSON）
trigger_keywords: ["Excel导入", "Excel解析", "导入Excel", "解析Excel", "excel import", "excel parse"]
---
# Excel 导入解析技能使用规范

## 使用时机
当需要将上传到 `upload/` 目录的 Excel 文件（`.xlsx`/`.xls`）解析成可直接返回给前端/接口的 JSON 数据时使用。

## 输入要求
- file_path: Excel 文件路径（必需，通常位于 `upload/` 目录）
- sheet_name: 工作表名称（可选；不传则解析所有工作表）
- max_rows: 每个工作表最多返回的行数（可选，默认：200）

## 输出说明
- success: 是否成功
- file_path: 输入文件路径
- sheets: 工作表解析结果
  - 当解析所有工作表时：`{"Sheet1": {"columns": [...], "rows": [...]}, ...}`
  - 当指定工作表时：仅返回该工作表键
- error: 失败原因（仅失败时返回）

## 使用示例

### 示例1：解析所有工作表
```json
{
  "file_path": "upload/demo.xlsx",
  "max_rows": 100
}
```

### 示例2：仅解析指定工作表
```json
{
  "file_path": "upload/demo.xlsx",
  "sheet_name": "Sheet1",
  "max_rows": 50
}
```
