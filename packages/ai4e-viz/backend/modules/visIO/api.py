"""可视化资产保存、预览和查询 HTTP 接口。

Router 只处理协议与错误转换。数据画像和案例构造来自 ``visDatasets`` 公开门面，参数和
Spec 版本来自 ``visTaskManage`` 公开门面，可视化记录只由本模块 Repository 持久化。
"""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Body, HTTPException, Request

from modules.dataAssets import get_artifact
from modules.visDatasets import build_example, recommend_artifact
from modules.visTaskManage import list_versions, save_visualization_spec, validate_visualization_parameters

from . import create_visualization, get_visualization, list_visualizations

router = APIRouter(tags=["visIO"])


def _parameter_validation_error(errors: list[dict[str, Any]]) -> HTTPException:
    """把 JSON Schema 错误转换为稳定的中文 API 错误。"""

    labels = {
        "enum": "值不在允许范围内", "minimum": "数值低于允许下限",
        "maximum": "数值超过允许上限", "type": "参数类型不正确",
        "additionalProperties": "包含未注册参数", "pattern": "格式不符合要求",
        "maxItems": "选择项数量过多", "uniqueItems": "选择项不能重复",
    }
    localized = [
        {**item, "message": labels.get(item.get("validator"), item.get("message", "参数不合法"))}
        for item in errors
    ]
    return HTTPException(
        422,
        detail={"code": "PARAMETER_VALIDATION_FAILED", "message": "可视化参数校验失败", "errors": localized},
    )


def _selected_recommendation(artifact_id: str, recommendation_id: str) -> tuple[dict, dict, dict]:
    """读取资产和指定推荐，不允许调用方绕过合法候选集合。"""

    recommendations = recommend_artifact(artifact_id)
    candidates = recommendations.get("detected_candidates", recommendations.get("candidates", []))
    selected = next((item for item in candidates if item["recommendation_id"] == recommendation_id), None)
    if selected is None:
        raise HTTPException(
            422,
            detail={"code": "UNKNOWN_RECOMMENDATION", "legal": [item["recommendation_id"] for item in candidates]},
        )
    try:
        stored = get_artifact(artifact_id)
    except KeyError as exc:
        raise HTTPException(404, f"未知 Artifact: {artifact_id}") from exc
    return stored, recommendations, selected


def _validated_parameters(stored: dict, selected: dict, parameters: object) -> dict:
    """通过任务模块公开用例校验参数，并保持本 Router 的错误协议。"""

    try:
        normalized, errors = validate_visualization_parameters(
            selected["function_id"], stored.get("profile") or {}, selected.get("encoding") or {}, parameters
        )
    except KeyError as exc:
        raise HTTPException(422, detail={"code": "UNKNOWN_FUNCTION", "function_id": selected["function_id"]}) from exc
    if errors:
        raise _parameter_validation_error(errors)
    return normalized


def _representation_manifest(rendered: dict, generated_at: str | None = None) -> dict:
    """为同一冻结业务结果建立交互与静态表现清单。"""

    renderer = rendered["renderer"]
    timestamp = generated_at or datetime.now().astimezone().isoformat()
    static_url = renderer.get("fallback_url")
    return {
        "interactive": {
            "owner": renderer["owner"], "url": renderer.get("url"),
            "status": renderer.get("status", "partial"), "generated_at": timestamp,
        },
        "static": {
            "owner": renderer["owner"], "url": static_url,
            "status": "available" if static_url else "pending",
            "mode": "same-renderer" if static_url else "same-renderer-capture-required",
            "generated_at": timestamp if static_url else None,
        },
    }


