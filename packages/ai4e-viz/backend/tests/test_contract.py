import hashlib
import json
import os
import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from server.api import app
from modules.dataAssets import application as data_assets_application
from modules.visDatasets.pipeline import DATA_DIR
from modules.reportManage.gradShafranovReport import ROOT as GS_ROOT
from modules.reportManage import api as report_api
from modules.visGeometry.api import api_o3dv_representation
from modules.visTaskManage.catalog import FUNCTIONS
from modules.visTaskManage.parameterRegistry import normalize_and_validate, parameter_contract


client = TestClient(app)


def test_health_identifies_current_runtime_layout() -> None:
    """健康端点必须让启动器区分模块化入口与仍连接旧库的遗留API。"""

    health = client.get("/api/health")
    assert health.status_code == 200
    payload = health.json()
    assert payload["entrypoint"] == "server.api"
    assert payload["runtime_layout"] == "var-v1"
    assert payload["artifacts"] > 0


def test_catalog_exact_counts_and_every_method_has_openable_case():
    catalog = client.get("/api/catalog").json()
    assert catalog["counts"] == {"families": 5, "kinds": 19, "functions": 23}
    assert {item["family"] for item in catalog["kinds"]} == {"PLT", "FLD", "ENT", "GEO", "ASSET"}
    all_case_ids = set()
    for kind in catalog["kinds"]:
        assert len(kind["examples"]) == len(kind["example_ids"])
        assert len(kind["example_ids"]) == len(kind["method_ids"])
        assert all(example["name"] and example["case_type_label"] for example in kind["examples"])
        for method_id, example_id in zip(kind["method_ids"], kind["example_ids"]):
            assert example_id in kind["example_ids"]
            all_case_ids.add(example_id)
            response = client.get(f"/api/examples/{example_id}")
            assert response.status_code == 200, f"{kind['id']}/{method_id}"
            payload = response.json()
            assert payload["artifact"]["kind"] == kind["id"]
            assert payload["resolved_spec"]["function_id"] == method_id
            assert "variant" not in payload["artifact"]
            assert payload["renderer"]["owner"]
            assert payload["data"], f"{kind['id']}/{method_id} has no visual data"
    assert len(all_case_ids) == 23


def test_function_registry_and_renderer_binding():
    registry = client.get("/api/specs").json()
    assert len(registry["functions"]) == 23
    catalog = client.get("/api/catalog").json()
    catalog_method_ids = {method_id for item in catalog["kinds"] for method_id in item["method_ids"]}
    assert catalog_method_ids == {item["id"] for item in registry["functions"]}
    assert all(len(item["compatible_kinds"]) == 1 for item in registry["functions"])
    assert all(item["accepted_formats"] for item in registry["functions"])
    assert all(item["example_id"] for item in registry["functions"])
    mesh = next(item for item in registry["functions"] if item["id"] == "scientific.mesh@2.0.0")
    assert mesh["renderer"] == "o3dv"
    assert registry["renderer_bindings"]["scientific.mesh@2.0.0"]["owner"] == "o3dv"
    assert all(item["status"] == "available" for item in registry["functions"])
    assert all("vizro" not in item["id"].lower() and item["renderer"] != "vizro" for item in registry["functions"])


def test_physical_field_methods_accept_npz():
    registry = client.get("/api/specs").json()["functions"]
    methods = {item["id"]: item for item in registry}
    assert "NPZ" in methods["scientific.field-scalar@2.1.0"]["accepted_formats"]
    assert "NPZ" in methods["scientific.field-vector@2.1.0"]["accepted_formats"]


def test_all_23_functions_have_draft_2020_12_schema_defaults_and_ui_groups():
    registry = client.get("/api/specs").json()["functions"]
    assert len(registry) == 23
    for function in registry:
        schema = function["parameter_schema"]
        assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
        assert schema["type"] == "object"
        assert schema["additionalProperties"] is False
        assert function["schema_revision"]
        assert function["ui_schema"]["groups"]
        normalized, errors = normalize_and_validate(function, {}, {}, function["default_parameters"])
        assert errors == [], function["id"]
        assert normalized == function["default_parameters"]
        _, illegal = normalize_and_validate(function, {}, {}, {"__script__": "alert(1)"})
        assert illegal and illegal[0]["validator"] == "additionalProperties"


