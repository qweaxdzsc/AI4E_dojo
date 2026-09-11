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
        project, identity, body.stage, body.values, body.expected_revision, services(request)
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
