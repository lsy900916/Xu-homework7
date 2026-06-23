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

class TestOrderManagementAPI:
    """订单管理技能API测试 - 覆盖5大核心功能"""
    
    def test_create_order(self, client):
        """测试1: create_order - 创建新订单"""
        response = client.post(
            '/api/skills/order-management/execute',
            json={
                "action": "create_order",
                "customer_name": "测试用户",
                "customer_phone": "13800138000",
                "items": [
                    {"name": "测试商品", "quantity": 1, "price": 99.9}
                ]
            },
            content_type='application/json'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        # 通用skill接口返回结构: {"success": True, "result": {...skill返回的实际数据...}}
        result = data.get('result', {})
        assert result.get('success') is True, f"技能执行失败: {result.get('error')}"
        assert 'order_no' in result  # 应返回订单号
        print(f"✅ create_order测试通过，创建订单号: {result.get('order_no')}")
        return result.get('order_no')  # 返回订单号供其他测试使用
    
    def test_list_orders(self, client):
        """测试2: list_orders - 查询订单列表"""
        # 测试无参数查询所有订单
        response = client.post(
            '/api/skills/order-management/execute',
            json={"action": "list_orders"},
            content_type='application/json'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        # 通用skill接口返回结构: {"success": True, "result": {...}}
        result = data.get('result', {})
        assert result.get('success') is True
        assert 'data' in result
        assert isinstance(result['data'], list)
        
        # 测试带状态筛选（中文自动转换）
        response2 = client.post(
            '/api/skills/order-management/execute',
            json={
                "action": "list_orders",
                "status": "已支付"  # 测试中文状态自动转换
            },
            content_type='application/json'
        )
        assert response2.status_code == 200
        data2 = json.loads(response2.data)
        assert data2['success'] is True
        result2 = data2.get('result', {})
        assert result2.get('success') is True
        print(f"✅ list_orders测试通过，查询到{len(result2['data'])}条已支付订单")
    
    def test_get_order_detail(self, client):
        """测试3: get_order_detail - 查看订单详情"""
        # 先创建一个订单用于测试
        create_resp = client.post(
            '/api/skills/order-management/execute',
            json={
                "action": "create_order",
                "customer_name": "详情测试用户",
                "customer_phone": "13800138001",
                "items": [{"name": "详情测试商品", "quantity": 2, "price": 199.0}]
            },
            content_type='application/json'
        )
        create_data = json.loads(create_resp.data)
        assert create_data['success'] is True
        create_result = create_data.get('result', {})
        assert create_result.get('success') is True
        test_order_no = create_result['order_no']
        
        # 测试查询该订单详情
        response = client.post(
            '/api/skills/order-management/execute',
            json={
                "action": "get_order_detail",
                "order_no": test_order_no
            },
            content_type='application/json'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        result = data.get('result', {})
        assert result.get('success') is True
        assert 'order' in result
        assert result['order']['order_no'] == test_order_no
        print(f"✅ get_order_detail测试通过，查询订单: {test_order_no}")
    
    def test_update_order_status(self, client):
        """测试4: update_order_status - 更新订单状态（含中文状态转换）"""
        # 创建一个测试订单
        create_resp = client.post(
            '/api/skills/order-management/execute',
            json={
                "action": "create_order",
                "customer_name": "更新测试用户",
                "customer_phone": "13800138002",
                "items": [{"name": "更新测试商品", "quantity": 1, "price": 99.0}]
            },
            content_type='application/json'
        )
        assert create_resp.status_code == 200
        create_data = json.loads(create_resp.data)
        assert create_data['success'] is True
        create_result = create_data.get('result', {})
        assert create_result.get('success') is True
        test_order_no = create_result['order_no']
        
        # 测试更新状态为已支付（中文自动转换为paid）
        response = client.post(
            '/api/skills/order-management/execute',
            json={
                "action": "update_order_status",
                "order_no": test_order_no,
                "new_status": "已支付"  # 测试中文状态自动转换
            },
            content_type='application/json'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        result = data.get('result', {})
        assert result.get('success') is True
        assert result['new_status'] == 'paid'  # 验证已转换为英文状态值
        assert result['old_status'] == 'pending'
        print(f"✅ update_order_status测试通过，订单{test_order_no}状态更新: pending→paid")
    
    def test_order_statistics(self, client):
        """测试5: order_statistics - 统计订单数据"""
        response = client.post(
            '/api/skills/order-management/execute',
            json={
                "action": "order_statistics",
                "group_by": "date"
            },
            content_type='application/json'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        result = data.get('result', {})
        assert result.get('success') is True
        assert 'group_statistics' in result
        assert 'overall_summary' in result
        print(f"✅ order_statistics测试通过，成功获取订单统计数据，分组统计数量: {len(result['group_statistics'])}, 总订单数: {result['overall_summary'].get('total_orders', 0)}")
    
    def test_parameter_fallback(self, client):
        """测试兜底逻辑：LLM犯错时的参数自动修复能力"""
        # 先创建一个真实订单用于测试
        create_resp = client.post(
            '/api/skills/order-management/execute',
            json={
                "action": "create_order",
                "customer_name": "兜底测试用户",
                "customer_phone": "13800138003",
                "items": [{"name": "兜底测试商品", "quantity": 1, "price": 99.0}]
            },
            content_type='application/json'
        )
        create_data = json.loads(create_resp.data)
        create_result = create_data.get('result', {})
        test_order_no = create_result.get('order_no')
        
        # 测试LLM编造参数名的兜底（用真实存在的订单号）
        response = client.post(
            '/api/skills/order-management/execute',
            json={
                # action故意漏传，测试自动推断
                "order_id_or_order_no": test_order_no,  # 编造的参数名
                "new_status": "已支付"  # 中文状态
            },
            content_type='application/json'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        result = data.get('result', {})
        assert result.get('success') is True
        assert result.get('new_status') == 'paid'
        print(f"✅ 参数兜底测试通过，系统成功修复LLM的错误参数，自动推断为update_order_status，状态成功更新为paid")

if __name__ == '__main__':
    pytest.main([__file__, '-v'])