def test_dynamic_parameter_enums_come_from_artifact_profile():
    recommendations = client.get("/api/artifacts/A-1025/recommendations").json()["candidates"]
    series = next(item for item in recommendations if item["kind"] == "series")
    properties = series["parameter_schema"]["properties"]
    assert "time" in properties["x"]["enum"]
    assert {"pitot_p1", "temp_t1"}.issubset(properties["y"]["items"]["enum"])
    assert series["default_parameters"]["x"] == "time"


@pytest.mark.parametrize("artifact_id", ["A-1027", "A-1031", "A-1033", "A-1114"])
def test_all_geo_examples_are_owned_by_o3dv(artifact_id):
    example = client.get(f"/api/examples/{artifact_id}").json()
    assert example["artifact"]["family"] == "GEO"
    assert example["renderer"]["owner"] == "o3dv"
    assert example["renderer"]["url"].startswith("http://testserver/")
    recommendation = client.get(f"/api/artifact/{artifact_id}/recommend").json()
    assert {item["renderer"] for item in recommendation["candidates"]} == {"o3dv"}


def test_example_asset_urls_follow_the_request_origin():
    image = client.get("/api/examples/A-1112").json()
    video = client.get("/api/examples/A-1113").json()
    assert image["data"]["url"] == "http://testserver/api/example-assets/A-1112"
    assert video["data"]["url"] == "http://testserver/api/example-assets/A-1113"
    assert video["data"]["poster_url"] == "http://testserver/api/example-assets/A-1112"


def test_field_is_separate_from_geo_and_trame_owned():
    field = client.get("/api/examples/A-1108").json()
    geometry = client.get("/api/examples/A-1027").json()
    assert field["artifact"]["kind"] == "field"
    assert field["renderer"]["owner"] == "trame-vtkjs"
    assert geometry["renderer"]["owner"] == "o3dv"


@pytest.mark.parametrize(
    ("artifact_id", "function_id", "view"),
    [
        ("CASE-RASTER-SCALAR", "scientific.raster-scalar@2.1.0", "raster"),
        ("CASE-RASTER-VECTOR", "scientific.raster-vector@2.1.0", "raster_vector"),
        ("CASE-VOLUME-SCALAR", "scientific.volume-scalar@2.1.0", "volume"),
        ("CASE-VOLUME-VECTOR", "scientific.volume-vector@2.1.0", "volume_vector"),
        ("CASE-FIELD-SCALAR", "scientific.field-scalar@2.1.0", "field"),
        ("CASE-FIELD-VECTOR", "scientific.field-vector@2.1.0", "field_vector"),
    ],
)
def test_scientific_methods_have_distinct_examples_and_trame_views(artifact_id, function_id, view):
    example = client.get(f"/api/examples/{artifact_id}")
    assert example.status_code == 200
    payload = example.json()
    assert payload["artifact"]["id"] == artifact_id
    assert payload["resolved_spec"]["function_id"] == function_id
    assert payload["renderer"]["owner"] == "trame-vtkjs"
    assert f"view={view}" in payload["renderer"]["url"]


def test_vtu_converts_to_valid_glb():
    response = client.get("/api/artifact/A-1027/representation/o3dv.glb")
    assert response.status_code == 200
    assert response.content[:4] == b"glTF"
    assert len(response.content) > 1000


def test_fusion_station_glb_is_profiled_and_streamed_without_conversion():
    parsed = client.get("/api/artifact/A-1114/parse")
    assert parsed.status_code == 200
    profile = parsed.json()
    assert profile["format"] == "GLB"
    assert profile["inferred_kind"] == "mesh"
    assert profile["mesh_structure"] == "multiblock"
    assert profile["geometries"] == 140
    assert profile["points"] == 1_828_671
    assert profile["cells"] == 2_658_695

    response = api_o3dv_representation("A-1114")
    source = Path(response.path)
    assert source.resolve() == (Path(DATA_DIR) / "fusion_station_geometry.glb").resolve()
    with source.open("rb") as handle:
        assert handle.read(4) == b"glTF"


