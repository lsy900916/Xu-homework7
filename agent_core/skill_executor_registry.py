"""
技能执行器注册表
自动发现和注册所有技能执行器
"""
import os
import sys
import importlib.util
from pathlib import Path
from typing import Dict, Optional
from agent_core.skill_executor_base import SkillExecutorBase


class SkillExecutorRegistry:
    """技能执行器注册表"""
    
    def __init__(self, skills_dir: str = "skills"):
        """
        初始化注册表
        
        参数:
        - skills_dir: 技能目录路径
        """
        self.skills_dir = Path(skills_dir)
        self.executors: Dict[str, SkillExecutorBase] = {}
        self._discover_executors()
    
    def _discover_executors(self):
        """自动发现所有技能执行器"""
        if not self.skills_dir.exists():
            print(f"警告：技能目录不存在：{self.skills_dir}")
            return
        
        # 遍历所有技能目录
        for skill_dir in self.skills_dir.iterdir():
            if not skill_dir.is_dir():
                continue
            
            executor_path = skill_dir / "executor.py"
            if executor_path.exists():
                try:
                    executor = self._load_executor(executor_path)
                    if executor:
                        self.executors[executor.skill_name] = executor
                        print(f"已注册技能执行器：{executor.skill_name}")
                except Exception as e:
                    print(f"加载技能执行器失败 {skill_dir.name}: {e}")
    
    def _load_executor(self, executor_path: Path) -> Optional[SkillExecutorBase]:
        """
        加载技能执行器
        
        参数:
        - executor_path: 执行器文件路径
        
        返回:
        - 技能执行器实例
        """
        # 构建模块名
        module_name = f"skill_executor_{executor_path.parent.name}"
        
        # 动态加载模块
        spec = importlib.util.spec_from_file_location(module_name, executor_path)
        if spec is None or spec.loader is None:
            return None
        
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        
        # 查找执行器类（查找继承自SkillExecutorBase的类）
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (isinstance(attr, type) and 
                issubclass(attr, SkillExecutorBase) and 
                attr != SkillExecutorBase):
                executor_instance = attr()
                return executor_instance
        
        return None
    
    def get_executor(self, skill_name: str) -> Optional[SkillExecutorBase]:
        """
        获取技能执行器
        
        参数:
        - skill_name: 技能名称
        
        返回:
        - 技能执行器实例，如果不存在返回None
        """
        return self.executors.get(skill_name)
    
    def register_executor(self, executor: SkillExecutorBase):
        """
        手动注册技能执行器
        
        参数:
        - executor: 技能执行器实例
        """
        self.executors[executor.skill_name] = executor
    
    def list_executors(self) -> list:
        """列出所有已注册的执行器名称"""
        return list(self.executors.keys())
