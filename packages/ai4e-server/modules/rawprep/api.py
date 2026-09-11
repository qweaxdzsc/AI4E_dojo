"""配置接口仅允许原始处理配置段。"""

import ai4e_task as task
from fastapi import APIRouter, Request
from pydantic import BaseModel, ConfigDict

from ...bootstrap.dependencies import services
from ..capabilities.aero_cfd import require_profile
from .application import preflight, submit
from .recipe_mapping import patch

router = APIRouter(prefix="/projects/{project}/tasks/{identity}/rawprep")


class ConfigEdit(BaseModel):
    """配置修订和原始处理编辑请求。"""

    model_config = ConfigDict(extra="forbid")
    revision: str
    rawprep: dict


class Selection(BaseModel):
    """完整输入选择与幂等提交身份。"""

    model_config = ConfigDict(extra="forbid")
    revision: str
    root: str
    files: list[str]
    all_selected: bool = True
    count: int | None = None
    samples: list[str] | None = None
    idempotency_key: str | None = None


@router.get("")
def read(project: str, identity: str, request: Request):
    """读取持久化的当前内容。"""
    value = task.read_configuration(services(request).project(project), identity)
    return {"revision": value["revision"], "rawprep": value["config"]["rawprep"]}


@router.put("")
def save(project: str, identity: str, body: ConfigEdit, request: Request):
    """校验并保存当前编辑内容。"""
    require_profile(services(request), project, identity)
    base = services(request).project(project)
    current = task.read_configuration(base, identity)
    if current["config"].get("components", {}).get("dataset", "").endswith("nasa_crm"):
        if set(body.rawprep) - {
            "format",
            "extraction",
            "vtkhdf",
            "overwrite",
            "sources",
            "fields",
            "geometry",
            "filters",
            "statistics",
        }:
            raise ValueError("rawprep.unsupported_keys")
        if body.rawprep.get("format", "pt") not in {"pt", "zarr"}:
            raise ValueError("rawprep.format")
        payload = {"rawprep": body.rawprep}
    else:
        payload = patch(body.rawprep)
    value = task.save_configuration(base, identity, payload, revision=body.revision)
    return {"revision": value["revision"], "rawprep": value["config"]["rawprep"]}


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
