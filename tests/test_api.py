"""
API接口单元测试
测试所有API端点的功能
"""
import pytest
import json
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class TestHealthAPI:
    """健康检查API测试"""
    
    def test_health_check(self, client):
        """测试健康检查接口"""
        response = client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'ok'
        assert 'message' in data


class TestSkillsAPI:
    """技能列表API测试"""
    
    def test_list_skills(self, client):
        """测试获取所有技能列表"""
        response = client.get('/api/skills')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'skills' in data
        assert isinstance(data['skills'], list)
        assert len(data['skills']) > 0
        
        # 验证技能结构
        skill = data['skills'][0]
        assert 'name' in skill
        assert 'description' in skill
        assert 'trigger_keywords' in skill


class TestAuthAPI:
    """认证API测试"""

    def test_login_success(self, controller, tmp_path, monkeypatch):
        monkeypatch.setenv("AUTH_DB_PATH", str(tmp_path / "auth.db"))
        monkeypatch.setenv("AUTH_DEFAULT_USERNAME", "admin")
        monkeypatch.setenv("AUTH_DEFAULT_PASSWORD", "admin123")
        monkeypatch.setenv("AUTH_TOKEN_SECRET", "test-secret")
        c = controller.app.test_client()

        response = c.post(
            "/api/auth/login",
            json={"username": "admin", "password": "admin123"},
            content_type="application/json",
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is True
        assert "access_token" in data
        assert "refresh_token" in data
        assert "uid" in data

    def test_refresh_success(self, controller, tmp_path, monkeypatch):
        monkeypatch.setenv("AUTH_DB_PATH", str(tmp_path / "auth.db"))
        monkeypatch.setenv("AUTH_DEFAULT_USERNAME", "admin")
        monkeypatch.setenv("AUTH_DEFAULT_PASSWORD", "admin123")
        monkeypatch.setenv("AUTH_TOKEN_SECRET", "test-secret")
        c = controller.app.test_client()
        login_resp = c.post(
            "/api/auth/login",
            json={"username": "admin", "password": "admin123"},
            content_type="application/json",
        )
        assert login_resp.status_code == 200
        refresh_token = json.loads(login_resp.data)["refresh_token"]

        refresh_resp = c.post(
            "/api/auth/refresh",
            json={"refresh_token": refresh_token},
            content_type="application/json",
        )
        assert refresh_resp.status_code == 200
        refresh_data = json.loads(refresh_resp.data)
        assert refresh_data["success"] is True
        assert "access_token" in refresh_data
        assert "refresh_token" in refresh_data

    def test_protected_api_without_token(self, controller):
        c = controller.app.test_client()
        response = c.get("/api/skills")
        assert response.status_code == 401


class TestSkillExecuteAPI:
    """技能执行API测试"""
    
     
    def test_execute_nonexistent_skill(self, client):
        """测试执行不存在的技能"""
        response = client.post(
            '/api/skills/nonexistent-skill/execute',
            json={},
            content_type='application/json'
        )
        assert response.status_code in [200, 400, 500]
        data = json.loads(response.data)
        # 应该返回错误
        assert data['success'] is False or 'error' in data


class TestTechnicalWritingAPI:
    """技术文档写作API测试"""
    
    def test_generate_document(self, client):
        """测试生成技术文档"""
        response = client.post(
            '/api/writing/generate',
            json={
                'title': '测试文档',
                'content': '这是测试内容',
                'save': False
            },
            content_type='application/json'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'result' in data

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
