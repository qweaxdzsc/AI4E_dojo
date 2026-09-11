"""项目 HTTP 接口。"""

import ai4e_task as task
from fastapi import APIRouter, Request
from pydantic import BaseModel, ConfigDict

from ...bootstrap.dependencies import services
from .application import create, listing

router = APIRouter(prefix="/projects")


class ProjectEdit(BaseModel):
    """项目管理编辑请求。"""

    model_config = ConfigDict(extra="forbid")
    name: str | None = None
    description: str | None = None
    archived: bool | None = None


@router.get("")
def list_projects(request: Request):
    """查询已登记项目的当前管理记录。"""
    return listing(services(request))


@router.post("")
def create_project(body: ProjectEdit, request: Request):
    """创建本机项目并登记其位置。"""
    value = create(services(request), body.name or "")
    if body.description:
        value = task.update_project(
            services(request).project(value["id"]), description=body.description
        )
    return value


@router.patch("/{project}")
def update_project(project: str, body: ProjectEdit, request: Request):
    """更新项目属性或归档状态。"""
    return task.update_project(
        services(request).project(project), **body.model_dump(exclude_none=True)
    )
