"""
批次计数器查询API测试
测试batch_counter相关的所有API端点
包含：
- 使用mock的单元测试（不依赖真实数据库）
- 连接真实数据库的集成测试（标记为integration）
"""
import pytest
import json
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# ===================== Mock数据 =====================

MOCK_PAGE_DATA = [
    {"id": 1, "batch_date": "2024-01-01", "seq": 5},
    {"id": 2, "batch_date": "2024-01-02", "seq": 3},
    {"id": 3, "batch_date": "2024-01-03", "seq": 8},
]

MOCK_DATE_SUMMARY_DATA = [
    {"batch_date": "2024-01-03", "record_count": 1, "seq_total": 8, "seq_min": 8, "seq_max": 8, "seq_avg": 8.0},
    {"batch_date": "2024-01-02", "record_count": 1, "seq_total": 3, "seq_min": 3, "seq_max": 3, "seq_avg": 3.0},
    {"batch_date": "2024-01-01", "record_count": 1, "seq_total": 5, "seq_min": 5, "seq_max": 5, "seq_avg": 5.0},
]

MOCK_TOTAL_SUMMARY = {
    "total_records": 3,
    "total_dates": 3,
    "seq_grand_total": 16,
    "seq_min": 3,
    "seq_max": 8,
    "seq_avg": 5.33,
    "earliest_date": "2024-01-01",
    "latest_date": "2024-01-03",
}


def _mock_page_query_result(page=1, page_size=10, start_date=None, end_date=None):
    """生成mock的分页查询结果"""
    return {
        "success": True,
        "action": "page_query",
        "data": MOCK_PAGE_DATA,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_count": 3,
            "total_pages": 1,
            "has_next": False,
            "has_prev": False,
        },
        "filters": {"start_date": start_date, "end_date": end_date},
    }


def _mock_date_summary_result(page=1, page_size=10, start_date=None, end_date=None):
    """生成mock的按日期统计结果"""
    return {
        "success": True,
        "action": "date_summary",
        "data": MOCK_DATE_SUMMARY_DATA,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_count": 3,
            "total_pages": 1,
            "has_next": False,
            "has_prev": False,
        },
        "filters": {"start_date": start_date, "end_date": end_date},
    }


def _mock_total_summary_result(start_date=None, end_date=None):
    """生成mock的整体汇总结果"""
    return {
        "success": True,
        "action": "total_summary",
        "summary": MOCK_TOTAL_SUMMARY,
        "filters": {"start_date": start_date, "end_date": end_date},
    }


# ===================== 单元测试（Mock数据库）=====================