def test_o3dv_static_fallback_is_a_real_png():
    response = client.get("/api/example-assets/A-1027-snapshot")
    assert response.status_code == 200
    assert response.content[:8] == b"\x89PNG\r\n\x1a\n"
    assert len(response.content) > 10_000


@pytest.mark.parametrize(
    ("artifact_id", "asset_id", "label"),
    [
        ("A-1028", "A-1028-trame-snapshot", "真实中截面静态证据"),
        ("A-1029", "A-1029-trame-snapshot", "真实轨迹 XY 投影"),
        ("A-1108", "A-1108-trame-snapshot", "真实场值二维索引视图"),
    ],
)
def test_trame_fallbacks_are_same_renderer_pngs(artifact_id, asset_id, label):
    example = client.get(f"/api/examples/{artifact_id}").json()
    assert example["renderer"]["owner"] == "trame-vtkjs"
    assert example["renderer"]["fallback"] == "same-renderer-snapshot"
    assert example["renderer"]["fallback_url"] == f"http://testserver/api/example-assets/{asset_id}"
    assert example["data"]["fallback_label"] == label

    response = client.get(f"/api/example-assets/{asset_id}")
    assert response.status_code == 200
    assert response.content[:8] == b"\x89PNG\r\n\x1a\n"
    assert len(response.content) > 10_000


def test_recommendation_scoring_and_incompatible_selection():
    response = client.get("/api/artifact/A-1025/recommend").json()
    scores = [item["score"] for item in response["candidates"]]
    assert scores == sorted(scores, reverse=True)
    assert response["candidates"][0]["score"] == 102
    bad = client.get("/api/artifact/A-1025/recommend", params={"function_id": "scientific.mesh@2.0.0"})
    assert bad.status_code == 422
    assert bad.json()["detail"]["code"] == "INCOMPATIBLE_FUNCTION"
    assert "chart.echarts-series@2.1.0" in bad.json()["detail"]["legal_alternatives"]


def test_spec_versions_are_immutable_and_stale_writes_conflict(tmp_path, monkeypatch):
    context_id = app.state.runtime.register({"scope": {"scope_id":"p:t", "project_id":"p", "task_id":"t", "root":str(tmp_path/"visualizations"), "writable":True}, "sources":[], "bindings":[]})["context_id"]
    monkeypatch.setenv("QODER_SPEC_DB", str(tmp_path / "specs.sqlite3"))
    payload = {"context_id": context_id, "spec_id": "vspec-test", "artifact_id": "A-1101", "function_id": "chart.echarts-scalar@2.1.0", "kind": "scalar", "params": {"unit": "%"}}
    created = client.post("/api/visualization-specs", json=payload)
    assert created.status_code == 201
    assert created.json()["version"] == 1
    assert "variant" not in created.json()
    version_two = client.post("/api/visualization-specs/vspec-test/versions", json={**payload, "base_version": 1, "params": {"unit": "%", "precision": 1}})
    assert version_two.status_code == 201
    assert version_two.json()["version"] == 2
    stale = client.post("/api/visualization-specs/vspec-test/versions", json={**payload, "base_version": 1})
    assert stale.status_code == 409
    assert stale.json()["detail"] == "visualization_revision_conflict"
    original = client.get("/api/visualization-specs/vspec-test/versions/1", params={"context_id":context_id}).json()
    assert original["params"] == {"unit": "%"}
    assert "variant" not in original


def test_all_reports_open_and_unknown_is_404():
    reports = client.get("/api/reports").json()["items"]
    seeded_report_ids = {
        "rep-2026-0818-a",
        "rep-2026-0814-b",
        "rep-2026-0812-c",
        "rep-2026-0811-d",
        "rep-gs-pino-2026-0823",
        "rep-miller-tokamak-timeseries",
    }
    report_ids = {report["id"] for report in reports}
    assert seeded_report_ids <= report_ids
    for report in reports:
        response = client.get(f"/api/reports/{report['id']}")
        assert response.status_code == 200
        payload = response.json()
        assert payload.get("sections") or payload.get("document", {}).get("sections")
    assert client.get("/api/reports/does-not-exist").status_code == 404


