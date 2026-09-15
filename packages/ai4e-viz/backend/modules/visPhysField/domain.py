"""三维物理场一级共享领域对象和不变量。"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class FieldCommand:
    """提交给一级应用层的物理场操作，不携带Trame运行时对象。"""

    action: str
    payload: dict[str, Any] = field(default_factory=dict)


def normalize_range(minimum: float, maximum: float) -> tuple[float, float]:
    """规范颜色或提取范围，禁止上下界倒置。"""

    lower, upper = float(minimum), float(maximum)
    if lower > upper:
        raise ValueError("范围下界不能大于上界")
    return lower, upper