class TestBatchCounterPageAPI:
    """分页查询API测试（Mock）"""

    @patch("agent_core.skill_executor.SkillExecutor.call_skill")
    def test_page_query_default(self, mock_call_skill, client):
        """测试默认分页查询"""
        mock_call_skill.return_value = _mock_page_query_result()

        response = client.get('/api/batch-counter/page')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['action'] == 'page_query'
        assert 'data' in data
        assert 'pagination' in data
        assert isinstance(data['data'], list)

    @patch("agent_core.skill_executor.SkillExecutor.call_skill")
    def test_page_query_with_pagination(self, mock_call_skill, client):
        """测试指定页码和每页条数"""
        mock_call_skill.return_value = _mock_page_query_result(page=2, page_size=5)

        response = client.get('/api/batch-counter/page?page=2&page_size=5')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        # 验证mock被正确的参数调用
        mock_call_skill.assert_called_once()
        call_kwargs = mock_call_skill.call_args
        assert call_kwargs[1]['page'] == 2 or call_kwargs.kwargs.get('page') == 2

    @patch("agent_core.skill_executor.SkillExecutor.call_skill")
    def test_page_query_with_date_filter(self, mock_call_skill, client):
        """测试带日期过滤的分页查询"""
        mock_call_skill.return_value = _mock_page_query_result(
            start_date="2024-01-01", end_date="2024-01-31"
        )

        response = client.get(
            '/api/batch-counter/page?start_date=2024-01-01&end_date=2024-01-31'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True

    @patch("agent_core.skill_executor.SkillExecutor.call_skill")
    def test_page_query_pagination_info(self, mock_call_skill, client):
        """测试分页信息结构完整性"""
        mock_call_skill.return_value = _mock_page_query_result()

        response = client.get('/api/batch-counter/page')
        data = json.loads(response.data)
        pagination = data['pagination']
        assert 'page' in pagination
        assert 'page_size' in pagination
        assert 'total_count' in pagination
        assert 'total_pages' in pagination
        assert 'has_next' in pagination
        assert 'has_prev' in pagination


class TestBatchCounterDateSummaryAPI:
    """按日期统计API测试（Mock）"""

    @patch("agent_core.skill_executor.SkillExecutor.call_skill")
    def test_date_summary_default(self, mock_call_skill, client):
        """测试默认日期统计"""
        mock_call_skill.return_value = _mock_date_summary_result()

        response = client.get('/api/batch-counter/date-summary')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['action'] == 'date_summary'
        assert 'data' in data
        assert isinstance(data['data'], list)

    @patch("agent_core.skill_executor.SkillExecutor.call_skill")
    def test_date_summary_data_structure(self, mock_call_skill, client):
        """测试日期统计返回的数据结构"""
        mock_call_skill.return_value = _mock_date_summary_result()

        response = client.get('/api/batch-counter/date-summary')
        data = json.loads(response.data)
        if data['data']:
            row = data['data'][0]
            assert 'batch_date' in row
            assert 'record_count' in row
            assert 'seq_total' in row
            assert 'seq_min' in row
            assert 'seq_max' in row
            assert 'seq_avg' in row

    @patch("agent_core.skill_executor.SkillExecutor.call_skill")
    def test_date_summary_with_date_filter(self, mock_call_skill, client):
        """测试带日期过滤的统计"""
        mock_call_skill.return_value = _mock_date_summary_result(
            start_date="2024-01-01", end_date="2024-06-30"
        )

        response = client.get(
            '/api/batch-counter/date-summary?start_date=2024-01-01&end_date=2024-06-30'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True


class TestBatchCounterTotalSummaryAPI:
    """整体汇总统计API测试（Mock）"""

    @patch("agent_core.skill_executor.SkillExecutor.call_skill")
    def test_total_summary_default(self, mock_call_skill, client):
        """测试默认整体汇总"""
        mock_call_skill.return_value = _mock_total_summary_result()

        response = client.get('/api/batch-counter/total-summary')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['action'] == 'total_summary'
        assert 'summary' in data

    @patch("agent_core.skill_executor.SkillExecutor.call_skill")
    def test_total_summary_structure(self, mock_call_skill, client):
        """测试整体汇总的数据结构"""
        mock_call_skill.return_value = _mock_total_summary_result()

        response = client.get('/api/batch-counter/total-summary')
        data = json.loads(response.data)
        summary = data['summary']
        assert 'total_records' in summary
        assert 'total_dates' in summary
        assert 'seq_grand_total' in summary
        assert 'seq_min' in summary
        assert 'seq_max' in summary
        assert 'seq_avg' in summary
        assert 'earliest_date' in summary
        assert 'latest_date' in summary

    @patch("agent_core.skill_executor.SkillExecutor.call_skill")
    def test_total_summary_with_date_filter(self, mock_call_skill, client):
        """测试带日期过滤的整体汇总"""
        mock_call_skill.return_value = _mock_total_summary_result(
            start_date="2024-01-01", end_date="2024-12-31"
        )

        response = client.get(
            '/api/batch-counter/total-summary?start_date=2024-01-01&end_date=2024-12-31'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True


class TestBatchCounterPostAPI:
    """通用POST查询接口测试（Mock）"""

    @patch("agent_core.skill_executor.SkillExecutor.call_skill")
    def test_post_page_query(self, mock_call_skill, client):
        """测试POST方式分页查询"""
        mock_call_skill.return_value = _mock_page_query_result()

        response = client.post(
            '/api/batch-counter/query',
            json={"action": "page_query", "page": 1, "page_size": 10},
            content_type='application/json'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True

    @patch("agent_core.skill_executor.SkillExecutor.call_skill")
    def test_post_date_summary(self, mock_call_skill, client):
        """测试POST方式日期统计"""
        mock_call_skill.return_value = _mock_date_summary_result()

        response = client.post(
            '/api/batch-counter/query',
            json={
                "action": "date_summary",
                "start_date": "2024-01-01",
                "end_date": "2024-12-31"
            },
            content_type='application/json'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True

    @patch("agent_core.skill_executor.SkillExecutor.call_skill")
    def test_post_total_summary(self, mock_call_skill, client):
        """测试POST方式整体汇总"""
        mock_call_skill.return_value = _mock_total_summary_result()

        response = client.post(
            '/api/batch-counter/query',
            json={"action": "total_summary"},
            content_type='application/json'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True

    @patch("agent_core.skill_executor.SkillExecutor.call_skill")
    def test_post_default_action(self, mock_call_skill, client):
        """测试POST不指定action时默认为page_query"""
        mock_call_skill.return_value = _mock_page_query_result()

        response = client.post(
            '/api/batch-counter/query',
            json={},
            content_type='application/json'
        )
        assert response.status_code == 200
        # 验证默认action是page_query
        mock_call_skill.assert_called_once()
        call_kwargs = mock_call_skill.call_args
        assert call_kwargs[1].get('action') == 'page_query' or call_kwargs.kwargs.get('action') == 'page_query'


# ===================== 集成测试（真实数据库连接）=====================

@pytest.mark.integration
class TestBatchCounterIntegration:
    """批次计数器集成测试（连接真实数据库）"""

    def test_real_page_query(self, client):
        """集成测试：分页查询真实数据"""
        response = client.get('/api/batch-counter/page?page=1&page_size=5')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['action'] == 'page_query'
        assert 'data' in data
        assert 'pagination' in data
        print(f"\n[集成测试] 分页查询结果: 共{data['pagination']['total_count']}条记录")
        print(f"  当前第{data['pagination']['page']}页，共{data['pagination']['total_pages']}页")
        if data['data']:
            print(f"  第一条: {data['data'][0]}")

    def test_real_date_summary(self, client):
        """集成测试：按日期统计seq合计"""
        response = client.get('/api/batch-counter/date-summary?page=1&page_size=5')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['action'] == 'date_summary'
        print(f"\n[集成测试] 日期统计结果: 共{data['pagination']['total_count']}个日期")
        for row in data['data']:
            print(f"  {row['batch_date']}: seq合计={row['seq_total']}, "
                  f"记录数={row['record_count']}, 平均={row.get('seq_avg', 'N/A')}")

    def test_real_total_summary(self, client):
        """集成测试：整体汇总"""
        response = client.get('/api/batch-counter/total-summary')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['action'] == 'total_summary'
        summary = data['summary']
        print(f"\n[集成测试] 整体汇总:")
        print(f"  总记录数: {summary.get('total_records')}")
        print(f"  总日期数: {summary.get('total_dates')}")
        print(f"  seq总计: {summary.get('seq_grand_total')}")
        print(f"  日期范围: {summary.get('earliest_date')} ~ {summary.get('latest_date')}")

    def test_real_page_query_with_date_filter(self, client):
        """集成测试：带日期过滤的分页查询"""
        response = client.get(
            '/api/batch-counter/page?page=1&page_size=5&start_date=2024-01-01&end_date=2025-12-31'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        print(f"\n[集成测试] 日期过滤查询: 2024-01-01 ~ 2025-12-31")
        print(f"  共{data['pagination']['total_count']}条记录")

    def test_real_post_query(self, client):
        """集成测试：POST通用查询"""
        response = client.post(
            '/api/batch-counter/query',
            json={
                "action": "date_summary",
                "page": 1,
                "page_size": 5
            },
            content_type='application/json'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        print(f"\n[集成测试] POST通用查询(date_summary): 成功")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
