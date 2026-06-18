import os
import sys
from typing import List, Optional
from agent_core.skill_manager import SkillManager, Skill
from agent_core.skill_executor_registry import SkillExecutorRegistry
from agent_core.skill_executor_base import SkillExecutorBase

class SkillExecutor:
    def __init__(self, skill_manager: SkillManager, skills_dir: str = "skills"):
        """
        初始化技能执行器
        
        参数:
        - skill_manager: 技能管理器
        - skills_dir: 技能目录路径，用于自动发现执行器
        """
        self.skill_manager = skill_manager  # 关联技能管理器
        # 初始化执行器注册表，自动发现所有技能执行器
        self.registry = SkillExecutorRegistry(skills_dir=skills_dir)

    # 显式调用技能：指定技能名执行
    def call_skill(self, skill_name: str, **kwargs) -> Optional[any]:
        """
        调用技能执行
        
        参数:
        - skill_name: 技能名称
        - **kwargs: 技能参数
        
        返回:
        - 执行结果
        """
        # 先激活技能，再获取资源
        skill = self.skill_manager.activate_skill(skill_name)
        resources = self.skill_manager.get_skill_resources(skill_name)
        if not skill or not resources:
            return None
        
        # 从注册表获取执行器
        executor = self.registry.get_executor(skill_name)
        if not executor:
            print(f"警告：未找到技能 {skill_name} 的执行器，尝试使用默认执行逻辑")
            return None
        
        # 执行技能
        print(f"=== 开始执行技能：{skill_name} ===")
        try:
            result = executor.execute(skill, resources, **kwargs)
            print(f"技能{skill_name}执行完成，结果：{result}\n")
            return result
        except Exception as e:
            print(f"技能{skill_name}执行失败：{e}\n")
            return None

    # 自动触发技能：根据用户查询匹配技能并执行
    def auto_trigger_skill(self, query: str, **kwargs) -> Optional[any]:
        print(f"=== 开始自动匹配技能：查询={query} ===")
        skill = self.skill_manager.match_skill_by_keyword(query)
        if not skill:
            print("未匹配到任何技能\n")
            return None
        print(f"匹配到技能：{skill.name}\n")
        return self.call_skill(skill.name, **kwargs)

    # 技能组合执行：按指定顺序执行多个技能，数据流转（基础版）
    def call_skill_chain(self, skill_chain: List[str], **kwargs) -> List[any]:
        print(f"=== 开始执行技能链：{skill_chain} ===")
        results = []
        current_kwargs = kwargs
        # 按顺序执行，上一个技能的结果作为下一个技能的入参
        for skill_name in skill_chain:
            result = self.call_skill(skill_name, **current_kwargs)
            results.append(result)
            current_kwargs["prev_skill_result"] = result  # 数据流转
        print(f"技能链执行完成，所有结果：{results}\n")
        return results