def test_seed_reports_use_current_references_without_false_error_blocks():
    gs = client.get("/api/reports/rep-gs-pino-2026-0823").json()
    assert gs["status"] == "succeeded"
    assert all(block["type"] != "error" for section in gs["sections"] for block in section["blocks"])
    assert "GS-AUDIT-001" not in json.dumps(gs, ensure_ascii=False)
    assert any(block.get("title") == "源文档口径说明" for section in gs["sections"] for block in section["blocks"])

    heater = client.get("/api/reports/rep-2026-0811-d").json()
    assert heater["status"] == "partial"
    assert "引用失效" not in heater["title"]
    assert "REF-SPEC-404" not in json.dumps(heater, ensure_ascii=False)
    examples = [block for section in heater["sections"] for block in section["blocks"] if block["type"] == "example"]
    assert [block["artifact_id"] for block in examples] == ["A-1030"]
    assert client.get("/api/examples/A-1030").json()["renderer"]["owner"] == "o3dv"
    heater_glb = client.get("/api/artifact/A-1030/representation/o3dv.glb")
    assert heater_glb.status_code == 200
    assert heater_glb.headers["content-type"].startswith("model/gltf-binary")
    assert heater_glb.content[:4] == b"glTF"


def test_negative_field_declaration_is_blocked():
    result = client.get("/api/artifact/A-1030/recommend").json()
    assert result["blocked"] is True
    assert result["error_issues"][0]["rule"] == "V-MESH-006"


def test_upload_is_persistent_deduplicated_and_creates_multiple_visual_tasks(tmp_path, monkeypatch):
    context_id = app.state.runtime.register({"scope": {"scope_id":"p:t", "project_id":"p", "task_id":"t", "root":str(tmp_path/"visualizations"), "writable":True}, "sources":[], "bindings":[]})["context_id"]
    database = tmp_path / "assets.sqlite3"
    upload_dir = tmp_path / "uploads"
    monkeypatch.setenv("QODER_ASSET_DB", str(database))
    monkeypatch.setenv("QODER_SPEC_DB", str(database))
    monkeypatch.setattr(data_assets_application, "UPLOAD_DIR", upload_dir)
    content = b"epoch,train_loss,val_loss\n1,1.0,1.2\n2,0.5,0.7\n3,0.25,0.42\n"

    first = client.post("/api/artifacts", files={"files": ("metrics.csv", content, "text/csv")})
    assert first.status_code == 201
    uploaded = first.json()["items"][0]
    artifact_id = uploaded["artifact"]["id"]
    task_ids = {item["recommendation_id"] for item in uploaded["recommendations"]["candidates"]}
    assert {"records-table", "ordered-series", "numeric-distribution"}.issubset(task_ids)

    duplicate = client.post("/api/artifacts", files={"files": ("same-content.csv", content, "text/csv")})
    assert duplicate.status_code == 201
    assert duplicate.json()["items"][0]["deduplicated"] is True
    assert duplicate.json()["items"][0]["artifact"]["id"] == artifact_id
    assert client.get(f"/api/artifacts/{artifact_id}").json()["parse_status"] == "ready"

    rendered = client.post(f"/api/artifacts/{artifact_id}/visualizations", json={"context_id":context_id,"recommendation_id": "ordered-series"})
    assert rendered.status_code == 201
    record = rendered.json()
    restored = client.get(f"/api/visualizations/{record['visualization_id']}", params={"context_id": context_id})
    assert restored.status_code == 200
    assert restored.json()["spec"]["method"]["renderer"] == "echarts-svg"
    assert restored.json()["payload"]["data"]["x"] == [1, 2, 3]


