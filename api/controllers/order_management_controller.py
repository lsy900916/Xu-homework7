"""
订单管理控制器
提供order-management技能的所有功能API接口
支持订单的创建、查询、详情、状态更新和统计功能
"""
from flask import request, jsonify
from api.controllers.base_controller import BaseController


class OrderManagementController(BaseController):
    """订单管理控制器"""

    def register_routes(self):
        """注册订单管理路由"""

        @self.app.route('/api/orders/list', methods=['GET'])
        def order_list_query():
            """
            分页查询订单列表（GET接口）
            
            Query参数:
            - page: 页码（默认1）
            - page_size: 每页条数（默认10）
            - status: 订单状态（支持中文：待支付/已支付/发货中/已完成，自动转换为英文值）
            - start_date: 起始日期（可选，格式YYYY-MM-DD）
            - end_date: 结束日期（可选，格式YYYY-MM-DD）
            - category: 商品类别（可选）
            """
            params = {
                "action": "list_orders",
                "page": request.args.get("page", 1, type=int),
                "page_size": request.args.get("page_size", 10, type=int),
                "status": request.args.get("status"),
                "start_date": request.args.get("start_date"),
                "end_date": request.args.get("end_date"),
                "category": request.args.get("category")
            }
            result = self.skill_executor.call_skill("order-management", **params)
            return jsonify(result if result else {"success": False, "error": "订单列表查询失败"})

        @self.app.route('/api/orders/detail/<order_no>', methods=['GET'])
        def order_detail_query(order_no: str):
            """
            获取单个订单详情（GET接口）
            
            路径参数:
            - order_no: 订单号（必须，如ORD20260622001）
            """
            params = {
                "action": "get_order_detail",
                "order_no": order_no
            }
            result = self.skill_executor.call_skill("order-management", **params)
            return jsonify(result if result else {"success": False, "error": "订单详情查询失败"})

        @self.app.route('/api/orders/create', methods=['POST'])
        def order_create():
            """
            创建新订单（POST接口）
            
            JSON Body:
            - customer_name: 客户姓名（必须）
            - customer_phone: 客户手机号（必须）
            - items: 商品列表（必须，格式：[{"name": "商品名", "quantity": 数量, "price": 单价}, ...]）
            """
            params = request.get_json() or {}
            params["action"] = "create_order"
            result = self.skill_executor.call_skill("order-management", **params)
            return jsonify(result if result else {"success": False, "error": "订单创建失败"})

        @self.app.route('/api/orders/<order_no>/update-status', methods=['PUT'])
        def order_update_status(order_no: str):
            """
            更新订单状态（PUT接口）
            
            路径参数:
            - order_no: 订单号（必须）
            
            JSON Body:
            - new_status: 新状态（必须，支持中文：待支付/已支付/发货中/已完成，自动转换）
            """
            body = request.get_json() or {}
            params = {
                "action": "update_order_status",
                "order_no": order_no,
                "new_status": body.get("new_status")
            }
            result = self.skill_executor.call_skill("order-management", **params)
            return jsonify(result if result else {"success": False, "error": "订单状态更新失败"})

        @self.app.route('/api/orders/statistics', methods=['GET'])
        def order_statistics_query():
            """
            订单统计接口（GET）
            
            Query参数:
            - start_date: 起始日期（可选，格式YYYY-MM-DD）
            - end_date: 结束日期（可选，格式YYYY-MM-DD）
            - group_by: 分组方式，默认date（支持date/category/status）
            """
            params = {
                "action": "order_statistics",
                "start_date": request.args.get("start_date"),
                "end_date": request.args.get("end_date"),
                "group_by": request.args.get("group_by", "date")
            }
            result = self.skill_executor.call_skill("order-management", **params)
            return jsonify(result if result else {"success": False, "error": "订单统计失败"})

        @self.app.route('/api/orders/execute', methods=['POST'])
        def order_general_execute():
            """
            通用订单执行接口（POST，兼容原有调用方式）
            
            JSON Body:
            - action: 操作类型（必须：list_orders/get_order_detail/create_order/update_order_status/order_statistics）
            - 其他参数随action不同而变化
            """
            params = request.get_json() or {}
            print(f"[订单管理] 收到通用接口调用，参数: {params}")
            result = self.skill_executor.call_skill("order-management", **params)
            return jsonify(result if result else {"success": False, "error": "执行失败"})