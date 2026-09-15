"""AI4E_Vis FastAPI 进程装配入口。

Server只创建应用、配置跨域、注册十三级一级模块Router，并暴露技术健康检查。
业务规则、SQL、文件解析和渲染逻辑全部留在所属模块或 Infrastructure。
"""

from __future__ import annotations

import argparse
import asyncio
import hmac
from contextlib import asynccontextmanager
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from .runtime import Runtime

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from infrastructure.config import REPOSITORY_ROOT
from infrastructure.observability.health import renderer_health
from modules.dataAssets import list_artifacts
from modules.dataAssets.api import router as data_assets_router
from modules.MCP.api import router as mcp_router
from modules.automation.api import router as automation_router
from modules.reportDesigner.api import router as report_designer_router
from modules.reportManage.api import router as report_manage_router
from modules.visConvertor.api import router as vis_convertor_router
from modules.visDatasets import ensure_builtin_artifacts
from modules.visDatasets.api import router as vis_datasets_router
from modules.visFigure.api import router as vis_figure_router
from modules.visGeometry.api import router as vis_geometry_router
from modules.visIO.api import router as vis_io_router
from modules.visPhysField.api import router as vis_phys_field_router
from modules.visTaskManage.api import router as vis_task_manage_router
from modules.visTaskManage.catalog import catalog_response


@asynccontextmanager
async def lifespan(app):
    async def reap():
        while True:
            await asyncio.sleep(30)
            app.state.runtime.sessions.reap()
    job = asyncio.create_task(reap())
    yield
    job.cancel()
    app.state.runtime.shutdown()


app = FastAPI(lifespan=lifespan, title="AI4E VizReport · 解析/推荐/上传 API", version="2.0")
app.state.runtime = Runtime()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

health_router = APIRouter(tags=["server"])


@health_router.get("/api/health")
def health() -> dict:
    """确认 API 可用并返回内置资产数与目录修订号。"""

    ensure_builtin_artifacts()
    return {
        "ok": True, "service": "ai4e-vizreport-api",
        "entrypoint": "server.api", "runtime_layout": "var-v1",
        "artifacts": len(list_artifacts()), "revision": catalog_response()["revision"],
    }


@health_router.get("/api/renderer-health")
def api_renderer_health() -> dict:
    """返回浏览器 Renderer 与 Trame 服务的技术健康状态。"""

    return renderer_health(REPOSITORY_ROOT)


for module_router in (
    health_router,
    data_assets_router,
    vis_task_manage_router,
    vis_geometry_router,
    vis_datasets_router,
    vis_phys_field_router,
    vis_figure_router,
    vis_io_router,
    vis_convertor_router,
    automation_router,
    mcp_router,
    report_manage_router,
    report_designer_router,
):
    app.include_router(module_router)


def main() -> None:
    """解析命令行参数并启动唯一 FastAPI 进程。"""

    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8091)
    parser.add_argument("--host", default="127.0.0.1")
    args = parser.parse_args()
    import uvicorn

    print(f"[api] AI4E_Vis service on http://{args.host}:{args.port}/", flush=True)
    uvicorn.run(app, host=args.host, port=args.port, log_level="warning")

__all__ = ["app", "main"]




@app.exception_handler(ValueError)
async def value_error(request, exc):
    """稳定错误语义，保存冲突单独返回 409。"""
    return JSONResponse({'detail': str(exc)}, status_code=409 if 'conflict' in str(exc) else 422)


@app.exception_handler(KeyError)
@app.exception_handler(FileNotFoundError)
async def missing_error(request, exc):
    """数据缺失与未知上下文不会冒充成功。"""
    return JSONResponse({'detail': str(exc)}, status_code=404)


@app.post('/internal/contexts')
def register_context(request: Request, body: dict):
    """仅可信宿主控制通道可登记实际文件位置。"""
    if not hmac.compare_digest(request.headers.get('x-vis-control', ''), app.state.runtime.control_token):
        raise HTTPException(403, 'trusted_host_required')
    return app.state.runtime.register(body)


@app.get('/api/contexts/{identity}')
def context_summary(identity: str):
    """浏览器读取可用来源与目标身份，不暴露实际机器路径。"""
    context = app.state.runtime.context(identity)
    return {key: context.get(key) for key in ('context_id', 'sources')} | {'target': {key: context.get('scope', {}).get(key) for key in ('project_id', 'task_id', 'writable')}}


@app.get('/api/phys/capabilities')
def capabilities():
    """明确区分渲染模式和平台受支持范围。"""
    import sys
    return {'renderers': ['local', 'remote'], 'views': [1,2,3,4], 'filters': ['clip','slice','glyph','streamline','isosurface','contour'], 'exports': ['png','csv','png_sequence','mp4','webm'], 'shadows': sys.platform == 'linux', 'linked_cameras_default': False}


from fastapi.staticfiles import StaticFiles
frontend_dist = REPOSITORY_ROOT/'frontend'/'dist'
if frontend_dist.is_dir():
    app.mount('/workspace', StaticFiles(directory=frontend_dist, html=True), name='vis-workspace')
else:
    @app.get('/workspace/{path:path}')
    def frontend_missing(path: str):
        """纯 Python 安装缺前端时给出明确诊断。"""
        raise HTTPException(503, 'frontend_bundle_missing: build frontend before publishing workbench wheel')


if __name__ == "__main__":
    main()


@app.post('/internal/phys/sessions/{identity}/sources')
def append_trusted_sources(identity: str, request: Request, body: dict):
    """只允许可信宿主把已校验来源交给现有会话。"""
    if not hmac.compare_digest(request.headers.get('x-vis-control', ''), app.state.runtime.control_token):
        raise HTTPException(403, 'trusted_host_required')
    from modules.visPhysField import append_sources
    runtime = app.state.runtime
    binding_context = runtime.context(body['binding_context_id'])
    return append_sources(runtime, identity, body['context_id'], binding_context)
