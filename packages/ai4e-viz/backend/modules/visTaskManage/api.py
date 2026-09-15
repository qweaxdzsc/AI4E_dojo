"""可视化任务管理的 HTTP 适配层。

本 Router 拥有方法 Schema 与 VisualizationSpec 版本接口。它只调用本模块公开用例，
负责把字段校验、未找到和乐观锁冲突转换为稳定 HTTP 响应，不直接执行 SQL。
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Body, HTTPException, Request

from . import append_version, create_spec, get_version, list_specs, list_versions
from .catalog import FUNCTIONS, KINDS, canonical_function, catalog_response, function_response
from .parameterRegistry import enrich_function
from modules.dataAssets import get_artifact
from modules.visDatasets import build_example, ensure_builtin_artifacts, recommend_artifact
from .examples import CASES, example_payload


router = APIRouter(tags=["visTaskManage"])


@router.get("/api/catalog")
def api_catalog() -> dict:
    """返回 5 家族、19 语义类型、23 方法及其可运行案例摘要。"""

    ensure_builtin_artifacts()

    def example_entry(artifact_id: str) -> dict:
        """把案例标识转换为目录使用的公开摘要。"""

        case = CASES.get(artifact_id)
        if case is not None:
            return {
                "id": case["id"], "name": case["name"],
                "case_type": case["case_type"], "case_type_label": case["case_type_label"],
            }
        try:
            artifact = get_artifact(artifact_id)
        except KeyError:
            return {"id": artifact_id, "name": artifact_id, "case_type": "generated-demo", "case_type_label": "确定性生成演示"}
        return {
            "id": artifact_id, "name": artifact["name"],
            "case_type": "file-fixture", "case_type_label": "文件型工程案例",
        }

    payload = catalog_response()
    payload["kinds"] = [
        {**kind, "examples": [example_entry(artifact_id) for artifact_id in kind["example_ids"]]}
        for kind in payload["kinds"]
    ]
    return payload


@router.get("/api/examples/{artifact_id}")
def api_example(artifact_id: str, request: Request, recommendation_id: str | None = None) -> dict:
    """返回确定性生成案例，或根据真实文件画像生成可运行案例。"""

    ensure_builtin_artifacts()
    try:
        stored = get_artifact(artifact_id)
        dynamic_builtin = {"A-1027", "A-1028", "A-1029", "A-1030", "A-1031", "A-1032", "A-1033", "A-1108", "A-1114", "A-1115"}
        if stored["source"] in {"uploaded", "gs-fixture"} or artifact_id in dynamic_builtin:
            return build_example(artifact_id, str(request.base_url), recommendation_id)
        if artifact_id in CASES:
            return example_payload(artifact_id, str(request.base_url))
        return build_example(artifact_id, str(request.base_url), recommendation_id)
    except KeyError as exc:
        if artifact_id not in CASES:
            raise HTTPException(404, f"未知案例 Artifact: {artifact_id}") from exc
        return example_payload(artifact_id, str(request.base_url))


@router.get("/api/artifact/{artifact_id}/recommend")
def api_recommend(artifact_id: str, function_id: str | None = None) -> dict:
    """返回指定数据资产的推荐，允许按方法标识选择候选。"""

    return recommend_artifact(artifact_id, function_id=function_id)


@router.get("/api/artifacts/{artifact_id}/recommendations")
def api_artifact_recommendations(artifact_id: str) -> dict:
    """返回数据资产的完整确定性推荐候选集合。"""

    return recommend_artifact(artifact_id)


def _validate_spec_payload(payload: dict) -> dict:
    """校验并规范 VisualizationSpec 请求，不允许类型和方法不兼容。"""

    required = ["artifact_id", "function_id", "kind"]
    missing = [key for key in required if not payload.get(key)]
    if missing:
        raise HTTPException(422, detail={"code": "SPEC_FIELDS_REQUIRED", "fields": missing})
    kind = next((item for item in KINDS if item["id"] == payload["kind"]), None)
    if kind is None:
        raise HTTPException(422, detail={"code": "UNKNOWN_KIND", "field": "kind"})
    normalized_function = canonical_function(payload["function_id"])
    function = next((item for item in FUNCTIONS if item["id"] == normalized_function), None)
    legal = [item["id"] for item in FUNCTIONS if payload["kind"] in item["compatible_kinds"]]
    if function is None or payload["kind"] not in function["compatible_kinds"]:
        raise HTTPException(422, detail={"code": "INCOMPATIBLE_FUNCTION", "field": "function_id", "legal_alternatives": legal})
    clean = {key: payload[key] for key in required}
    clean["function_id"] = normalized_function
    clean["params"] = payload.get("params", {})
    if not isinstance(clean["params"], dict):
        raise HTTPException(422, detail={"code": "INVALID_PARAMS", "field": "params"})
    return clean


@router.get("/api/specs")
def api_specs() -> dict:
    """返回包含参数 Schema 的 23 种可视化方法。"""

    response = function_response()
    response["functions"] = [enrich_function(item) for item in response["functions"]]
    return response


@router.get("/api/visualization-specs")
def api_visualization_specs() -> dict:
    """列出 VisualizationSpec 的当前版本摘要。"""

    return {"items": list_specs()}


@router.post("/api/visualization-specs", status_code=201)
def api_create_visualization_spec(request: Request, payload: dict = Body(...)) -> dict:
    """创建 VisualizationSpec 首版，重复标识返回冲突。"""

    from .application import save_method_config
    context = request.app.state.runtime.context(payload.get('context_id'))
    return save_method_config(context, _validate_spec_payload(payload), payload.get('spec_id') or None)


@router.get("/api/visualization-specs/{spec_id}/versions")
def api_visualization_spec_versions(spec_id: str, request: Request, context_id: str | None = None) -> dict:
    """列出指定 VisualizationSpec 的不可变版本。"""

    if context_id:
        from modules.visIO import read_asset
        saved = read_asset(request.app.state.runtime.context(context_id)['scope'], spec_id)
        return {'items': [{'spec_id': spec_id, 'version': revision} for revision in range(saved['revision'], 0, -1)]}
    items = list_versions(spec_id)
    if not items:
        raise HTTPException(404, f"未知 VisualizationSpec: {spec_id}")
    return {"items": items}


@router.get("/api/visualization-specs/{spec_id}/versions/{version}")
def api_visualization_spec_version(spec_id: str, version: int, request: Request, context_id: str | None = None) -> dict:
    """读取指定 VisualizationSpec 版本。"""

    if context_id:
        from modules.visIO import read_asset
        saved = read_asset(request.app.state.runtime.context(context_id)['scope'], spec_id, version)
        spec = saved['spec']
        return {'spec_id': spec_id, 'version': version, 'artifact_id': spec['sources'][0]['ref']['asset_id'], 'function_id': spec['method']['function_id'], 'kind': spec['kind'], 'params': spec['parameters']}
    try:
        return get_version(spec_id, version)
    except KeyError as exc:
        raise HTTPException(404, f"未知 VisualizationSpec 版本: {spec_id}@{version}") from exc


@router.post("/api/visualization-specs/{spec_id}/versions", status_code=201)
def api_append_visualization_spec(spec_id: str, request: Request, payload: dict = Body(...)) -> dict:
    """基于显式基线追加版本，过期基线返回可恢复冲突。"""

    from .application import save_method_config
    context = request.app.state.runtime.context(payload.get('context_id'))
    return save_method_config(context, _validate_spec_payload(payload), spec_id, payload['base_version'])