def test_preview_is_non_persistent_and_saved_visualization_versions_conflict(tmp_path, monkeypatch):
    context_id = app.state.runtime.register({"scope": {"scope_id":"p:t", "project_id":"p", "task_id":"t", "root":str(tmp_path/"visualizations"), "writable":True}, "sources":[], "bindings":[]})["context_id"]
    database = tmp_path / "visualizations.sqlite3"
    monkeypatch.setenv("QODER_ASSET_DB", str(database))
    monkeypatch.setenv("QODER_SPEC_DB", str(database))
    before = client.get("/api/visualizations",params={"context_id":context_id}).json()["items"]
    assert before == []
    preview = client.post("/api/artifacts/A-1025/visualizations/preview", json={"context_id":context_id,
        "recommendation_id": "time-series", "parameters": {"line_width": 3.5, "show_symbols": True}
    })
    assert preview.status_code == 200
    assert preview.json()["persisted"] is False
    assert preview.json()["preview"]["resolved_spec"]["params"]["line_width"] == 3.5
    assert client.get("/api/visualizations",params={"context_id":context_id}).json()["items"] == []

    first = client.post("/api/artifacts/A-1025/visualizations", json={"context_id":context_id,
        "recommendation_id": "time-series", "parameters": {"line_width": 3.5}
    })
    assert first.status_code == 201
    saved = first.json()
    second = client.post("/api/artifacts/A-1025/visualizations", json={"context_id":context_id,
        "recommendation_id": "time-series", "parameters": {"line_width": 4},
        "base_spec_id": saved["spec_id"], "base_version": saved["spec_version"],
    })
    assert second.status_code == 201
    assert second.json()["spec_version"] == 2
    stale = client.post("/api/artifacts/A-1025/visualizations", json={"context_id":context_id,
        "recommendation_id": "time-series", "parameters": {"line_width": 5},
        "base_spec_id": saved["spec_id"], "base_version": saved["spec_version"],
    })
    assert stale.status_code == 409
    assert stale.json()["detail"] == "visualization_revision_conflict"
    library = client.get("/api/visualizations",params={"context_id":context_id}).json()["items"]
    assert len(library) == 1
    assert library[0]["revision"] == 2
    assert all(item["content_hash"] and len(item["content_hash"]) == 64 for item in library)


def test_parameter_errors_are_json_pointer_localized():
    response = client.post("/api/artifacts/A-1025/visualizations/preview", json={
        "recommendation_id": "time-series", "parameters": {"line_width": 99, "x_scale": "impossible"}
    })
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert detail["code"] == "PARAMETER_VALIDATION_FAILED"
    assert {item["path"] for item in detail["errors"]} == {"/line_width", "/x_scale"}
    assert all(item["message"] for item in detail["errors"])


def test_report_draft_optimistic_lock_freeze_and_frozen_visualization_reference(tmp_path, monkeypatch):
    database = tmp_path / "reports.sqlite3"
    monkeypatch.setenv("QODER_ASSET_DB", str(database))
    monkeypatch.setenv("QODER_SPEC_DB", str(database))
    monkeypatch.setenv("QODER_REPORT_DB", str(database))
    from modules.visIO import create_visualization
    payload = client.get("/api/examples/A-1025?recommendation_id=time-series").json()
    visualization = create_visualization({"visualization_id":"legacy-viz", "artifact_id":"A-1025",
        "recommendation_id":"time-series", "spec_id":"legacy-spec", "spec_version":1,
        "function_id":"chart.echarts-line@2.1.0", "renderer":"echarts-svg", "parameters":{}, "payload":payload})
    report = client.post("/api/reports", json={
        "title": "参数审计报告", "author": "测试", "goal": "验证报告编排持久化",
        "audience": "工程团队", "template": "analysis", "key_questions": ["参数是否可追溯"]
    })
    assert report.status_code == 201
    draft = report.json()
    document = draft["document"]
    document["sections"][0]["rows"].append({"id": "row-viz-contract", "gap": 16, "align": "start", "blocks": [{
        "id": "block-viz-contract", "type": "visualization", "title": "真实冻结结果", "body": "",
        "source_ref": {
            "artifact_id": visualization["artifact_id"], "visualization_id": visualization["visualization_id"],
            "spec_id": visualization["spec_id"], "spec_version": visualization["spec_version"],
            "content_hash": visualization["content_hash"],
        },
        "layout": {"span": 12, "align": "stretch", "min_height": 120, "page_break_before": False, "keep_together": True, "hidden": False},
        "display": {"caption": "", "alt_text": "真实冻结结果", "show_source": True},
    }]})
    saved = client.patch(f"/api/reports/{draft['report_id']}/draft", json={"base_revision": 1, "document": document})
    assert saved.status_code == 200
    assert saved.json()["draft_revision"] == 2
    stale = client.patch(f"/api/reports/{draft['report_id']}/draft", json={"base_revision": 1, "document": document})
    assert stale.status_code == 409
    assert stale.json()["detail"]["code"] == "STALE_DRAFT_REVISION"
    frozen = client.post(f"/api/reports/{draft['report_id']}/versions", json={})
    assert frozen.status_code == 201
    assert frozen.json()["version"] == 1
    reader = client.get(f"/api/reports/{draft['report_id']}").json()
    assert reader["document"]["sections"][0]["rows"][-1]["blocks"][-1]["source_ref"]["content_hash"] == visualization["content_hash"]


