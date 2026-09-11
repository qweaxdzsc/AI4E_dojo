"""FastAPI 本机应用，使用公开 task 能力与独立预览进程。"""

from contextlib import asynccontextmanager
from importlib import import_module

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from ..infrastructure.transport import FiniteJSONResponse
from .dependencies import Services


def create_app(settings):
    """装配可测试的本机应用。"""

    @asynccontextmanager
    async def lifespan(app):
        yield
        from ..modules.visualization.application import shutdown_operations

        shutdown_operations(app.state.services)

    app = FastAPI(
        lifespan=lifespan, title="Dojo", version="0.1.0", default_response_class=FiniteJSONResponse
    )
    app.state.services = Services(settings)

    @app.exception_handler(ValueError)
    async def value_error(request: Request, exc: ValueError):
        return JSONResponse(
            {"detail": str(exc)}, status_code=409 if "conflict" in str(exc) else 400
        )

    @app.exception_handler(KeyError)
    async def missing(request: Request, exc: KeyError):
        return JSONResponse({"detail": "not_found: " + str(exc)}, status_code=404)

    @app.exception_handler(FileNotFoundError)
    async def file_missing(request: Request, exc: FileNotFoundError):
        return JSONResponse({"detail": "文件不存在或数据根未配置"}, status_code=404)

    @app.exception_handler(RuntimeError)
    async def runtime_error(request: Request, exc: RuntimeError):
        return JSONResponse({"detail": str(exc)}, status_code=409)

    from subprocess import TimeoutExpired

    @app.exception_handler(TimeoutExpired)
    async def preview_timeout(request: Request, exc: TimeoutExpired):
        return JSONResponse({"detail": "预览读取超时，请选择更小的文件"}, status_code=504)

    for name in [
        "projects",
        "tasks",
        "rawprep",
        "assets",
        "previews",
        "executions",
        "capabilities",
        "lineage",
        "comparisons",
        "reports",
        "visualization",
        "stages",
    ]:
        app.include_router(
            import_module("ai4e_server.modules." + name + ".api").router, prefix="/api/v1"
        )

    @app.get("/api/v1/health")
    def health():
        return {"status": "ok"}

    if settings.web_dist:
        from fastapi.responses import FileResponse

        root = settings.web_dist.resolve()

        @app.get("/{path:path}", include_in_schema=False)
        def frontend(path: str):
            if path.startswith("api/"):
                return JSONResponse({"detail": "not_found"}, status_code=404)
            candidate = (root / path).resolve()
            if not candidate.is_relative_to(root):
                raise ValueError("invalid_web_path")
            return FileResponse(candidate if candidate.is_file() else root / "index.html")

    return app
