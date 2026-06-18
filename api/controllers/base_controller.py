"""
基础控制器类
所有控制器都应该继承这个基类
"""
import os
from flask import Flask
from flask import jsonify, request, g
from agent_core.skill_manager import SkillManager
from agent_core.skill_executor import SkillExecutor
from agent_core.auth_token import verify_token


class BaseController:
    """基础控制器类"""
    
    def __init__(self, app: Flask, skill_manager: SkillManager, skill_executor: SkillExecutor):
        """
        初始化基础控制器
        
        参数:
        - app: Flask应用实例
        - skill_manager: 技能管理器
        - skill_executor: 技能执行器
        """
        self.app = app
        self.skill_manager = skill_manager
        self.skill_executor = skill_executor
        self._register_auth_middleware()

    def _register_auth_middleware(self):
        """
        注册统一认证中间件（仅注册一次）：
        - /api/* 默认需要 Bearer Token
        - /api/auth/login 与 /api/auth/refresh 放行
        - 校验成功后将 uid 写入 g.uid，供其他 controller 使用
        - 可通过环境变量 AUTH_REQUIRED=false 关闭认证
        """
        if self.app.config.get("_AUTH_MIDDLEWARE_REGISTERED"):
            return
        self.app.config["_AUTH_MIDDLEWARE_REGISTERED"] = True
        
        # 从环境变量读取是否需要认证（默认为 true）
        auth_required = os.getenv("AUTH_REQUIRED", "true").lower() != "false"

        @self.app.before_request
        def _check_auth_token():
            path = request.path or ""
            if not path.startswith("/api/"):
                return None
            if path in ["/api/auth/login", "/api/auth/refresh"]:
                return None
            
            # 如果关闭了认证要求，则跳过验证
            if not auth_required:
                g.uid = None
                g.username = "anonymous"
                return None

            auth = request.headers.get("Authorization", "")
            if not auth.startswith("Bearer "):
                return jsonify({"success": False, "error": "缺少或无效的 Authorization Bearer Token"}), 401

            token = auth[7:].strip()
            payload = verify_token(token, expected_type="access")
            if payload is None:
                return jsonify({"success": False, "error": "Token 无效或已过期"}), 401

            g.uid = payload.get("uid")
            g.username = payload.get("username")
            return None

    def get_current_uid(self):
        """在子控制器中获取当前登录用户ID"""
        return getattr(g, "uid", None)
    
    def register_routes(self):
        """注册路由（子类需要实现）"""
        raise NotImplementedError("子类必须实现 register_routes 方法")
