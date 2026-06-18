"""
测试本地SQLite数据库是否正常工作
"""
import os
import sys
from dotenv import load_dotenv

# 加载环境变量
project_root = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(project_root, ".env"))

# 导入我们的查询模块（处理带连字符的模块名）
sys.path.insert(0, os.path.join(project_root, "skills", "batch-counter-query", "scripts"))
import importlib.util
spec = importlib.util.spec_from_file_location(
    "batch_counter_query",
    os.path.join(project_root, "skills", "batch-counter-query", "scripts", "batch_counter_query.py")
)
batch_counter_query = importlib.util.module_from_spec(spec)
spec.loader.exec_module(batch_counter_query)
query_batch_counter = batch_counter_query.query_batch_counter

def test_local_database():
    print("=== 测试本地SQLite批次计数器数据库 ===")
    
    # 测试1: 分页查询
    print("\n1. 测试分页查询(page_query):")
    result1 = query_batch_counter(action="page_query", page=1, page_size=10)
    if result1["success"]:
        print(f"   ✅ 成功，获取到{len(result1['data'])}条记录")
        print(f"   📊 总记录数: {result1['pagination']['total_count']}")
        print(f"   📄 当前页: {result1['pagination']['page']}/{result1['pagination']['total_pages']}")
        for i, row in enumerate(result1['data'][:3]):  # 只显示前3条
            print(f"      {i+1}. 日期: {row['batch_date']}, seq: {row['seq']}")
    else:
        print(f"   ❌ 失败: {result1['error']}")
    
    # 测试2: 按日期统计
    print("\n2. 测试按日期统计(date_summary):")
    result2 = query_batch_counter(action="date_summary", page=1, page_size=10)
    if result2["success"]:
        print(f"   ✅ 成功，获取到{len(result2['data'])}个日期的统计数据")
        for i, row in enumerate(result2['data'][:3]):
            print(f"      {i+1}. 日期: {row['batch_date']}, 记录数: {row['record_count']}, seq总和: {row['seq_total']}")
    else:
        print(f"   ❌ 失败: {result2['error']}")
    
    # 测试3: 整体汇总
    print("\n3. 测试整体汇总(total_summary):")
    result3 = query_batch_counter(action="total_summary")
    if result3["success"]:
        summary = result3['summary']
        print(f"   ✅ 成功获取整体汇总数据")
        print(f"      总记录数: {summary['total_records']}")
        print(f"      总日期数: {summary['total_dates']}")
        print(f"      seq总和: {summary['seq_grand_total']}")
        print(f"      seq最小值: {summary['seq_min']}")
        print(f"      seq最大值: {summary['seq_max']}")
        print(f"      seq平均值: {summary['seq_avg']}")
        print(f"      最早日期: {summary['earliest_date']}")
        print(f"      最晚日期: {summary['latest_date']}")
    else:
        print(f"   ❌ 失败: {result3['error']}")
    
    # 测试4: 日期过滤
    print("\n4. 测试日期过滤:")
    result4 = query_batch_counter(
        action="total_summary",
        start_date="2026-05-01",
        end_date="2026-05-31"
    )
    if result4["success"]:
        summary = result4['summary']
        print(f"   ✅ 2026年5月数据统计:")
        print(f"      记录数: {summary['total_records']}")
        print(f"      seq总和: {summary['seq_grand_total']}")
    else:
        print(f"   ❌ 失败: {result4['error']}")

if __name__ == "__main__":
    test_local_database()