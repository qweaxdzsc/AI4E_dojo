"""平台公共传输契约：固定资产、辅助操作与显示资产，不依赖数值库。"""

from typing import Any, Literal, NotRequired, TypedDict


class AssetRef(TypedDict):
    """受控资产及内容修订；浏览器不能指定服务器路径。"""

    project_id: str
    asset_id: str
    revision: str
    task_id: NotRequired[str | None]
    run_id: NotRequired[str | None]
    member: NotRequired[str | None]
    block: NotRequired[str | None]


class FieldDescriptor(TypedDict):
    """字段身份包含归属与成员，未知单位不猜测。"""

    field_id: str
    name: str
    member: str | None
    association: Literal["geometry", "point", "cell", "global", "array", "column"]
    shape: list[int]
    dtype: str
    components: int
    unit: str | None
    entity_set: str | None
    semantic_key: str | None


class DatasetDescriptor(TypedDict):
    """数据组件给出的样本、字段和完整性依赖，不由页面猜测。"""

    dataset_id: str
    revision: str
    samples: list[dict[str, Any]]
    sources: list[dict[str, Any]]
    fields: list[FieldDescriptor]
    dependencies: list[dict[str, Any]]
    capabilities: dict[str, Any]
    profile: NotRequired[dict[str, Any]]
    inspection: NotRequired[dict[str, Any]]
    errors: NotRequired[list[dict[str, Any]]]
    selection: NotRequired[list[str] | dict[str, list[str]]]


class RawprepDescriptor(TypedDict):
    """数据组件的原始处理描述，前端不维护默认值或绑定规则。"""

    schema_version: int
    dataset_id: str
    defaults: dict[str, Any]
    binding: dict[str, Any]
    domains: dict[str, str]
    outputs: list[dict[str, Any]]
    geometry: list[dict[str, Any]]
    filters: list[dict[str, Any]]
    formats: list[str]
    vtkhdf: bool
    statistics_modes: list[str]


class ExtractionMember(TypedDict):
    """一个输出成员独立引用原字段，不暗示拼接。"""

    source_field: str
    output_member: str
    components: NotRequired[int]


class ExtractionOutput(TypedDict):
    """格式在阶段级设置，输出只保存命名与成员。"""

    id: str
    name: str
    members: list[ExtractionMember]


class ExtractionEntry(TypedDict):
    """一条来源选择对应多个输出。"""

    id: str
    name: str
    source_selector: dict[str, Any]
    outputs: list[ExtractionOutput]


class StageConfig(TypedDict):
    """任务配置工作副本及能力，不保存计算统计事实。"""

    task_id: str
    revision: str
    stage: str
    values: dict[str, Any]
    capabilities: dict[str, Any]
    readiness: dict[str, Any]


class StageOperationRequest(TypedDict):
    """固定修订后检查、试跑或正式执行。"""

    expected_revision: str
    mode: Literal["check", "trial", "execute"]
    inputs: list[AssetRef]
    selection: dict[str, Any]
    idempotency_key: str


class OperationError(TypedDict):
    """可定位的业务失败。"""

    code: str
    message: str
    location: NotRequired[str]


class Operation(TypedDict):
    """辅助操作快照，不替代 task 研究运行记录。"""

    operation_id: str
    kind: str
    status: Literal["queued", "running", "succeeded", "failed", "canceled", "interrupted", "stale"]
    phase: str | None
    progress: float | None
    result_refs: list[AssetRef]
    error: OperationError | None
    event_cursor: int
    subscription_id: NotRequired[str]


class VizRequest(TypedDict):
    """服务校验后发送给独立进程；输出目录由服务分配。"""

    protocol_version: Literal[1]
    request_id: str
    operation: Literal["inspect", "read_slice", "summarize", "transform"]
    source: dict[str, Any]
    options: dict[str, Any]
    output_dir: str


class BinaryBuffer(TypedDict):
    """显示清单中的相对文件成员，保留数组类型。"""

    name: str
    path: str
    dtype: str
    shape: list[int]
    byte_order: Literal["little", "big", "not-applicable"]
    byte_length: int
    sha256: str


class CoordinateSpace(TypedDict):
    """源文件显式声明的坐标空间；未知长度单位不能由物理场单位代替。"""

    id: str
    unit: str
    evidence: Literal["source-declaration"]
    source_refs: list[AssetRef]


class DisplayAssetManifest(TypedDict):
    """显示资产与源数据分开，实体映射不能由顶点编号猜测。"""

    schema_version: Literal[1]
    source_refs: list[dict[str, Any]]
    pipeline: list[dict[str, Any]]
    dataset_type: str
    bounds: list[float]
    geometry_buffers: list[BinaryBuffer]
    topology_buffers: list[BinaryBuffer]
    fields: list[dict[str, Any]]
    entity_mapping: dict[str, Any]
    statistics: dict[str, Any]
    provenance: dict[str, Any]
    coordinate_space: NotRequired[CoordinateSpace]


class SceneDocument(TypedDict):
    """可序列化场景，不保存 GPU 对象、下载句柄或数组缓存。"""

    schema_version: Literal[1]
    sources: list[AssetRef]
    pipeline_nodes: list[dict[str, Any]]
    representations: list[dict[str, Any]]
    viewports: list[dict[str, Any]]
    link_groups: list[dict[str, Any]]
    active_view: str | None
    selected_node: str | None
