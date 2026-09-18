"""资产、辅助操作和场景的版本化传输边界。"""

import asyncio
import hashlib
import json
from uuid import uuid4

from fastapi import APIRouter, Request
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, ConfigDict

from ...bootstrap.dependencies import services
from ...infrastructure.transport import finite_values
from .application import TERMINAL, archive_asset, asset, cancel, get_operation, register, submit
from .scenes import validate_scene

router = APIRouter(prefix="/projects/{project}")


class AssetRegistration(BaseModel):
    """浏览器使用受控根与相对路径登记。"""

    model_config = ConfigDict(extra="forbid")
    root: str
    path: str
    task_id: str | None = None


class PreviewOperation(BaseModel):
    """资产修订与有限显示操作。"""

    model_config = ConfigDict(extra="forbid")
    source: dict
    operation: str = "transform"
    options: dict = {}
    idempotency_key: str | None = None


@router.post("/assets")
def register_asset(project: str, body: AssetRegistration, request: Request):
    """登记内容身份。"""
    return register(services(request), project, body.root, body.path, body.task_id)


@router.get("/assets")
def assets(project: str, request: Request):
    """列出已登记固定资产，不暴露路径。"""
    services(request).project(project)
    return [
        v["ref"] for v in services(request).store.list("asset") if v["ref"]["project_id"] == project
    ]


@router.get("/assets/{identity}/content")
def content(
    project: str,
    identity: str,
    request: Request,
    member: str | None = None,
    revision: str | None = None,
    download: bool = False,
):
    """下载受控文件或显示二进制成员。"""
    ref = {"asset_id": identity}
    if revision:
        ref["revision"] = revision
    root = asset(services(request), project, ref)
    if download and member is None and root.is_dir():
        path, filename = archive_asset(services(request), project, ref)
        return FileResponse(path, filename=filename, media_type="application/zip")
    path = root if member is None else (root / member).resolve()
    if member is not None and (
        not root.is_dir()
        or not path.is_relative_to(root)
        or any(p.startswith(".") for p in __import__("pathlib").Path(member).parts)
    ):
        raise ValueError("asset_member_outside_root")
    if not path.is_file():
        raise ValueError("file_required")
    return FileResponse(path, filename=path.name if download else None)


@router.post("/visualization/operations")
@router.post("/previews/operations")
def operation(project: str, body: PreviewOperation, request: Request):
    """提交有限 viz 操作。"""
    if body.operation not in {"inspect", "read_slice", "summarize", "transform"}:
        raise ValueError("unsupported_preview_operation")
    return submit(services(request), project, body.model_dump())


@router.get("/operations/{identity}")
def status(project: str, identity: str, request: Request):
    """读取辅助操作状态。"""
    return get_operation(services(request), project, identity)


@router.post("/operations/{identity}/cancel")
def stop(project: str, identity: str, request: Request, body: dict | None = None):
    """请求取消转换。"""
    return cancel(services(request), project, identity, (body or {}).get("subscription_id"))


@router.get("/operations/{identity}/events")
async def events(project: str, identity: str, request: Request):
    """订阅状态修订，重连不会重启计算。"""
    service = services(request)
    get_operation(service, project, identity)

    async def stream():
        last = -1
        while not await request.is_disconnected():
            value = get_operation(service, project, identity)
            if value["event_cursor"] != last:
                last = value["event_cursor"]
                yield f"id: {last}\ndata: {json.dumps(finite_values(value), ensure_ascii=False, allow_nan=False)}\n\n"
            if value["status"] in TERMINAL:
                break
            await asyncio.sleep(0.3)

    return StreamingResponse(stream(), media_type="text/event-stream")


@router.get("/scenes")
def scenes(project: str, request: Request):
    """查询本项目保存的场景。"""
    services(request).project(project)
    return [v for v in services(request).store.list("scene") if v["project_id"] == project]


@router.get("/scenes/{identity}")
def scene(project: str, identity: str, request: Request):
    """读取固定修订场景。"""
    value = services(request).store.get("scene", identity)
    if value["project_id"] != project:
        raise KeyError(identity)
    return value


@router.post("/scenes")
def create_scene(project: str, body: dict, request: Request):
    """保存场景，核验固定数据来源。"""
    return _save_scene(project, uuid4().hex, body, request, False)


@router.put("/scenes/{identity}")
def update_scene(project: str, identity: str, body: dict, request: Request):
    """按修订修改场景。"""
    return _save_scene(project, identity, body, request, True)


def _save_scene(project, identity, body, request, update):
    service = services(request)
    service.project(project)
    document = body.get("scene", body)
    validate_scene(document)
    for source in document.get("sources", []):
        asset(service, project, source)
    if update:
        scene(project, identity, request)
    rev = hashlib.sha256(json.dumps(document, sort_keys=True).encode()).hexdigest()
    value = {"scene_id": identity, "project_id": project, "revision": rev, "scene": document}
    if update:
        return service.store.compare_and_swap(
            "scene", identity, value, expected_revision=body.get("expected_revision")
        )
    return service.store.put("scene", identity, value)


@router.get('/tasks/{task_id}/visualizations/sources')
def visualizable_sources(
    project: str,
    task_id: str,
    request: Request,
    root: str | None = None,
    path: str = "",
):
    """列出任务产物、共享数据集和已挂数据根中的可视化网格。"""
    from .bindings import list_visualizable_sources

    return list_visualizable_sources(services(request), project, task_id, root, path)


@router.get('/tasks/{task_id}/visualizations')
def task_visualizations(project: str, task_id: str, request: Request):
    """列出任务保存的可视化配置资产。"""
    from .bindings import list_saved
    return list_saved(services(request), project, task_id)


@router.get('/tasks/{task_id}/visualizations/{identity}')
def task_visualization(project: str, task_id: str, identity: str, request: Request, revision: int | None = None):
    """读取固定配置修订。"""
    from .bindings import read_saved
    return read_saved(services(request), project, task_id, identity, revision)


@router.post('/tasks/{task_id}/visualizations')
def save_task_visualization(project: str, task_id: str, request: Request, body: dict):
    """保存到 task 授权区域，不创建研究版本。"""
    from .bindings import save
    return save(services(request), project, task_id, body)


@router.post('/tasks/{task_id}/visualizations/sessions')
def open_physical_session(project: str, task_id: str, request: Request, body: dict):
    """文件、后处理、比较共用独立物理场工作区。"""
    from .bindings import open_session
    return open_session(services(request), project, task_id, body)


@router.delete('/tasks/{task_id}/visualizations/sessions/{identity}')
def close_physical_session(project: str, task_id: str, identity: str, request: Request):
    """页面关闭后释放所属工作区。"""
    from .bindings import close_session
    return close_session(services(request), project, task_id, identity)


@router.post('/tasks/{task_id}/visualizations/sessions/{identity}/sources')
def append_physical_sources(project: str, task_id: str, identity: str, request: Request, body: dict):
    """浏览器仅提供已登记来源引用，不提供实际文件位置。"""
    from .bindings import append_session_sources
    return append_session_sources(services(request),project,task_id,identity,body['sources'])