def test_classification_correction_is_versioned_and_unlocks_detected_geo(tmp_path, monkeypatch):
    database = tmp_path / "classification.sqlite3"
    monkeypatch.setenv("QODER_ASSET_DB", str(database))
    before = client.get("/api/artifacts/A-1030/recommendations").json()
    assert before["blocked"] is True
    preview = client.get("/api/examples/A-1030").json()
    assert preview["artifact"]["validation"] == "warning"
    assert preview["renderer"]["owner"] == "o3dv"

    corrected = client.patch("/api/artifacts/A-1030/classification", json={"declared_kind": "mesh", "reason": "contract test"})
    assert corrected.status_code == 200
    detail = client.get("/api/artifacts/A-1030").json()
    assert detail["version"] == 2
    assert detail["validation_status"] == "passed"
    assert client.get("/api/artifacts/A-1030/recommendations").json()["blocked"] is False
    with sqlite3.connect(database) as connection:
        row = connection.execute("SELECT declared_kind, reason FROM artifact_classification_history WHERE artifact_id='A-1030' AND version=2").fetchone()
    assert row == ("mesh", "contract test")


@pytest.mark.parametrize(
    ("artifact_id", "kind", "renderer"),
    [
        ("A-1027", "mesh", "o3dv"),
        ("A-1028", "volume", "trame-vtkjs"),
        ("A-1029", "trajectory", "trame-vtkjs"),
        ("A-1032", "table", "perspective"),
    ],
)
def test_previously_broken_assets_return_real_payloads(artifact_id, kind, renderer):
    payload = client.get(f"/api/examples/{artifact_id}").json()
    assert payload["artifact"]["kind"] == kind
    assert payload["renderer"]["owner"] == renderer
    if artifact_id == "A-1028":
        assert payload["data"]["source_shape"] == [144, 112, 96]
        assert len(payload["data"]["values"]) > 10
    if artifact_id == "A-1029":
        assert payload["data"]["track_count"] == 900
        assert payload["data"]["frame_count"] == 160
        assert payload["data"]["tracks"][0][0] != payload["data"]["tracks"][0][-1]
    if artifact_id == "A-1032":
        assert payload["data"]["total_rows"] == 41_207
        tasks = client.get("/api/artifacts/A-1032/recommendations").json()["candidates"]
        assert {item["recommendation_id"] for item in tasks} == {"log-table", "log-levels", "log-residual"}


