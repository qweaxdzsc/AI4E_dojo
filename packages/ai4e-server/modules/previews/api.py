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
    root: str | None = None,
    path: str | None = None,
    task_id: str | None = None,
    asset_id: str | None = None,
    revision: str | None = None,
    operation: str = "inspect",
    field: str | None = None,
    offset: int = 0,
):
    """读取受控文件的真实检查或预览内容；阶段产物可用已登记资产定位。"""
    if operation not in {"inspect", "preview"}:
        raise ValueError("invalid_operation")
    s = services(request)
    if asset_id:
        from ..visualization.application import asset

        target = asset(
            s, project, {"project_id": project, "asset_id": asset_id, "revision": revision}
        )
    elif root is not None and path is not None:
        target = resolve(s, project, root, path, task_id)
    else:
        raise ValueError("controlled_preview_source_required")
    return inspect_preview(s, target, operation, {"field": field, "offset": offset})
