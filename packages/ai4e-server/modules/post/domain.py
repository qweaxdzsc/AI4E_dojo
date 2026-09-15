"""后处理协议模型；不包含数组、内部路径及算法对象。"""

from pydantic import BaseModel, ConfigDict, Field


class ResultRef(BaseModel):
    """固定结果身份与内容修订。"""

    model_config = ConfigDict(extra="forbid")
    id: str
    revision: str


class MetricRequest(BaseModel):
    """评价只接受已登记结果和目录中的指标字段。"""

    model_config = ConfigDict(extra="forbid")
    results: list[ResultRef] = Field(min_length=1)
    fields: list[str] = Field(min_length=1)
    metrics: list[str] = Field(min_length=1)
    idempotency_key: str = Field(min_length=1)


class ExportRequest(BaseModel):
    """导出不接受文件路径。"""

    model_config = ConfigDict(extra="forbid")
    format: str = "csv"
    row_ids: list[str] | None = None
