"""
Excel 导入解析 API 单元测试
"""
import io
import json
import os
from pathlib import Path

import pytest
import pandas as pd


@pytest.fixture
def excel_bytes() -> io.BytesIO:
    buf = io.BytesIO()
    df = pd.DataFrame([{"a": 1, "b": "x"}, {"a": 2, "b": "y"}])
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Sheet1")
    buf.seek(0)
    return buf


def test_excel_import_upload_and_parse(client, controller, tmp_path: Path, excel_bytes: io.BytesIO):
    controller.app.config["UPLOAD_DIR"] = str(tmp_path / "upload")

    resp = client.post(
        "/api/excel/import",
        data={
            "file": (excel_bytes, "demo.xlsx"),
            "max_rows": "10",
        },
        content_type="multipart/form-data",
    )
    assert resp.status_code == 200

    data = json.loads(resp.data)
    assert data["success"] is True
    assert "sheets" in data
    assert "Sheet1" in data["sheets"]
    assert data["sheets"]["Sheet1"]["columns"] == ["a", "b"]
    assert len(data["sheets"]["Sheet1"]["rows"]) == 2

    # 确认文件已保存到 upload 目录
    file_path = data.get("file_path")
    assert file_path is not None
    assert os.path.exists(file_path)
    assert Path(file_path).parent == (tmp_path / "upload")


def test_excel_import_rejects_non_excel(client):
    resp = client.post(
        "/api/excel/import",
        data={"file": (io.BytesIO(b"not excel"), "demo.txt")},
        content_type="multipart/form-data",
    )
    assert resp.status_code == 400
    data = json.loads(resp.data)
    assert data["success"] is False

