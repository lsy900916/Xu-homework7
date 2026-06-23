"""
订单管理技能执行器
"""
import os
import sys
from typing import Any
from agent_core.skill_executor_base import SkillExecutorBase
from agent_core.skill_manager import Skill


class OrderManagementExecutor(SkillExecutorBase):
    """订单管理技能执行器"""

    @property
    def skill_name(self) -> str:
        return "order-management"

    def execute(self, skill: Skill, resources: dict, **kwargs) -> Any:
        """执行订单管理技能"""
        # 执行技能脚本
        script_path = (
            os.path.join(resources["scripts_path"], "order_management.py")
            if resources["scripts_path"]
            else None
        )
        if not script_path or not os.path.exists(script_path):
            return {"success": False, "error": "未找到订单管理脚本"}

        # 将脚本目录添加到sys.path
        script_dir = os.path.dirname(script_path)
        if script_dir not in sys.path:
            sys.path.insert(0, script_dir)

        # 使用importlib动态导入模块
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "order_management",
            script_path
        )
        if spec is None or spec.loader is None:
            return {"success": False, "error": "无法加载订单管理模块"}
            
        order_management = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(order_management)

        # 调用脚本中的处理函数
        if hasattr(order_management, "handle_order_operation"):
            # 【日志】记录LLM传入的原始参数，用于调试
            print(f"[订单管理技能] 收到LLM传入的原始参数: {kwargs}")
            print(f"[订单管理技能] action参数是否存在: {'action' in kwargs}, action值: {kwargs.get('action', '未提供')}")
            
            # 如果没有指定action，尝试根据输入参数自动推断
            if "action" not in kwargs or not kwargs["action"]:
                print(f"[订单管理技能] ⚠️  触发兜底逻辑：LLM未正确提供action参数，开始自动推断...")
                # 将所有输入转换为小写，方便匹配
                input_str = str(kwargs).lower()
                # 额外检查是否包含订单号模式（ORD开头+数字），这是get_order_detail的强特征
                import re
                has_order_number = re.search(r'ord\d+', input_str) is not None
                
                # 智能推断action - 调整判断顺序，优先判断更新状态的场景
                if any(k in input_str for k in ["更新", "修改", "状态", "new_status", "改为", "改成"]):
                    kwargs["action"] = "update_order_status"
                    # 尝试从输入中提取order_no
                    if has_order_number and "order_no" not in kwargs:
                        order_no_match = re.search(r'(ord\d+)', input_str)
                        if order_no_match:
                            kwargs["order_no"] = order_no_match.group(1).upper()
                elif any(k in input_str for k in ["创建", "新建", "生成", "create", "customer_name", "items"]):
                    kwargs["action"] = "create_order"
                elif any(k in input_str for k in ["统计", "分析", "statistics", "group_by"]):
                    kwargs["action"] = "order_statistics"
                elif (any(k in input_str for k in ["详情", "detail", "order_id", "order_no"]) or has_order_number):
                    kwargs["action"] = "get_order_detail"
                    # 尝试从输入中提取order_no（增强兜底能力）
                    if has_order_number and "order_no" not in kwargs:
                        order_no_match = re.search(r'(ord\d+)', input_str)
                        if order_no_match:
                            kwargs["order_no"] = order_no_match.group(1).upper()
                else:
                    # 默认查询订单列表
                    kwargs["action"] = "list_orders"
            
            return order_management.handle_order_operation(**kwargs)
        else:
            return {"success": False, "error": "脚本中未找到handle_order_operation函数"}