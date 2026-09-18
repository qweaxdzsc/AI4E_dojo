"""配置接口仅允许原始处理配置段。"""

import ai4e_task as task
from fastapi import APIRouter, Request
from pydantic import BaseModel, ConfigDict, Field

from ...bootstrap.dependencies import services
from .application import preflight, submit

router = APIRouter(prefix="/projects/{project}/tasks/{identity}/rawprep")


class ConfigEdit(BaseModel):
    """配置修订和原始处理编辑请求。"""

    model_config = ConfigDict(extra="forbid")
    revision: str
    rawprep: dict
    edited_paths: list[list[str]] | None = None
    removed_paths: list[list[str]] | None = None
    processed_name: str | None = None
    profile: dict | None = None


class Selection(BaseModel):
    """完整输入选择与幂等提交身份。"""

    model_config = ConfigDict(extra="forbid")
    revision: str
    root: str = ""
    files: list[str] = Field(default_factory=list)
    all_selected: bool = True
    count: int | None = None
    samples: list[str] | None = None
    idempotency_key: str | None = None
    sample_scope: dict | None = None
    catalog_revision: str | None = None
    overwrite_processed_name: bool = False


def _with_name_status(service, project: str, identity: str, value: dict) -> dict:
    """读取/保存后附带名称状态，与正式执行预检使用同一份声明。"""
    from ..datasets.application import claim_config, describe_name

    cfg = task.read_configuration(service.project(project), identity)
    value["processed_name_status"] = describe_name(
        service,
        value.get("processed_name") or "",
        claim_config(cfg["config"], value.get("rawprep") or {}),
        project=project,
    )
    return value


@router.get("")
def read(project: str, identity: str, request: Request):
    """读取持久化的当前内容。"""
    service = services(request)
    return _with_name_status(
        service,
        project,
        identity,
        task.describe_rawprep(service.project(project), identity),
    )


@router.put("")
def save(project: str, identity: str, body: ConfigEdit, request: Request):
    """校验并保存当前编辑内容。"""
    from .application import save_configuration

    save_configuration(services(request), project, identity, body)
    base = services(request).project(project)
    return _with_name_status(
        services(request), project, identity, task.describe_rawprep(base, identity)
    )


@router.post("/preflight")
def check(project: str, identity: str, body: Selection, request: Request):
    """校验配置与完整输入样本，不写处理产物。"""
    value = preflight(services(request), project, identity, body)
    value.pop("root")
    return value


@router.post("/execute")
def execute(project: str, identity: str, body: Selection, request: Request):
    """提交既有案例的原始数据处理。"""
    return submit(services(request), project, identity, body)


@router.post("/catalog")
def catalog(project: str, identity: str, body: Selection, request: Request):
    """通过数据集公开描述读取真实样本、字段和依赖。"""
    from .application import dataset_catalog

    return dataset_catalog(services(request), project, identity, body, public=True)


@router.post("/trial")
def trial(project: str, identity: str, body: Selection, request: Request):
    """按明确选择试跑，产物不成为默认正式输入。"""
    return submit(services(request), project, identity, body, mode="trial")
