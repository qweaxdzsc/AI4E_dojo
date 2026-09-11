"""线程中的请求协调，数值文件读取发生在独立进程。"""

from fastapi import APIRouter, Request

from ...bootstrap.dependencies import services
from ...infrastructure.content_access import resolve
from .worker_adapter import inspect_preview

router = APIRouter(prefix="/projects/{project}/preview")


@router.get("")
def preview(
    project: str,
    request: Request,
    root: str,
    path: str,
    task_id: str | None = None,
    operation: str = "inspect",
    field: str | None = None,
    offset: int = 0,
):
    """读取受控文件的真实检查或预览内容。"""
    if operation not in {"inspect", "preview"}:
        raise ValueError("invalid_operation")
    s = services(request)
    return inspect_preview(
        s, resolve(s, project, root, path, task_id), operation, {"field": field, "offset": offset}
    )
