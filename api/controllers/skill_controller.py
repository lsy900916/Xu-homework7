"""
技能管理控制器
提供技能列表和执行接口
"""
from flask import request, jsonify
from api.controllers.base_controller import BaseController


class SkillController(BaseController):
    """技能管理控制器"""
    
    def register_routes(self):
        """注册技能管理路由"""
        
        @self.app.route('/api/skills', methods=['GET'])
        def list_skills():
            """列出所有可用技能"""
            skills = []
            for skill in self.skill_manager.skills.values():
                skills.append({
                    "name": skill.name,
                    "description": skill.description,
                    "trigger_keywords": skill.trigger_keywords
                })
            return jsonify({"success": True, "skills": skills})
        
        @self.app.route('/api/skills/<skill_name>/execute', methods=['POST'])
        def execute_skill(skill_name: str):
            """执行指定技能（通用接口）"""
            try:
                # 获取请求参数
                params = request.get_json() or {}
                
                # 调用技能执行器
                result = self.skill_executor.call_skill(skill_name, **params)
                
                if result is None:
                    return jsonify({
                        "success": False,
                        "error": f"技能 {skill_name} 执行失败或不存在"
                    }), 400
                
                return jsonify({
                    "success": True,
                    "skill_name": skill_name,
                    "uid": self.get_current_uid(),
                    "result": result
                })
            except Exception as e:
                return jsonify({
                    "success": False,
                    "error": str(e)
                }), 500
