"""物理预测和比较的轻量产物约定；数组存储与渲染实现保持独立。"""

from typing import Any, TypedDict


class PhysicalDomain(TypedDict):
    """域中的数组逻辑名与身份基础，拓扑引用可为空。"""

    position: str
    ids: str
    targets: dict[str, str]
    identity_basis: str
    topology: Any


class PhysicalPrediction(TypedDict):
    """完整样本物理预测清单，protocol 绑定模型、准备与检查点。"""

    identity: dict[str, Any]
    protocol: str
    domains: dict[str, PhysicalDomain]
    metrics: dict[str, Any]
    filemap: dict[str, str]


class ComparisonVisual(TypedDict, total=False):
    """core 已计算的图形引用；viz 只按该几何和显示声明表达。"""

    sample: str
    kind: str
    path: str
    fields: list[str]
    axis: int
    fraction: float
    span_fraction: float | None
    origin: list[float]
    normal: list[float]
    view_up: list[float]
    interpolation: str
    invalid_region: str
