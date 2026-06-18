"""
技能执行器基类
所有技能执行器都应该继承这个基类
"""
from abc import ABC, abstractmethod
from typing import Any, Optional
from agent_core.skill_manager import Skill


class SkillExecutorBase(ABC):
    """技能执行器基类"""
    
    @abstractmethod
    def execute(self, skill: Skill, resources: dict, **kwargs) -> Any:
        """
        执行技能的核心方法
        
        参数:
        - skill: 技能对象
        - resources: 技能资源字典
        - **kwargs: 其他参数
        
        返回:
        - 执行结果
        """
        pass
    
    @property
    @abstractmethod
    def skill_name(self) -> str:
        """
        返回技能名称，用于注册和匹配
        """
        pass
