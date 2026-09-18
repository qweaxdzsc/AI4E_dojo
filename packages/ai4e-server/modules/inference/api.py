"""推理 HTTP 协议适配；请求形状由 spec 校验，用例承接业务。"""

from fastapi import APIRouter, Request
from pydantic import BaseModel, ConfigDict

from ...bootstrap.dependencies import services
from . import application

router = APIRouter(prefix="/projects/{project}/tasks/{identity}/inference")


class CheckpointSelectionRequest(BaseModel):
    """固定检查点内容修订。"""

    model_config = ConfigDict(extra="forbid")
    id: str
    revision: str


class SampleSelectionRequest(BaseModel):
    """跨分片样本身份。"""

    model_config = ConfigDict(extra="forbid")
    split: str
    sample: str


class InferenceOptionsRequest(BaseModel):
    """独立推理参数，不修改训练配置。"""

    model_config = ConfigDict(extra="forbid")
    evaluate: bool = True
    save_predictions: bool = True
    export_vtk: bool = True
    export_pointcloud: bool | None = None
    export_mesh: bool | None = None
    query_chunk_size: int = 16384


class InferenceBatchRequest(BaseModel):
    """新旧样本协议互斥，业务校验交由 spec。"""

    model_config = ConfigDict(extra="forbid")
    expected_revision: str
    checkpoints: list[CheckpointSelectionRequest]
    name: str = "批量推理"
    samples: list[str] | None = None
    split: str | None = None
    sample_selection: list[SampleSelectionRequest] | None = None
    fields: list[str] | None = None
    metrics: list[str] | None = None
    device: str = "auto"
    options: InferenceOptionsRequest | None = None
    idempotency_key: str | None = None


class InferenceExportRequest(BaseModel):
    """固定结果导出选择。"""

    model_config = ConfigDict(extra="forbid")
    format: str
    selection: dict | None = None


class RetryRequest(BaseModel):
    """重试请求身份。"""

    model_config = ConfigDict(extra="forbid")
    idempotency_key: str | None = None


@router.get("/checkpoints")
def checkpoints(project: str, identity: str, request: Request):
    """读取可选检查点。"""
    return application.checkpoints(services(request), project, identity)


@router.get("/samples")
def samples(project: str, identity: str, checkpoint_id: str, request: Request):
    """读取准备分片。"""
    return application.samples(services(request), project, identity, checkpoint_id)


@router.post("/check")
def check(project: str, identity: str, body: InferenceBatchRequest, request: Request):
    """预检批次。"""
    return application.check(
        services(request), project, identity, body.model_dump(exclude_unset=True)
    )


@router.post("/batches")
def submit(project: str, identity: str, body: InferenceBatchRequest, request: Request):
    """提交批次。"""
    return application.submit(
        services(request), project, identity, body.model_dump(exclude_unset=True)
    )


@router.get("/batches")
def batches(project: str, identity: str, request: Request):
    """列出批次。"""
    return application.batches(services(request), project, identity)


@router.get("/batches/{batch_id}")
def get_batch(project: str, identity: str, batch_id: str, request: Request):
    """读取批次。"""
    return application.get_batch(services(request), project, identity, batch_id)


@router.get("/batches/{batch_id}/results")
def results(project: str, identity: str, batch_id: str, request: Request):
    """读取已提交结果。"""
    return application.results(services(request), project, identity, batch_id)


@router.post("/batches/{batch_id}/exports")
def export(
    project: str, identity: str, batch_id: str, body: InferenceExportRequest, request: Request
):
    """从已保存指标导出 CSV 或 XLSX。"""
    return application.export(
        services(request), project, identity, batch_id, body.model_dump(exclude_unset=True)
    )


@router.post("/batches/{batch_id}/{operation}")
def action(
    project: str, identity: str, batch_id: str, operation: str, body: RetryRequest, request: Request
):
    """取消、恢复和重试协议。"""
    return application.action(
        services(request), project, identity, batch_id, operation, body.idempotency_key
    )
