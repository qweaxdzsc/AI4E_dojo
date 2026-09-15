"""宿主只代理 Vis 公共展示路由，拒绝内部上下文登记与任意目标。"""

import asyncio

import aiohttp
from fastapi import APIRouter, HTTPException, Request, WebSocket
from fastapi.responses import Response

router = APIRouter()


def allowed(path):
    """内部控制 API 永远不能从浏览器代理访问。"""
    return not any(part in (".", "..") for part in path.split("/")) and path.startswith(
        ("workspace/", "api/phys/", "api/contexts/", "api/visualizations")
    )


@router.api_route("/vis/{path:path}", methods=["GET", "POST", "DELETE"])
async def proxy(request: Request, path: str):
    """只向已配置的本机 Vis 进程转发。"""
    if not allowed(path):
        raise HTTPException(404)
    service = request.app.state.services
    if request.method == "POST" and path.startswith("api/visualizations"):
        import ai4e_task as task

        identity = request.query_params.get("context_id")
        if not identity and "application/json" in request.headers.get("content-type", ""):
            identity = (await request.json()).get("context_id")
        binding = service.vis_contexts.get(identity)
        if not binding:
            raise HTTPException(403, "host_context_required")
        task.visualization_storage(service.project(binding["project"]), binding["task"], write=True)
    client = service.vis
    await asyncio.to_thread(client.start)
    target = client.url + "/" + path + ("?" + request.url.query if request.url.query else "")
    async with (
        aiohttp.ClientSession() as session,
        session.request(
            request.method,
            target,
            data=await request.body(),
            headers={
                k: v for k, v in request.headers.items() if k.lower() in ("content-type", "accept")
            },
        ) as response,
    ):
        return Response(
            await response.read(),
            status_code=response.status,
            headers={
                k: v
                for k, v in response.headers.items()
                if k.lower() in ("content-type", "content-disposition", "cache-control")
            },
        )


@router.websocket("/vis/{path:path}")
async def stream(websocket: WebSocket, path: str):
    """双向传输独立工作区的 WebSocket 帧。"""
    if not path.startswith("api/phys/view/") or not allowed(path):
        await websocket.close(code=1008)
        return
    client = websocket.app.state.services.vis
    await asyncio.to_thread(client.start)
    target = client.url + "/" + path + ("?" + websocket.url.query if websocket.url.query else "")
    await websocket.accept()
    async with (
        aiohttp.ClientSession() as session,
        session.ws_connect(target, max_msg_size=0) as remote,
    ):

        async def inbound():
            while True:
                message = await websocket.receive()
                if message["type"] == "websocket.disconnect":
                    return
                if message.get("bytes") is not None:
                    await remote.send_bytes(message["bytes"])
                elif message.get("text") is not None:
                    await remote.send_str(message["text"])

        async def outbound():
            async for message in remote:
                if message.type == aiohttp.WSMsgType.BINARY:
                    await websocket.send_bytes(message.data)
                elif message.type == aiohttp.WSMsgType.TEXT:
                    await websocket.send_text(message.data)
                elif message.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR):
                    return

        jobs = [asyncio.create_task(inbound()), asyncio.create_task(outbound())]
        try:
            await asyncio.wait(jobs, return_when=asyncio.FIRST_COMPLETED)
        finally:
            for job in jobs:
                job.cancel()
            await asyncio.gather(*jobs, return_exceptions=True)
