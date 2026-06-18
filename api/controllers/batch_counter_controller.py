"""
批次计数器查询控制器
提供batch_counter表的分页查询和按日期统计seq合计的API接口
"""
from flask import request, jsonify
from api.controllers.base_controller import BaseController


class BatchCounterController(BaseController):
    """批次计数器查询控制器"""

    def register_routes(self):
        """注册批次计数器查询路由"""

        @self.app.route('/api/batch-counter/page', methods=['GET'])
        def batch_counter_page_query():
            """
            分页查询batch_counter原始数据
            
            Query参数:
            - page: 页码（默认1）
            - page_size: 每页条数（默认10）
            - start_date: 起始日期（可选，格式YYYY-MM-DD）
            - end_date: 结束日期（可选，格式YYYY-MM-DD）
            数据库由环境变量 MSSQL_DATABASE 指定。
            """
            params = {
                "action": "page_query",
                "page": request.args.get("page", 1, type=int),
                "page_size": request.args.get("page_size", 10, type=int),
                "start_date": request.args.get("start_date"),
                "end_date": request.args.get("end_date"),
            }
            result = self.skill_executor.call_skill("batch-counter-query", **params)
            return jsonify(result if result else {"success": False, "error": "执行失败"})

        @self.app.route('/api/batch-counter/date-summary', methods=['GET'])
        def batch_counter_date_summary():
            """
            按日期统计seq合计（分页）
            
            Query参数:
            - page: 页码（默认1）
            - page_size: 每页条数（默认10）
            - start_date: 起始日期（可选，格式YYYY-MM-DD）
            - end_date: 结束日期（可选，格式YYYY-MM-DD）
           
            """
            params = {
                "action": "date_summary",
                "page": request.args.get("page", 1, type=int),
                "page_size": request.args.get("page_size", 10, type=int),
                "start_date": request.args.get("start_date"),
                "end_date": request.args.get("end_date"),
            }
            result = self.skill_executor.call_skill("batch-counter-query", **params)
            return jsonify(result if result else {"success": False, "error": "执行失败"})

        @self.app.route('/api/batch-counter/total-summary', methods=['GET'])
        def batch_counter_total_summary():
            """
            获取整体汇总统计
            
            Query参数:
            - start_date: 起始日期（可选，格式YYYY-MM-DD）
            - end_date: 结束日期（可选，格式YYYY-MM-DD）
            
            """
            params = {
                "action": "total_summary",
                "start_date": request.args.get("start_date"),
                "end_date": request.args.get("end_date")
              
            }
            result = self.skill_executor.call_skill("batch-counter-query", **params)
            return jsonify(result if result else {"success": False, "error": "执行失败"})

        @self.app.route('/api/batch-counter/query', methods=['POST'])
        def batch_counter_query():
            """
            通用查询接口（POST）
            
            JSON Body:
            - action: 操作类型（page_query / date_summary / total_summary）
            - page: 页码（默认1）
            - page_size: 每页条数（默认10）
            - start_date: 起始日期（可选）
            - end_date: 结束日期（可选）
            数据库由环境变量 MSSQL_DATABASE 指定。
            """
            params = request.get_json() or {}
            params.pop("database", None)  # 数据库仅由环境变量 MSSQL_DATABASE 指定
            params.setdefault("action", "page_query")
            params.setdefault("page", 1)
            params.setdefault("page_size", 10)
            print("------------------uid--------------" + str(self.get_current_uid()) + "--------------------------------")
            result = self.skill_executor.call_skill("batch-counter-query", **params)
            return jsonify(result if result else {"success": False, "error": "执行失败"})
