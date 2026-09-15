"""visTaskManage目录、参数Schema和Spec版本接入测试。"""

from fastapi.testclient import TestClient

from server.api import app
from modules.visTaskManage.catalog import COUNTS, FUNCTIONS
from modules.visTaskManage.parameterRegistry import normalize_and_validate, parameter_contract
from modules.visTaskManage.repository import append_version, create_spec, list_versions


def test_catalog_and_parameter_contract() -> None:
    """验证5家族、19类型、23方法及画像字段动态枚举。"""

    assert COUNTS == {"families": 5, "kinds": 19, "functions": 23}
    function = next(item for item in FUNCTIONS if item["id"] == "chart.echarts-series@2.1.0")
    contract = parameter_contract(function, {"columns": ["time", "pressure"], "numeric_columns": ["time", "pressure"]}, {"x": "time", "y": ["pressure"]})
    assert contract["parameter_schema"]["properties"]["x"]["enum"] == ["time", "pressure"]
    normalized, errors = normalize_and_validate(function, {"columns": ["time", "pressure"]}, {"x": "time"}, {})
    assert errors == []
    assert normalized["x"] == "time"


def test_first_recommendation_uses_fresh_profile(tmp_path, monkeypatch) -> None:
    """验证首次HTTP推荐响应已经包含解析画像生成的字段枚举。"""

    database = tmp_path / "task-first-request.sqlite3"
    monkeypatch.setenv("QODER_ASSET_DB", str(database))
    monkeypatch.setenv("QODER_SPEC_DB", str(database))
    client = TestClient(app)
    candidates = client.get("/api/artifacts/A-1025/recommendations").json()["candidates"]
    series = next(item for item in candidates if item["kind"] == "series")
    assert "time" in series["parameter_schema"]["properties"]["x"]["enum"]


def test_visualization_spec_optimistic_lock(tmp_path, monkeypatch) -> None:
    """验证Spec创建、追加和版本历史由模块Repository接管。"""

    monkeypatch.setenv("QODER_SPEC_DB", str(tmp_path / "spec.sqlite3"))
    payload = {"artifact_id": "A-1", "function_id": "chart.echarts-series@2.1.0", "kind": "series", "params": {"x": "time"}}
    created = create_spec("S-TEST", payload, "测试")
    appended = append_version("S-TEST", created["version"], payload, "测试")
    assert appended["version"] == 2
    assert [item["version"] for item in list_versions("S-TEST")] == [2, 1]
