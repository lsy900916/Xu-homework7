"""
pytest配置文件
提供共享的fixtures和测试配置
"""
import pytest
import sys
import json
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agent_core.skill_manager import SkillManager
from agent_core.skill_executor import SkillExecutor
from api.controller import SkillController


@pytest.fixture(scope="session")
def test_data_dir():
    """测试数据目录"""
    return Path(__file__).parent.parent / "data"


@pytest.fixture(scope="session")
def ensure_test_data(test_data_dir):
    """确保测试数据存在"""
    if not test_data_dir.exists():
        pytest.skip(f"测试数据目录不存在: {test_data_dir}")
    
    csv_files = list(test_data_dir.glob("*.csv"))
    if len(csv_files) == 0:
        pytest.skip(f"测试数据目录中没有CSV文件: {test_data_dir}")
    
    return test_data_dir


@pytest.fixture
def skill_manager():
    """创建技能管理器fixture"""
    manager = SkillManager(skills_dir="skills")
    manager.discover_skills()
    return manager


@pytest.fixture
def skill_executor(skill_manager):
    """创建技能执行器fixture"""
    return SkillExecutor(skill_manager)


@pytest.fixture
def controller(skill_manager, skill_executor):
    """创建API控制器fixture"""
    c = SkillController(skill_manager, skill_executor)
    c.app.config["TESTING"] = True
    return c


@pytest.fixture
def client(controller, tmp_path, monkeypatch):
    """创建默认带认证头的Flask测试客户端fixture"""
    auth_db = tmp_path / "auth.db"
    monkeypatch.setenv("AUTH_DB_PATH", str(auth_db))
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
    login_data = json.loads(login_resp.data)
    access_token = login_data["access_token"]
    c.environ_base["HTTP_AUTHORIZATION"] = f"Bearer {access_token}"
    return c
