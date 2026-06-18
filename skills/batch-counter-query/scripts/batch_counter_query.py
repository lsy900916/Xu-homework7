"""
批次计数器查询技能脚本
连接SQL Server数据库，对batch_counter表进行分页查询和按日期统计seq合计
"""
import sys
import os

# 将项目根目录加入sys.path，以便导入repository
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 尽早加载 .env，保证创建 MssqlRepository 前环境变量已就绪
from dotenv import load_dotenv
load_dotenv(os.path.join(project_root, ".env"))

from repository.mssql_repository import MssqlRepository
from typing import Dict, Any, Optional


def query_batch_counter(
    action: str = "page_query",
    page: int = 1,
    page_size: int = 10,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    批次计数器查询主函数

    参数:
    - action: 操作类型
        - "page_query": 分页查询原始数据
        - "date_summary": 按日期统计seq合计（支持分页）
        - "total_summary": 获取整体汇总统计
    - page: 页码（从1开始）
    - page_size: 每页记录数
    - start_date: 起始日期过滤（格式：YYYY-MM-DD，可选）
    - end_date: 结束日期过滤（格式：YYYY-MM-DD，可选）
    数据库由环境变量 MSSQL_DATABASE 指定。

    返回:
    - 查询结果字典
    """
    try:
        repo = MssqlRepository()

        if action == "page_query":
            return _page_query(repo, page, page_size, start_date, end_date)

        elif action == "date_summary":
            return _date_summary(repo, page, page_size, start_date, end_date)

        elif action == "total_summary":
            return _total_summary(repo, start_date, end_date)

        else:
            return {"success": False, "error": f"不支持的操作类型: {action}"}

    except Exception as e:
        return {"success": False, "error": str(e)}


def _build_date_filter(start_date: Optional[str], end_date: Optional[str]):
    """
    构建日期过滤条件

    返回:
    - (where_clause, params) 元组
    """
    conditions = []
    params = []

    if start_date:
        conditions.append("batch_date >= ?")
        params.append(start_date)
    if end_date:
        conditions.append("batch_date <= ?")
        params.append(end_date)

    where_clause = " AND ".join(conditions) if conditions else ""
    return where_clause, tuple(params)


def _page_query(
    repo: MssqlRepository,
    page: int,
    page_size: int,
    start_date: Optional[str],
    end_date: Optional[str],
) -> Dict[str, Any]:
    """分页查询原始数据"""
    where_clause, params = _build_date_filter(start_date, end_date)
    where_sql = f"WHERE {where_clause}" if where_clause else ""

    # 查询总记录数
    count_sql = f"SELECT COUNT(*) FROM [dbo].[batch_counter] {where_sql}"
    total_count = repo.execute_scalar(count_sql, params if params else None)

    # 计算分页参数
    offset = (page - 1) * page_size
    total_pages = (total_count + page_size - 1) // page_size if total_count > 0 else 0

    # 分页查询数据（使用 OFFSET...FETCH 语法，SQL Server 2012+）
    data_sql = f"""
        SELECT id, batch_date, seq
        FROM [dbo].[batch_counter]
        {where_sql}
        ORDER BY batch_date DESC, id DESC
        OFFSET ? ROWS FETCH NEXT ? ROWS ONLY
    """
    data_params = params + (offset, page_size) if params else (offset, page_size)
    data = repo.execute_query(data_sql, data_params)

    return {
        "success": True,
        "action": "page_query",
        "data": data,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_count": total_count,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
        },
        "filters": {
            "start_date": start_date,
            "end_date": end_date,
        },
    }


def _date_summary(
    repo: MssqlRepository,
    page: int,
    page_size: int,
    start_date: Optional[str],
    end_date: Optional[str],
) -> Dict[str, Any]:
    """按日期统计seq合计（分页）"""
    where_clause, params = _build_date_filter(start_date, end_date)
    where_sql = f"WHERE {where_clause}" if where_clause else ""

    # 查询按日期分组的总数
    count_sql = f"""
        SELECT COUNT(*) FROM (
            SELECT batch_date
            FROM [dbo].[batch_counter]
            {where_sql}
            GROUP BY batch_date
        ) AS date_groups
    """
    total_count = repo.execute_scalar(count_sql, params if params else None)

    # 计算分页参数
    offset = (page - 1) * page_size
    total_pages = (total_count + page_size - 1) // page_size if total_count > 0 else 0

    # 分页查询按日期统计的seq合计
    data_sql = f"""
        SELECT
            batch_date,
            COUNT(*) AS record_count,
            SUM(seq) AS seq_total,
            MIN(seq) AS seq_min,
            MAX(seq) AS seq_max,
            AVG(CAST(seq AS FLOAT)) AS seq_avg
        FROM [dbo].[batch_counter]
        {where_sql}
        GROUP BY batch_date
        ORDER BY batch_date DESC
        OFFSET ? ROWS FETCH NEXT ? ROWS ONLY
    """
    data_params = params + (offset, page_size) if params else (offset, page_size)
    data = repo.execute_query(data_sql, data_params)

    # 格式化平均值，保留2位小数
    for row in data:
        if row.get("seq_avg") is not None:
            row["seq_avg"] = round(row["seq_avg"], 2)

    return {
        "success": True,
        "action": "date_summary",
        "data": data,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_count": total_count,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
        },
        "filters": {
            "start_date": start_date,
            "end_date": end_date,
        },
    }


def _total_summary(
    repo: MssqlRepository,
    start_date: Optional[str],
    end_date: Optional[str],
) -> Dict[str, Any]:
    """获取整体汇总统计"""
    where_clause, params = _build_date_filter(start_date, end_date)
    where_sql = f"WHERE {where_clause}" if where_clause else ""

    summary_sql = f"""
        SELECT
            COUNT(*) AS total_records,
            COUNT(DISTINCT batch_date) AS total_dates,
            SUM(seq) AS seq_grand_total,
            MIN(seq) AS seq_min,
            MAX(seq) AS seq_max,
            AVG(CAST(seq AS FLOAT)) AS seq_avg,
            MIN(batch_date) AS earliest_date,
            MAX(batch_date) AS latest_date
        FROM [dbo].[batch_counter]
        {where_sql}
    """
    data = repo.execute_query(summary_sql, params if params else None)

    if data:
        summary = data[0]
        if summary.get("seq_avg") is not None:
            summary["seq_avg"] = round(summary["seq_avg"], 2)
    else:
        summary = {}

    return {
        "success": True,
        "action": "total_summary",
        "summary": summary,
        "filters": {
            "start_date": start_date,
            "end_date": end_date,
        },
    }
