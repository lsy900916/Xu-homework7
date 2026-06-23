"""
API Controller层（主控制器）
按照Controller -> Skill -> Repository架构设计
Controller层只负责：参数接收、调用Skill、返回结果

将接口按功能模块分解到不同的控制器文件中
"""
import sys
from pathlib import Path
# 添加项目根目录到Python路径，解决模块导入问题
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from flask import Flask
from agent_core.skill_manager import SkillManager
from agent_core.skill_executor import SkillExecutor
from api.controllers import (
    HealthController,
    SkillController as SkillManagementController,   
    AuthController,
    WritingController,   
    BatchCounterController,
    ExcelImportController,
    OrderManagementController,
)


class SkillController:
    """技能控制器主类，整合所有子控制器"""
    
    def __init__(self, skill_manager: SkillManager, skill_executor: SkillExecutor):
        """
        初始化控制器
        
        参数:
        - skill_manager: 技能管理器
        - skill_executor: 技能执行器
        """
        self.skill_manager = skill_manager
        self.skill_executor = skill_executor
        self.app = Flask(__name__)
        self._register_all_routes()
    
    def _register_all_routes(self):
        """注册所有API路由"""
        # 初始化所有子控制器并注册路由
        controllers = [
            HealthController(self.app, self.skill_manager, self.skill_executor),
            AuthController(self.app, self.skill_manager, self.skill_executor),
            SkillManagementController(self.app, self.skill_manager, self.skill_executor),
            
            WritingController(self.app, self.skill_manager, self.skill_executor),
            
            BatchCounterController(self.app, self.skill_manager, self.skill_executor),
            ExcelImportController(self.app, self.skill_manager, self.skill_executor),
            OrderManagementController(self.app, self.skill_manager, self.skill_executor),
        ]
        
        # 注册所有控制器的路由
        for controller in controllers:
            controller.register_routes()
    
    def run(self, host='0.0.0.0', port=5000, debug=False):
        """启动API服务器"""
        print(f"启动Skill API服务器: http://{host}:{port}")
        print(f"API文档: http://{host}:{port}/api/skills")
        self.app.run(host=host, port=port, debug=debug)