@router.post("/api/artifacts/{artifact_id}/visualizations/preview")
def api_preview_artifact_visualization(artifact_id: str, request: Request, payload: dict = Body(...)) -> dict:
    """校验并渲染预览，但不创建 Spec 或可视化记录。"""

    recommendation_id = str(payload.get("recommendation_id") or "")
    stored, recommendations, selected = _selected_recommendation(artifact_id, recommendation_id)
    if recommendations.get("blocked"):
        raise HTTPException(422, detail={"code": "VALIDATION_BLOCKED", "message": "请先修正声明类型，或按检测到的几何预览。", "legal_detected_kind": recommendations.get("kind")})
    normalized = _validated_parameters(stored, selected, payload.get("parameters") or {})
    rendered = build_example(artifact_id, str(request.base_url), recommendation_id, normalized)
    parameter_hash = hashlib.sha256(
        json.dumps(normalized, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()[:16]
    return {
        "preview": rendered, "normalized_parameters": normalized,
        "schema_revision": selected.get("schema_revision"), "persisted": False,
        "parameter_hash": parameter_hash,
    }


@router.post("/api/artifacts/{artifact_id}/visualizations", status_code=201)
def api_create_artifact_visualization(artifact_id: str, request: Request, payload: dict = Body(...)) -> dict:
    """在参数与基线校验成功后原子创建 Spec 版本和可视化资产。"""

    from .application import save_scoped
    context = request.app.state.runtime.context(payload.get('context_id'))
    if 'spec' not in payload:
        from .application import save_catalog
        return save_catalog(context, artifact_id, payload)
    return save_scoped(context, payload)


@router.get("/api/visualizations")
def api_visualizations(
    request: Request,
    context_id: str | None = None,
    artifact_id: str | None = None,
    kind: str | None = None,
    renderer: str | None = None,
    dataset_id: str | None = None,
    include_payload: bool = False,
) -> dict:
    """按资产、数据集、类型或渲染器列出可视化资产。"""

    if context_id:
        from . import list_assets
        return {"items": list_assets(request.app.state.runtime.context(context_id)["scope"])}
    items = list_visualizations(artifact_id=artifact_id, kind=kind, renderer=renderer, dataset_id=dataset_id)
    result = []
    for item in items:
        payload = item.get("payload") or {}
        artifact = payload.get("artifact") or {}
        public = {
            "visualization_id": item["visualization_id"], "artifact_id": item["artifact_id"],
            "spec_id": item["spec_id"], "spec_version": item["spec_version"],
            "function_id": item["function_id"], "renderer": item["renderer"], "status": item["status"],
            "created_at": item["created_at"], "updated_at": item.get("updated_at") or item["created_at"],
            "name": artifact.get("name") or item["visualization_id"], "kind": artifact.get("kind"),
            "family": artifact.get("family"), "takeaway": artifact.get("takeaway"),
            "parameters": item["parameters"], "representations": item.get("representations", {}),
            "content_hash": item["content_hash"],
        }
        if include_payload:
            public["payload"] = payload
        result.append(public)
    return {"items": result, "updated_at": max((item["updated_at"] for item in result), default=None)}


@router.get("/api/visualizations/{visualization_id}")
def api_visualization(visualization_id: str, request: Request, context_id: str | None = None, revision: int | None = None) -> dict:
    """读取一个可视化资产的冻结参数、表现和内容摘要。"""

    if context_id:
        from .application import read_catalog
        return read_catalog(request.app.state.runtime.context(context_id), visualization_id, revision, str(request.base_url))
    try:
        return get_visualization(visualization_id)
    except KeyError as exc:
        raise HTTPException(404, f"未知可视化: {visualization_id}") from exc


@router.post('/api/visualizations', status_code=201)
def save_task_visualization(request: Request, payload: dict = Body(...)):
    """新保存协议必须绑定任务上下文。"""
    from .application import save_scoped
    context = request.app.state.runtime.context(payload.get('context_id'))
    return save_scoped(context, payload)


@router.post('/api/visualizations/{visualization_id}/exports', status_code=202)
def export_task_visualization(visualization_id: str, request: Request, payload: dict = Body(...)):
    """显式生成固定修订输出。"""
    runtime = request.app.state.runtime
    return runtime.exports.create(runtime.context(payload.get('context_id')), visualization_id, payload['revision'], payload['options'])


@router.get('/api/visualizations/{visualization_id}/exports/{export_id}')
def export_status(visualization_id: str, export_id: str, request: Request, context_id: str):
    """输出状态与保存修订独立。"""
    from . import get_export
    return get_export(request.app.state.runtime.context(context_id)['scope'], visualization_id, export_id)


@router.post('/api/visualizations/{visualization_id}/exports/{export_id}/cancel')
def cancel_export(visualization_id: str, export_id: str, request: Request, payload: dict = Body(...)):
    """取消任务输出。"""
    runtime = request.app.state.runtime
    return runtime.exports.cancel(runtime.context(payload.get('context_id'))['scope'], visualization_id, export_id)


@router.get('/api/visualizations/{visualization_id}/exports/{export_id}/files/{name}')
def download_export(visualization_id: str, export_id: str, name: str, request: Request, context_id: str):
    """只下载成功清单中的文件，禁止任意路径访问。"""
    from fastapi.responses import FileResponse
    from . import get_export, export_root
    scope = request.app.state.runtime.context(context_id)['scope']
    manifest = get_export(scope, visualization_id, export_id)
    if manifest['status'] != 'succeeded' or name not in [f['name'] for f in manifest['files']]:
        raise ValueError('export_file_not_committed')
    return FileResponse(export_root(scope, visualization_id, export_id)/name, filename=name)


@router.post('/api/visualizations/{visualization_id}/recordings')
async def upload_recording(visualization_id: str, request: Request, context_id: str, revision: int):
    """显式录制上传到当前任务。"""
    from . import recording
    content = bytearray()
    async for chunk in request.stream():
        content.extend(chunk)
        if len(content) > 256*1024*1024:
            raise ValueError('recording_too_large')
    return recording(request.app.state.runtime.context(context_id)['scope'], visualization_id, revision, bytes(content))
