"""三维物理场统一HTTP适配层。

全部二级业务共用此Router，由 ``server.api`` 统一注册，禁止二级模块重复建立路由。
"""

from fastapi import APIRouter

router = APIRouter(tags=["visPhysField"])

from fastapi import Request, WebSocket
from infrastructure.web.proxy import http_proxy, websocket_proxy

from . import default_spec


@router.post("/api/phys/sessions")
def create_session(request: Request, body: dict):
    """建立独立工作区，可显式提供配置或使用受控来源。"""
    runtime = request.app.state.runtime
    context = runtime.context(body.get("context_id"))
    spec = body.get("spec") or default_spec(context["sources"])
    if body.get("renderer"):
        spec = {**spec, "renderer": body["renderer"]}
    return runtime.sessions.create(context, spec)


@router.post("/api/phys/sessions/{identity}/commands")
def command(identity: str, request: Request, body: dict):
    """传输声明式命令，实际计算在工作进程内执行。"""
    return request.app.state.runtime.sessions.command(
        identity, body.get("context_id"), body["command"]
    )


@router.delete("/api/phys/sessions/{identity}")
def close(identity: str, request: Request, context_id: str):
    """显式关闭工作区。"""
    return request.app.state.runtime.sessions.close(identity, context_id)


@router.post("/api/phys/sessions/{identity}/heartbeat")
def heartbeat(identity: str, request: Request, body: dict):
    """活动页面刷新租约；关闭页面后自然回收。"""
    request.app.state.runtime.sessions.get(identity, body.get("context_id"))
    return {"status": "alive"}


@router.api_route("/api/phys/view/{context_id}/{identity}/{path:path}", methods=["GET", "POST"])
async def view(context_id: str, identity: str, path: str, request: Request):
    """提供受上下文约束的 Trame 页面和静态资源。"""
    item = request.app.state.runtime.sessions.get(identity, context_id)
    return await http_proxy(request, f"http://127.0.0.1:{item['port']}", path)


@router.websocket("/api/phys/view/{context_id}/{identity}/{path:path}")
async def stream(context_id: str, identity: str, path: str, websocket: WebSocket):
    """实时连接保持工作区隔离。"""
    item = websocket.app.state.runtime.sessions.get(identity, context_id)
    await websocket_proxy(websocket, f"http://127.0.0.1:{item['port']}", path)


@router.post("/api/phys/sessions/{identity}/sources")
def append_registered(identity: str, request: Request, body: dict):
    """独立应用选择登记资产，宿主来源必须经过宿主控制通道。"""
    from .application import append_registered_source

    return append_registered_source(
        request.app.state.runtime,
        identity,
        body["context_id"],
        body["asset_id"],
        body.get("member", ""),
    )
