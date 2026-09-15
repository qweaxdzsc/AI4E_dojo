"""文件列表和下载仅通过受控根访问。"""

from fastapi import APIRouter, Request
from fastapi.responses import FileResponse

from ...bootstrap.dependencies import services
from ...infrastructure.content_access import listing, resolve, roots

router = APIRouter(prefix="/projects/{project}/files")


@router.get("/roots")
def root_list(project: str, request: Request, task_id: str | None = None):
    """查询已登记的文件范围身份。"""
    return [
        {"id": k, "label": p.name} for k, p in roots(services(request), project, task_id).items()
    ]


@router.get("")
def files(
    project: str,
    request: Request,
    root: str = "project",
    path: str = "",
    task_id: str | None = None,
    query: str = "",
):
    """查询受控目录下的实际文件；空关键字只列一层。"""
    return listing(services(request), project, root, path, task_id, query)


@router.get("/download")
def download(project: str, request: Request, root: str, path: str, task_id: str | None = None):
    """返回受控范围内的真实文件内容。"""
    file = resolve(services(request), project, root, path, task_id)
    if not file.is_file():
        raise ValueError("file_required")
    return FileResponse(file, filename=file.name)
