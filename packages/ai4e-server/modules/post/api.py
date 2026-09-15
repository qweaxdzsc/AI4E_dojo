"""后处理HTTP适配；业务和计算分别由application及core承接。"""

from fastapi import APIRouter, Query, Request

from ...bootstrap.dependencies import services
from . import application
from .domain import ExportRequest, MetricRequest

router = APIRouter(prefix="/projects/{project}/tasks/{identity}/post")


@router.get("/results")
def results(
    project: str,
    identity: str,
    request: Request,
    offset: int = Query(0, ge=0),
    limit: int = Query(500, ge=1, le=1000),
    batch: str | None = None,
    query: str = "",
    directory: str | None = None,
    view: str = "catalog",
    run_id: str | None = None,
    sample: str | None = None,
    split: str | None = None,
    status: str | None = None,
):
    """查询评价目录或按层结果文件。"""
    return application.results(
        services(request),
        project,
        identity,
        offset=offset,
        limit=limit,
        batch=batch,
        query=query,
        directory=directory,
        view=view,
        run_id=run_id,
        sample=sample,
        split=split,
        status=status,
    )


@router.get("/metrics/catalog")
def catalog(project: str, identity: str, request: Request):
    """查询指标目录。"""
    return application.catalog(services(request), project, identity)


@router.post("/metric-jobs")
def submit(project: str, identity: str, body: MetricRequest, request: Request):
    """提交后台评价。"""
    return application.submit(services(request), project, identity, body.model_dump())


@router.get("/metric-jobs")
def jobs(project: str, identity: str, request: Request):
    """查询评价历史。"""
    return application.jobs(services(request), project, identity)


@router.get("/metric-jobs/{job}")
def read(
    project: str,
    identity: str,
    job: str,
    request: Request,
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """查询进度与结果行。"""
    return application.read(services(request), project, identity, job, offset, limit)


@router.post("/metric-jobs/{job}/cancel")
def cancel(project: str, identity: str, job: str, request: Request):
    """请求取消。"""
    return application.cancel(services(request), project, identity, job)


@router.post("/metric-jobs/{job}/exports")
def export(project: str, identity: str, job: str, body: ExportRequest, request: Request):
    """显式导出CSV或JSON。"""
    return application.export(services(request), project, identity, job, body.model_dump())
