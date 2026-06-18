"""
Excel 导入解析技能执行器
"""
import os
import sys
from typing import Any, Optional

from agent_core.skill_executor_base import SkillExecutorBase
from agent_core.skill_manager import Skill


class ExcelImportParseExecutor(SkillExecutorBase):
    """Excel 导入解析技能执行器"""

    @property
    def skill_name(self) -> str:
        return "excel-import-parse"

    def execute(self, skill: Skill, resources: dict, **kwargs) -> Any:
        file_path: Optional[str] = kwargs.get("file_path")
        sheet_name: Optional[str] = kwargs.get("sheet_name")
        max_rows = kwargs.get("max_rows", 200)

        if not file_path:
            return {"success": False, "error": "缺少必需参数: file_path"}

        script_path = (
            os.path.join(resources["scripts_path"], "excel_import_parse.py")
            if resources.get("scripts_path")
            else None
        )
        if not script_path or not os.path.exists(script_path):
            return {"success": False, "error": "未找到Excel解析脚本"}

        script_dir = os.path.dirname(script_path)
        if script_dir not in sys.path:
            sys.path.insert(0, script_dir)

        import excel_import_parse  # type: ignore

        if not hasattr(excel_import_parse, "parse_excel"):
            return {"success": False, "error": "脚本中未找到 parse_excel 函数"}

        try:
            return excel_import_parse.parse_excel(
                file_path=file_path,
                sheet_name=sheet_name,
                max_rows=max_rows,
            )
        except Exception as e:
            return {"success": False, "error": str(e)}

