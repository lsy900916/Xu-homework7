"""
Excel 导入解析控制器
提供上传 Excel 并解析输出内容的 API
"""
from __future__ import annotations

import os
import time
from typing import Any, Dict, Optional

from flask import jsonify, request
from werkzeug.utils import secure_filename

from api.controllers.base_controller import BaseController


class ExcelImportController(BaseController):
    """Excel 导入解析控制器"""

    def register_routes(self):
        @self.app.route("/api/excel/import", methods=["POST"])
        def excel_import() -> Any:
            """
            上传 Excel 文件并解析

            Multipart/Form-Data:
            - file: Excel 文件（必需）
            - sheet_name: 工作表名（可选）
            - max_rows: 最大返回行数（可选，默认200，最大2000）
            """
            upload_dir = self.app.config.get(
                "UPLOAD_DIR",
                os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "upload")),
            )
            os.makedirs(upload_dir, exist_ok=True)

            if "file" not in request.files:
                return jsonify({"success": False, "error": "缺少文件字段: file"}), 400

            f = request.files["file"]
            if not f or not f.filename:
                return jsonify({"success": False, "error": "未选择文件"}), 400

            filename = secure_filename(f.filename)
            ext = os.path.splitext(filename)[1].lower()
            if ext not in [".xlsx", ".xls"]:
                return jsonify({"success": False, "error": "仅支持 .xlsx / .xls 文件"}), 400

            ts = int(time.time() * 1000)
            saved_name = f"{ts}_{filename}"
            saved_path = os.path.join(upload_dir, saved_name)
            f.save(saved_path)

            sheet_name: Optional[str] = request.form.get("sheet_name") or None
            max_rows = request.form.get("max_rows", 200)

            result: Dict[str, Any] = self.skill_executor.call_skill(
                "excel-import-parse",
                file_path=saved_path,
                sheet_name=sheet_name,
                max_rows=max_rows,
            ) or {"success": False, "error": "技能执行失败"}

            # 附带文件保存信息，便于调用方定位
            result.setdefault("file_path", saved_path)
            result.setdefault("file_name", saved_name)
            return jsonify(result), 200

