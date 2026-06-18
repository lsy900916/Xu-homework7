"""
用户登录技能执行器
"""
import os
import sys
from typing import Any

from agent_core.skill_executor_base import SkillExecutorBase
from agent_core.skill_manager import Skill


class UserLoginExecutor(SkillExecutorBase):
    @property
    def skill_name(self) -> str:
        return "user-login"

    def execute(self, skill: Skill, resources: dict, **kwargs) -> Any:
        username = kwargs.get("username", "")
        password = kwargs.get("password", "")

        script_path = (
            os.path.join(resources["scripts_path"], "login.py")
            if resources.get("scripts_path")
            else None
        )
        if not script_path or not os.path.exists(script_path):
            return {"success": False, "error": "未找到登录脚本"}

        script_dir = os.path.dirname(script_path)
        if script_dir not in sys.path:
            sys.path.insert(0, script_dir)

        import login  # type: ignore

        if not hasattr(login, "login_with_username_password"):
            return {"success": False, "error": "脚本中未找到登录函数"}

        return login.login_with_username_password(username=username, password=password)