def test_grad_shafranov_fixture_and_report_are_data_derived():
    manifest_path = Path(GS_ROOT) / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert len(manifest["files"]) == 57
    assert manifest["geometries"]["circular"]["grid_shape"] == [151, 241]
    for item in manifest["files"]:
        path = Path(GS_ROOT) / item["path"]
        assert path.is_file()
        assert path.stat().st_size == item["size_bytes"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == item["sha256"]

    recommendations = client.get("/api/artifacts/GS-PINO-CIRCULAR/recommendations").json()
    assert {item["recommendation_id"] for item in recommendations["candidates"]} == {"gs-field", "gs-matrix", "gs-residual-distribution"}
    field = client.get("/api/examples/GS-PINO-CIRCULAR", params={"recommendation_id": "gs-field"}).json()
    assert field["data"]["source_shape"] == [151, 241]
    assert {"psi", "j_phi", "pde_residual", "plasma_mask"}.issubset(field["data"]["field_choices"])

    report = client.get("/api/reports/rep-gs-pino-2026-0823").json()
    block_types = {block["type"] for section in report["sections"] for block in section["blocks"]}
    assert {"training_curves", "geometry_errors", "image_gallery", "source", "example"}.issubset(block_types)
    assert "source_link" not in block_types
    assert any("200%" in takeaway for takeaway in report["takeaways"])
    assert "151×241" in report["summary"] or any("151×241" in block.get("message", "") for section in report["sections"] for block in section["blocks"])


def test_miller_npz_is_a_real_temporal_physical_field_and_report_source():
    fixture = Path(DATA_DIR) / "miller_tokamak_timeseries_240frames.npz"
    assert fixture.is_file()
    assert fixture.stat().st_size > 40_000_000
    assert hashlib.sha256(fixture.read_bytes()).hexdigest() == "bafe7524066a74e7c8b3416ea88a13739cae6ead3bcf6c68c7fc8fa961361b23"

    parsed = client.get("/api/artifact/A-1115/parse")
    assert parsed.status_code == 200
    profile = parsed.json()
    assert profile["inferred_kind"] == "field"
    assert profile["is_miller_tokamak"] is True
    assert profile["temporal_field"] is True
    assert profile["frames"] == 240
    assert profile["fps"] == 24
    assert profile["topology_shape"] == [148, 176]
    assert {"phi_surface_raw", "phi_surface_normalized"}.issubset(profile["field_arrays"])
    assert profile["vector_arrays"] == []
    assert "synthetic presentation field" in profile["scope"]

    recommendations = client.get("/api/artifacts/A-1115/recommendations").json()["candidates"]
    assert [(item["recommendation_id"], item["function_id"]) for item in recommendations] == [
        ("miller-surface-field", "scientific.field-scalar@2.1.0")
    ]
    preview = client.get("/api/examples/A-1115").json()
    assert preview["renderer"]["owner"] == "trame-vtkjs"
    assert "view=miller_field" in preview["renderer"]["url"]
    assert preview["data"]["source_shape"] == [240, 148, 176]
    assert preview["data"]["frame_count"] == 240
    assert preview["data"]["field"] == "phi_surface_normalized"
    assert len(preview["data"]["diagnostics"]) == 7

    report = client.get("/api/reports/rep-miller-tokamak-timeseries").json()
    block_types = {block["type"] for section in report["sections"] for block in section["blocks"]}
    assert {"example", "field_frames", "timeseries_diagnostics", "spectrum_heatmap", "source"}.issubset(block_types)
    assert "source_link" not in block_types
    assert "合成展示场" in json.dumps(report, ensure_ascii=False)
    assert client.get("/api/report-sources/miller-export-script").status_code == 404


def test_builtin_report_export_freezes_the_current_reader_payload(tmp_path, monkeypatch):
    monkeypatch.setenv("QODER_REPORT_DB", str(tmp_path / "reader-export.sqlite3"))
    monkeypatch.setattr(report_api, "start_export", lambda _export_id: None)

    response = client.post(
        "/api/reports/rep-miller-tokamak-timeseries/exports",
        json={"format": "html", "mode": "portable"},
    )
    assert response.status_code == 202
    task = response.json()
    assert task["source_report_id"] == "rep-miller-tokamak-timeseries"
    assert task["report_id"].startswith("reader-")

    frozen = client.get(f"/api/report-snapshots/{task['report_id']}/versions/{task['report_version']}")
    assert frozen.status_code == 200
    payload = frozen.json()
    assert payload["title"] == "Miller 托卡马克静电势时序场分析报告"
    assert "下载来源程序" not in json.dumps(payload, ensure_ascii=False)
    assert "下载 240 帧 NPZ" not in json.dumps(payload, ensure_ascii=False)
