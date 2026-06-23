"""
订单管理核心业务逻辑
实现订单的查询、创建、状态更新和统计分析
"""
import sys
import os
# 添加项目根目录到Python路径，确保能正确导入repository模块
# 无论从哪个目录运行脚本，都能找到项目根目录
script_dir = os.path.dirname(os.path.abspath(__file__))
# 从scripts目录向上三级到达项目根目录: skills/order-management/scripts/../../..
project_root = os.path.abspath(os.path.join(script_dir, "..", "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 根据环境变量选择使用SQLite还是SQL Server
USE_SQLITE = os.getenv("USE_SQLITE", "true").lower() == "true"

if USE_SQLITE:
    from repository.sqlite_order_repository import SqliteOrderRepository
    repo = SqliteOrderRepository()
else:
    # 如果需要使用SQL Server，导入对应的仓库
    from repository.mssql_repository import MssqlRepository
    repo = MssqlRepository()


def _build_filters(
    status: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    category: Optional[str] = None
) -> Tuple[str, List[Any]]:
    """构建筛选条件，返回where子句和参数列表"""
    conditions = []
    params = []
    
    if status:
        conditions.append("status = ?")
        params.append(status)
    
    if start_date:
        conditions.append("order_date >= ?")
        params.append(start_date)
    
    if end_date:
        conditions.append("order_date <= ?")
        params.append(end_date)
    
    if category:
        conditions.append("category = ?")
        params.append(category)
    
    where_clause = " AND ".join(conditions) if conditions else ""
    return where_clause, params


def _list_orders(
    page: int = 1,
    page_size: int = 10,
    status: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    category: Optional[str] = None
) -> Dict[str, Any]:
    """分页查询订单列表"""
    where_clause, params = _build_filters(status, start_date, end_date, category)
    where_sql = f"WHERE {where_clause}" if where_clause else ""
    
    # 兼容SQLite和SQL Server
    table_name = "orders" if USE_SQLITE else "[dbo].[orders]"

    # 查询总记录数
    count_sql = f"SELECT COUNT(*) FROM {table_name} {where_sql}"
    total_count = repo.execute_scalar(count_sql, tuple(params) if params else None) or 0

    # 计算分页参数
    offset = (page - 1) * page_size
    total_pages = (total_count + page_size - 1) // page_size if total_count > 0 else 0

    # 分页查询订单数据
    data_sql = f"""
        SELECT 
            id, order_no, customer_name, customer_phone, order_date,
            total_amount, status, category, created_at
        FROM {table_name}
        {where_sql}
        ORDER BY order_date DESC, id DESC
        OFFSET ? ROWS FETCH NEXT ? ROWS ONLY
    """
    query_params = params.copy()
    query_params.extend([offset, page_size])
    
    orders = repo.execute_query(data_sql, tuple(query_params))
    
    # 添加状态中文描述
    status_mapping = {
        "pending": "待支付",
        "paid": "已支付",
        "shipping": "发货中", 
        "completed": "已完成"
    }
    for order in orders:
        order["status_text"] = status_mapping.get(order["status"], order["status"])

    return {
        "success": True,
        "data": orders,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_count": total_count,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        },
        "filters": {
            "status": status,
            "start_date": start_date,
            "end_date": end_date,
            "category": category
        }
    }


def _get_order_detail(order_id: Optional[int] = None, order_no: Optional[str] = None) -> Dict[str, Any]:
    """获取订单详情"""
    if not order_id and not order_no:
        return {"success": False, "error": "必须提供order_id或order_no"}
    
    table_name = "orders" if USE_SQLITE else "[dbo].[orders]"
    
    if order_id:
        sql = f"SELECT * FROM {table_name} WHERE id = ?"
        result = repo.execute_query(sql, (order_id,))
    else:
        sql = f"SELECT * FROM {table_name} WHERE order_no = ?"
        result = repo.execute_query(sql, (order_no,))
    
    if not result:
        return {"success": False, "error": "订单不存在"}
    
    order = result[0]
    status_mapping = {
        "pending": "待支付",
        "paid": "已支付",
        "shipping": "发货中",
        "completed": "已完成"
    }
    order["status_text"] = status_mapping.get(order["status"], order["status"])
    
    return {
        "success": True,
        "order": order
    }


def _create_order(
    customer_name: str,
    customer_phone: str,
    items: List[Dict[str, Any]],
    order_date: Optional[str] = None
) -> Dict[str, Any]:
    """创建新订单"""
    # 验证必填参数
    if not customer_name or not customer_phone or not items:
        return {"success": False, "error": "客户姓名、电话和商品列表不能为空"}
    
    # 验证商品列表格式
    for item in items:
        if not all(k in item for k in ["name", "quantity", "price"]):
            return {"success": False, "error": "商品格式不正确，必须包含name, quantity, price"}
    
    # 设置默认订单日期为今天
    if not order_date:
        order_date = datetime.now().strftime("%Y-%m-%d")
    
    # 计算总金额
    total_amount = sum(item["price"] * item["quantity"] for item in items)
    
    # 从第一个商品获取类别（如果有多个商品，取第一个的类别）
    category = items[0].get("category", "未分类") if items else "未分类"
    
    # 生成订单号
    order_no = repo.generate_order_no(order_date)
    
    # 序列化商品列表为JSON
    items_json = json.dumps(items, ensure_ascii=False)
    current_time = datetime.now().isoformat()
    
    # 插入数据库
    table_name = "orders" if USE_SQLITE else "[dbo].[orders]"
    insert_sql = f"""
        INSERT INTO {table_name} (
            order_no, customer_name, customer_phone, order_date,
            total_amount, status, category, items, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, 'pending', ?, ?, ?, ?)
    """
    
    rows_affected = repo.execute_non_query(insert_sql, (
        order_no, customer_name, customer_phone, order_date,
        total_amount, category, items_json, current_time, current_time
    ))
    
    if rows_affected > 0:
        return {
            "success": True,
            "order_no": order_no,
            "total_amount": total_amount,
            "message": f"订单创建成功！订单号：{order_no}，总金额：¥{total_amount:.2f}"
        }
    else:
        return {"success": False, "error": "订单创建失败"}


def _update_order_status(order_no: str, new_status: str) -> Dict[str, Any]:
    """更新订单状态，支持状态流转验证"""
    # 先获取当前订单信息
    current_order = _get_order_detail(order_no=order_no)
    if not current_order["success"]:
        return current_order
    
    current_status = current_order["order"]["status"]
    
    # 验证状态流转是否合法
    if not repo.validate_status_transition(current_status, new_status):
        status_mapping = repo.STATUS_MAPPING
        valid_transitions = repo.VALID_STATUS_TRANSITIONS.get(current_status, [])
        valid_statuses = ", ".join([f"{s}({status_mapping.get(s, s)})" for s in valid_transitions])
        return {
            "success": False,
            "error": f"状态流转不合法，当前状态{current_status}({status_mapping.get(current_status, current_status)})只能变更为: {valid_statuses}"
        }
    
    # 更新状态
    table_name = "orders" if USE_SQLITE else "[dbo].[orders]"
    update_sql = f"""
        UPDATE {table_name} 
        SET status = ?, updated_at = ?
        WHERE order_no = ?
    """
    current_time = datetime.now().isoformat()
    rows_affected = repo.execute_non_query(update_sql, (new_status, current_time, order_no))
    
    if rows_affected > 0:
        status_mapping = repo.STATUS_MAPPING
        return {
            "success": True,
            "old_status": current_status,
            "old_status_text": status_mapping.get(current_status, current_status),
            "new_status": new_status,
            "new_status_text": status_mapping.get(new_status, new_status),
            "message": f"订单状态已更新：{status_mapping.get(current_status, current_status)} → {status_mapping.get(new_status, new_status)}"
        }
    else:
        return {"success": False, "error": "状态更新失败"}


def _order_statistics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    group_by: str = "date"
) -> Dict[str, Any]:
    """订单统计分析，支持按日期、状态、商品类别分组"""
    where_clause, params = _build_filters(start_date=start_date, end_date=end_date)
    where_sql = f"WHERE {where_clause}" if where_clause else ""
    
    table_name = "orders" if USE_SQLITE else "[dbo].[orders]"
    
    # 根据分组维度构建不同的SQL
    group_field = ""
    if group_by == "date":
        group_field = "order_date"
    elif group_by == "status":
        group_field = "status"
    elif group_by == "category":
        group_field = "category"
    else:
        return {"success": False, "error": "不支持的分组维度，仅支持date, status, category"}
    
    # 查询整体汇总
    summary_sql = f"""
        SELECT
            COUNT(*) AS total_orders,
            SUM(total_amount) AS total_amount,
            AVG(total_amount) AS avg_amount,
            MIN(order_date) AS earliest_date,
            MAX(order_date) AS latest_date,
            COUNT(DISTINCT status) AS status_types,
            COUNT(DISTINCT category) AS category_types
        FROM {table_name}
        {where_sql}
    """
    summary_result = repo.execute_query(summary_sql, tuple(params) if params else None)
    overall = summary_result[0] if summary_result else {}
    
    # 查询分组统计
    group_sql = f"""
        SELECT
            {group_field} AS group_key,
            COUNT(*) AS order_count,
            SUM(total_amount) AS group_amount,
            AVG(total_amount) AS group_avg
        FROM {table_name}
        {where_sql}
        GROUP BY {group_field}
        ORDER BY group_key DESC
    """
    group_data = repo.execute_query(group_sql, tuple(params) if params else None)
    
    # 添加状态中文描述
    if group_by == "status":
        status_mapping = repo.STATUS_MAPPING
        for item in group_data:
            item["group_key_text"] = status_mapping.get(item["group_key"], item["group_key"])
    
    return {
        "success": True,
        "overall_summary": overall,
        "group_statistics": group_data,
        "period": {
            "start_date": start_date,
            "end_date": end_date
        },
        "group_by": group_by
    }


def handle_order_operation(**kwargs) -> Dict[str, Any]:
    """处理所有订单操作的入口函数"""
    action = kwargs.get("action")
    print(f"传入的action参数: {action}")
    # 如果action为None，尝试自动推断
    if not action:
        print(f"[action推断调试] 开始推断，原始kwargs: {kwargs}")
        # 先提取所有可能的参数
        order_id = kwargs.get("order_id")
        order_no = kwargs.get("order_no")
        has_order_identifier = order_id or order_no
        print(f"[action推断调试] has_order_identifier: {has_order_identifier}")
        
        # 直接遍历所有键，检查是否包含new_status相关的任何字符串
        kwargs_str = str(kwargs).lower()
        print(f"[action推断调试] kwargs_str: {kwargs_str}")
        print(f"[action推断调试] 'new_status' in kwargs_str: {'new_status' in kwargs_str}")
        
        # 1. 优先判断更新订单状态的场景
        if ("new_status" in kwargs_str or any(k in kwargs_str for k in ["更新", "修改", "状态", "改为", "改成"])) and has_order_identifier:
            print(f"[action推断调试] 满足更新条件，设置action=update_order_status")
            action = "update_order_status"
        # 2. 判断创建订单的场景
        elif any(k in kwargs_str for k in ["创建", "新建", "生成", "create", "customer_name", "items"]):
            print(f"[action推断调试] 满足创建条件，设置action=create_order")
            action = "create_order"
        # 3. 判断统计分析的场景
        elif any(k in kwargs_str for k in ["统计", "分析", "statistics", "group_by"]):
            print(f"[action推断调试] 满足统计条件，设置action=order_statistics")
            action = "order_statistics"
        # 4. 判断获取订单详情的场景（必须有订单标识，且不是前面的场景）
        elif (any(k in kwargs_str for k in ["详情", "detail", "ord", "订单号", "查订单", "看订单"]) and has_order_identifier) or has_order_identifier:
            print(f"[action推断调试] 满足详情查询条件，设置action=get_order_detail")
            action = "get_order_detail"
        else:
            # 默认查询订单列表
            print(f"[action推断调试] 所有条件不满足，默认设置action=list_orders")
            action = "list_orders"
    
    # 【参数清洗】统一处理LLM可能生成的各种参数命名，提取标准参数
    def _clean_kwargs(input_kwargs):
        """清洗输入参数，从各种变种命名中提取标准参数值"""
        cleaned = {}
        
        # 中文状态到英文枚举值的映射（支持用户自然语言输入）
        chinese_status_map = {
            # 状态中文描述 -> 数据库标准值
            "待支付": "pending",
            "未支付": "pending",
            "待付款": "pending",
            "已支付": "paid",
            "付款成功": "paid",
            "支付成功": "paid",
            "发货中": "shipping",
            "配送中": "shipping",
            "已发货": "shipping",
            "已完成": "completed",
            "交易完成": "completed",
            "完成": "completed",
            # 支持标准值本身
            "pending": "pending",
            "paid": "paid",
            "shipping": "shipping",
            "completed": "completed"
        }
        
        # 定义通用的状态值转换函数
        def _convert_status(chinese_status: str) -> str:
            """将中文状态描述转换为标准的英文状态值"""
            if not chinese_status:
                return None
            status_str = str(chinese_status).strip()
            # 先尝试精确匹配
            for cn, en in chinese_status_map.items():
                if cn in status_str or status_str in cn:
                    return en
            # 如果没匹配到，返回原值（兼容已经是标准值的情况）
            return status_str
        
        # list_orders支持的标准参数及其可能的变种命名
        param_aliases = {
            "status": ["status", "order_status", "list_status", "filter_status", "list_orders_filter", "status_filter", "state"],
            "page": ["page", "page_num", "pagenum", "页码", "页数"],
            "page_size": ["page_size", "pagesize", "limit", "size", "每页数量"],
            "start_date": ["start_date", "startdate", "begin_date", "起始日期", "开始日期"],
            "end_date": ["end_date", "enddate", "finish_date", "截止日期", "结束日期"],
            "category": ["category", "cat", "type", "类别", "商品类别"],
            "order_id": ["order_id", "orderid", "id", "订单ID"],
            "order_no": ["order_no", "orderno", "order_number", "订单号", "单号", "order_id_or_order_no", "order_no_or_id", "id_or_order_no"],
            "customer_name": ["customer_name", "username", "name", "客户姓名", "姓名"],
            "customer_phone": ["customer_phone", "phone", "mobile", "客户电话", "手机号"],
            "items": ["items", "goods", "products", "商品列表", "产品列表", "order_items", "goods_list"],
            "new_status": ["new_status", "newstatus", "updated_status", "新状态", "更新状态"],
            "group_by": ["group_by", "groupby", "分组", "聚合维度"]
        }
        
        # 遍历所有可能的参数别名，提取值
        for std_name, aliases in param_aliases.items():
            for alias in aliases:
                if alias in input_kwargs and input_kwargs[alias] is not None:
                    value = input_kwargs[alias]
                    # 状态字段需要特殊处理：中文转英文
                    if std_name in ["status", "new_status"]:
                        original_value = value
                        value = _convert_status(value)
                        print(f"[参数清洗] 状态转换: {original_value} → {value}")
                    cleaned[std_name] = value
                    break  # 找到第一个匹配的别名就停止
        
        # 特殊处理：如果list_orders_filter是类似"status=pending"的字符串，解析它
        if "list_orders_filter" in input_kwargs and isinstance(input_kwargs["list_orders_filter"], str):
            filter_str = input_kwargs["list_orders_filter"]
            if "=" in filter_str:
                key, value = filter_str.split("=", 1)
                key = key.strip()
                value = value.strip()
                # 映射到标准参数名并转换状态
                if key in ["status", "order_status"]:
                    cleaned["status"] = _convert_status(value)
                    print(f"[参数清洗] 从filter提取状态: {value} → {cleaned['status']}")
                elif key in ["category", "cat"]:
                    cleaned["category"] = value
        
        # 额外逻辑：从原始用户输入中提取中文状态（处理兜底场景）
        raw_input = str(input_kwargs).lower()
        if "status" not in cleaned:  # 如果还没有识别到status，尝试从输入中提取
            for cn_status, en_status in chinese_status_map.items():
                if cn_status in raw_input:
                    cleaned["status"] = en_status
                    print(f"[参数清洗] 从用户输入识别状态: {cn_status} → {en_status}")
                    break
        # 针对update_order_status的特殊兜底：如果缺少new_status，尝试从输入中提取
        if "new_status" not in cleaned:
            for cn_status, en_status in chinese_status_map.items():
                if cn_status in raw_input:
                    cleaned["new_status"] = en_status
                    print(f"[参数清洗] 更新订单场景：从用户输入识别新状态: {cn_status} → {en_status}")
                    break
        # 如果已经识别到status但缺少new_status（更新场景），同步赋值
        if "new_status" not in cleaned and "status" in cleaned and "update_order_status" in str(input_kwargs):
            cleaned["new_status"] = cleaned["status"]
            print(f"[参数清洗] 更新订单场景：同步状态参数: {cleaned['status']}")
        
        return cleaned
    
    # 清洗参数
    cleaned_kwargs = _clean_kwargs(kwargs)
    
    # 【调试】打印清洗前后的参数，方便排查问题
    print(f"[参数调试] 原始参数: {kwargs}")
    print(f"[参数调试] 清洗后参数: {cleaned_kwargs}")
    
    # 【兜底】如果LLM漏传了action参数，自动推断
    if action is None:
        # 自动推断action逻辑
        if cleaned_kwargs.get("new_status"):
            action = "update_order_status"
            print(f"[参数兜底] LLM漏传action，自动推断为update_order_status")
        elif "ORD" in str(cleaned_kwargs.get("order_no", "")):
            action = "get_order_detail"
            print(f"[参数兜底] LLM漏传action，自动推断为get_order_detail")
        elif cleaned_kwargs.get("customer_name") and cleaned_kwargs.get("customer_phone"):
            action = "create_order"
            print(f"[参数兜底] LLM漏传action，自动推断为create_order")
        else:
            action = "list_orders"
            print(f"[参数兜底] LLM漏传action，默认使用list_orders")
    
    # 根据不同的action调用不同的处理函数
    if action == "list_orders":
        return _list_orders(
            page=cleaned_kwargs.get("page", 1),
            page_size=cleaned_kwargs.get("page_size", 10),
            status=cleaned_kwargs.get("status"),
            start_date=cleaned_kwargs.get("start_date"),
            end_date=cleaned_kwargs.get("end_date"),
            category=cleaned_kwargs.get("category")
        )
    
    elif action == "get_order_detail":
        return _get_order_detail(
            order_id=cleaned_kwargs.get("order_id"),
            order_no=cleaned_kwargs.get("order_no")
        )
    
    elif action == "create_order":
        return _create_order(
            customer_name=cleaned_kwargs.get("customer_name", ""),
            customer_phone=cleaned_kwargs.get("customer_phone", ""),
            items=cleaned_kwargs.get("items", []),
            order_date=cleaned_kwargs.get("order_date")
        )
    
    elif action == "update_order_status":
        return _update_order_status(
            order_no=cleaned_kwargs.get("order_no") or cleaned_kwargs.get("order_id"),
            new_status=cleaned_kwargs.get("new_status", "")
        )
    
    elif action == "order_statistics":
        return _order_statistics(
            start_date=cleaned_kwargs.get("start_date"),
            end_date=cleaned_kwargs.get("end_date"),
            group_by=cleaned_kwargs.get("group_by", "date")
        )
    
    else:
        return {
            "success": False,
            "error": f"不支持的操作类型: {action}，支持的操作：list_orders, get_order_detail, create_order, update_order_status, order_statistics"
        }


if __name__ == "__main__":
    # 测试代码
    print("=== 订单管理模块测试 ===")
    
    # 测试1：查询订单列表
    print("\n1. 测试查询订单列表（第一页，每页5条）:")
    result = _list_orders(page=1, page_size=5)
    if result["success"]:
        print(f"   共{result['pagination']['total_count']}条记录，分{result['pagination']['total_pages']}页")
        for order in result["data"][:3]:
            print(f"   {order['order_no']} - {order['customer_name']} - ¥{order['total_amount']:.2f} - {order['status_text']}")
    
    # 测试2：获取订单详情
    print("\n2. 测试获取第一个订单的详情:")
    if result["success"] and result["data"]:
        first_order_id = result["data"][0]["id"]
        detail_result = _get_order_detail(order_id=first_order_id)
        if detail_result["success"]:
            order = detail_result["order"]
            print(f"   订单号: {order['order_no']}")
            print(f"   客户: {order['customer_name']} ({order['customer_phone']})")
            print(f"   金额: ¥{order['total_amount']:.2f}")
            print(f"   状态: {order['status_text']}")
    
    # 测试3：订单统计
    print("\n3. 测试订单统计（按状态分组）:")
    stats_result = _order_statistics(group_by="status")
    if stats_result["success"]:
        print(f"   总订单数: {stats_result['overall_summary']['total_orders']}")
        print(f"   总金额: ¥{stats_result['overall_summary']['total_amount']:.2f}")
        for item in stats_result["group_statistics"]:
            print(f"   {item.get('group_key_text', item['group_key'])}: {item['order_count']}单，总金额¥{item['group_amount']:.2f}")