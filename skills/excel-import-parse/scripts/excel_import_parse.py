"""
Excel 解析脚本：读取 Excel 并输出 JSON 可序列化结构
"""
from __future__ import annotations

import os
from typing import Any, Dict, Optional

import pandas as pd


def _normalize_max_rows(max_rows: Any) -> int:
    try:
        value = int(max_rows)
    except Exception:
        value = 200
    return max(1, min(value, 2000))


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
    if not os.path.exists(file_path):
        return {"success": False, "error": f"文件不存在: {file_path}"}

    ext = os.path.splitext(file_path)[1].lower()
    if ext not in [".xlsx", ".xls"]:
        return {"success": False, "error": "仅支持 .xlsx / .xls 文件"}

    max_rows_int = _normalize_max_rows(max_rows)

    try:
        xls = pd.ExcelFile(file_path)
        available_sheets = list(xls.sheet_names)
        if sheet_name:
            if sheet_name not in available_sheets:
                return {
                    "success": False,
                    "error": f"工作表不存在: {sheet_name}",
                    "available_sheets": available_sheets,
                }
            target_sheets = [sheet_name]
        else:
            target_sheets = available_sheets

        sheets: Dict[str, Any] = {}
        for s in target_sheets:
            df = pd.read_excel(xls, sheet_name=s)
            df = df.head(max_rows_int)
            df = df.where(pd.notnull(df), None)
            sheets[s] = {
                "columns": [str(c) for c in df.columns.tolist()],
                "rows": df.to_dict(orient="records"),
            }

        return {
            "success": True,
            "file_path": file_path,
            "max_rows": max_rows_int,
            "sheets": sheets,
        }
    except Exception as e:
        return {"success": False, "error": str(e), "file_path": file_path}

