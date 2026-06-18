"""
认证控制器
"""
from flask import request, jsonify

from agent_core.auth_token import verify_token, create_access_token, create_refresh_token
from api.controllers.base_controller import BaseController


class AuthController(BaseController):
    """登录认证控制器"""

    def register_routes(self):
        @self.app.route("/api/auth/login", methods=["POST"])
        def login():
            params = request.get_json() or {}
            username = params.get("username", "")
            password = params.get("password", "")

            result = self.skill_executor.call_skill(
                "user-login",
                username=username,
                password=password,
            )
            if not result:
                return jsonify({"success": False, "error": "登录失败"}), 400
            if result.get("success") is not True:
                return jsonify(result), 401
            return jsonify(result), 200

        @self.app.route("/api/auth/refresh", methods=["POST"])
        def refresh():
            params = request.get_json() or {}
            refresh_token = params.get("refresh_token", "")
            if not refresh_token:
                return jsonify({"success": False, "error": "缺少 refresh_token"}), 400

            payload = verify_token(refresh_token, expected_type="refresh")
            if payload is None:
                return jsonify({"success": False, "error": "refresh_token 无效或已过期"}), 401

            uid = payload.get("uid")
            username = payload.get("username")
            if uid is None or not username:
                return jsonify({"success": False, "error": "refresh_token 载荷无效"}), 401

            access_token = create_access_token(uid=uid, username=username)
            new_refresh_token = create_refresh_token(uid=uid, username=username)
            return jsonify({
                "success": True,
                "token": access_token,  # 兼容旧字段
                "access_token": access_token,
                "refresh_token": new_refresh_token,
                "token_type": "Bearer",
                "uid": uid,
                "username": username,
            }), 200

