"""
健康检查控制器
"""
from flask import jsonify
from api.controllers.base_controller import BaseController


class HealthController(BaseController):
    """健康检查控制器"""
    
    def register_routes(self):
        """注册健康检查路由"""
        
        @self.app.route('/health', methods=['GET'])
        def health():
            """健康检查接口"""
            return jsonify({
                "status": "ok",
                "message": "Skill API is running"
            })
