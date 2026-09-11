"""复用真实版本树。"""

import ai4e_task as task
from fastapi import APIRouter, Request

from ...bootstrap.dependencies import services

router = APIRouter()


@router.get("/projects/{project}/lineage")
def lineage(project: str, request: Request):
    """协调此范围内的公开用例。"""
    return task.get_lineage(services(request).project(project))


@router.get("/projects/{project}/lineage/{identity}")
def detail(project: str, identity: str, request: Request):
    """读取已校验创建快照与明确运行身份的分阶段详情。"""
    return task.read_version_details(services(request).project(project), identity)
