"""
批次计数器查询技能执行器
"""
import os
import sys
from typing import Any
from agent_core.skill_executor_base import SkillExecutorBase
from agent_core.skill_manager import Skill


class BatchCounterQueryExecutor(SkillExecutorBase):
    """批次计数器查询技能执行器"""

    @property
    def skill_name(self) -> str:
        return "batch-counter-query"

    def execute(self, skill: Skill, resources: dict, **kwargs) -> Any:
        """执行批次计数器查询技能"""
        # 执行技能脚本
        script_path = (
            os.path.join(resources["scripts_path"], "batch_counter_query.py")
            if resources["scripts_path"]
            else None
        )
        if not script_path or not os.path.exists(script_path):
            return {"success": False, "error": "未找到批次计数器查询脚本"}

        # 将脚本目录添加到sys.path
        script_dir = os.path.dirname(script_path)
        if script_dir not in sys.path:
            sys.path.insert(0, script_dir)

        # 直接导入脚本模块
        import batch_counter_query

        # 调用脚本中的查询函数
        if hasattr(batch_counter_query, "query_batch_counter"):
            action = kwargs.get("action", "page_query")
            page = kwargs.get("page", 1)
            page_size = kwargs.get("page_size", 10)
            start_date = kwargs.get("start_date")
            end_date = kwargs.get("end_date")

            result = batch_counter_query.query_batch_counter(
                action=action,
                page=page,
                page_size=page_size,
                start_date=start_date,
                end_date=end_date,
            )
            return result
        else:
            return {"success": False, "error": "脚本中未找到query_batch_counter函数"}
