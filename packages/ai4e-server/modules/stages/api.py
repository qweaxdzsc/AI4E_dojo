"""阶段 HTTP 适配：验证传输形状，业务规则与提交编排由用例负责。"""

from fastapi import APIRouter, Request
from pydantic import BaseModel, ConfigDict

from ...bootstrap.dependencies import services
from . import application
from .domain import OperationCommand

router = APIRouter(prefix="/projects/{project}/tasks/{identity}")


class ConfigurationEdit(BaseModel):
    """当前配置修订和阶段修改。"""

    model_config = ConfigDict(extra="forbid")
    expected_revision: str
    values: dict
    stage: str
    bindings: dict[str, dict | None] = {}
    target_case_id: str | None = None
    target_model: str | None = None
    target_variant: str | None = None
    target_preset: str | None = None


class StageOperation(BaseModel):
    """固定配置和输入身份的阶段请求。"""

    model_config = ConfigDict(extra="forbid")
    expected_revision: str
    mode: str
    inputs: list[dict] = []
    selection: dict = {}
    idempotency_key: str | None = None


@router.get("/configuration")
def configuration(project: str, identity: str, request: Request, stage: str | None = None):
    """读取任务阶段配置。"""
    return application.configuration(project, identity, services(request), stage)


@router.put("/configuration")
def save(project: str, identity: str, body: ConfigurationEdit, request: Request):
    """传递带修订的配置保存命令。"""
    return application.save(
        project,
        identity,
        body.stage,
        body.values,
        body.expected_revision,
        services(request),
        body.bindings,
        body.target_case_id,
        body.target_model,
        body.target_variant,
        body.target_preset,
    )


class ModelPresetCreate(BaseModel):
    """导出当前已保存模型配置。"""

    model_config = ConfigDict(extra="forbid")
    expected_revision: str
    name: str


@router.get("/model-options")
def model_options(project: str, identity: str, request: Request):
    """读取官方模型与同数据集用户预设。"""
    from ..capabilities import model_options as describe

    return describe(services(request), project, identity)


@router.post("/model-presets")
def create_model_preset(project: str, identity: str, body: ModelPresetCreate, request: Request):
    """导出当前模型配置为项目共享预设。"""
    from ..capabilities.model_presets import export_preset

    return export_preset(
        services(request), project, identity, body.name, body.expected_revision
    )


@router.get("/capabilities")
def capabilities(project: str, identity: str, request: Request):
    """读取真实案例能力。"""
    return application.capabilities(project, identity, services(request))


@router.post("/model-inspections")
def model_inspection(project: str, identity: str, body: StageOperation, request: Request):
    """提交模型检查命令。"""
    return application.model_inspection(
        project, identity, OperationCommand(**body.model_dump()), services(request)
    )


@router.post("/stages/{stage}/operations")
def operation(project: str, identity: str, stage: str, body: StageOperation, request: Request):
    """提交阶段操作命令。"""
    return application.operation(
        project, identity, stage, OperationCommand(**body.model_dump()), services(request)
    )


@router.get("/stage-inputs")
def stage_inputs(project: str, identity: str, request: Request):
    """读取正式交接产物。"""
    return application.stage_inputs(project, identity, services(request))


@router.get("/stage-summary")
def stage_summary(project: str, identity: str, request: Request):
    """读取研究进度和当前配置对应的检查状态。"""
    return application.stage_summary(project, identity, services(request))


@router.get("/stage-files")
def stage_files(
    project: str,
    identity: str,
    request: Request,
    role: str,
    run_id: str | None = None,
    asset_id: str | None = None,
    revision: str | None = None,
    path: str = "",
    query: str = "",
):
    """读取明确运行或当前草稿选定清单的当前层阶段文件，未选择时返回空列表。"""
    return application.stage_files(
        project, identity, services(request), role, run_id, asset_id, revision, path, query
    )
