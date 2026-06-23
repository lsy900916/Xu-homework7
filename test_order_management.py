"""
订单管理技能测试脚本
验证order-management技能的所有功能是否正常工作
"""
import os
import sys
import importlib.util

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

def main():
    print("=" * 60)
    print("📦 订单管理技能功能测试")
    print("=" * 60)
    
    # 动态导入order_management模块
    script_path = os.path.join(project_root, "skills", "order-management", "scripts", "order_management.py")
    spec = importlib.util.spec_from_file_location("order_management", script_path)
    if spec is None or spec.loader is None:
        print("❌ 无法加载订单管理模块")
        return
    
    order_management = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(order_management)
    handle_order_operation = order_management.handle_order_operation
    
    # 测试1：查询订单列表
    print("\n📋 测试1：分页查询订单列表")
    print("-" * 40)
    result = handle_order_operation(
        action="list_orders",
        page=1,
        page_size=5
    )
    if result["success"]:
        print(f"✅ 成功获取订单列表")
        print(f"   总记录数: {result['pagination']['total_count']}")
        print(f"   当前页码: {result['pagination']['page']}/{result['pagination']['total_pages']}")
        print("   前3条订单:")
        for i, order in enumerate(result["data"][:3], 1):
            print(f"     {i}. {order['order_no']} - {order['customer_name']} - ¥{order['total_amount']:.2f} - {order['status_text']}")
    else:
        print(f"❌ 失败: {result.get('error')}")
    
    # 测试2：获取订单详情
    print("\n🔍 测试2：获取订单详情")
    print("-" * 40)
    if result["success"] and result["data"]:
        first_order_id = result["data"][0]["id"]
        detail_result = handle_order_operation(
            action="get_order_detail",
            order_id=first_order_id
        )
        if detail_result["success"]:
            order = detail_result["order"]
            print(f"✅ 成功获取订单详情")
            print(f"   订单号: {order['order_no']}")
            print(f"   客户: {order['customer_name']} ({order['customer_phone']})")
            print(f"   订单日期: {order['order_date']}")
            print(f"   总金额: ¥{order['total_amount']:.2f}")
            print(f"   当前状态: {order['status_text']}")
            if order.get('items'):
                print("   商品明细:")
                for item in order['items']:
                    print(f"     - {item['name']} x{item['quantity']} = ¥{item['price'] * item['quantity']:.2f}")
        else:
            print(f"❌ 获取订单详情失败: {detail_result.get('error')}")
    
    # 测试3：创建新订单
    print("\n➕ 测试3：创建新订单")
    print("-" * 40)
    create_result = handle_order_operation(
        action="create_order",
        customer_name="测试客户",
        customer_phone="13900139000",
        items=[
            {"name": "测试商品1", "quantity": 2, "price": 99.0, "category": "测试分类"},
            {"name": "测试商品2", "quantity": 1, "price": 199.0, "category": "测试分类"}
        ]
    )
    if create_result["success"]:
        print(f"✅ 订单创建成功")
        print(f"   订单号: {create_result['order_no']}")
        print(f"   总金额: ¥{create_result['total_amount']:.2f}")
        print(f"   消息: {create_result['message']}")
        # 保存这个订单号用于后续测试
        new_order_id = None
        # 查询刚创建的订单获取ID
        check_result = handle_order_operation(
            action="get_order_detail",
            order_no=create_result['order_no']
        )
        if check_result["success"]:
            new_order_id = check_result["order"]["id"]
    else:
        print(f"❌ 创建订单失败: {create_result.get('error')}")
    
    # 测试4：更新订单状态
    print("\n🔄 测试4：更新订单状态")
    print("-" * 40)
    if 'new_order_id' in locals() and new_order_id:
        update_result = handle_order_operation(
            action="update_order_status",
            order_id=new_order_id,
            new_status="paid"
        )
        if update_result["success"]:
            print(f"✅ 订单状态更新成功")
            print(f"   {update_result['old_status_text']} → {update_result['new_status_text']}")
            print(f"   消息: {update_result['message']}")
        else:
            print(f"❌ 更新状态失败: {update_result.get('error')}")
    else:
        print("⚠️ 跳过状态更新测试（未获取到新订单ID）")
    
    # 测试5：订单统计分析
    print("\n📊 测试5：订单统计分析")
    print("-" * 40)
    # 按状态分组统计
    stats_result = handle_order_operation(
        action="order_statistics",
        group_by="status",
        start_date="2024-01-01",
        end_date="2024-12-31"
    )
    if stats_result["success"]:
        print(f"✅ 统计完成")
        print(f"   总订单数: {stats_result['overall_summary']['total_orders']}")
        print(f"   总金额: ¥{stats_result['overall_summary']['total_amount']:.2f}")
        print(f"   平均订单金额: ¥{stats_result['overall_summary']['avg_amount']:.2f}")
        print("   按状态分组:")
        for item in stats_result["group_statistics"]:
            print(f"     {item.get('group_key_text', item['group_key'])}: {item['order_count']}单，总金额¥{item['group_amount']:.2f}")
    else:
        print(f"❌ 统计失败: {stats_result.get('error')}")
    
    # 测试6：条件筛选查询
    print("\n🎯 测试6：条件筛选查询（已支付订单）")
    print("-" * 40)
    filter_result = handle_order_operation(
        action="list_orders",
        status="paid",
        page=1,
       page_size=10
    )
    if filter_result["success"]:
        print(f"✅ 筛选查询成功")
        print(f"   已支付订单数量: {filter_result['pagination']['total_count']}")
        for i, order in enumerate(filter_result["data"][:3], 1):
            print(f"     {i}. {order['order_no']} - {order['customer_name']} - ¥{order['total_amount']:.2f}")
    else:
        print(f"❌ 筛选查询失败: {filter_result.get('error')}")
    
    print("\n" + "=" * 60)
    print("🎉 所有测试完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()