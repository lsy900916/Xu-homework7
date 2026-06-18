"""
技术文档写作控制器
"""
from flask import request, jsonify
from api.controllers.base_controller import BaseController


class WritingController(BaseController):
    """技术文档写作控制器"""
    
    def register_routes(self):
        """注册技术文档写作路由"""
        
        @self.app.route('/api/writing/generate', methods=['POST'])
        def generate_document():
            """生成技术文档"""
            params = request.get_json() or {}
            result = self.skill_executor.call_skill("technical-writing", **params)
            return jsonify({
                "success": True,
                "result": result
            } if result else {"success": False, "error": "生成文档失败"})
