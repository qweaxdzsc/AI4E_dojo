"""附加放大：归一化之后的可见系数，正反变换共用。"""

from __future__ import annotations

import math
from dataclasses import dataclass

import torch


def resolve_scale(declaration: dict | None) -> float:
    """读取场上 scale，缺省为 1；非正或非有限拒绝。"""
    raw = 1 if declaration is None else declaration.get("scale", 1)
    if raw is None:
        raw = 1
    try:
        factor = float(raw)
    except (TypeError, ValueError) as exc:
        raise ValueError("scale 必须为正有限数") from exc
    if not math.isfinite(factor) or factor <= 0:
        raise ValueError("scale 必须为正有限数")
    return factor


@dataclass(frozen=True)
class Scale:
    """把已归一化的场乘以正系数，反变换除回。"""

    factor: float = 1.0

    def __post_init__(self):
        if not math.isfinite(self.factor) or self.factor <= 0:
            raise ValueError("scale 必须为正有限数")

    def apply(self, value: torch.Tensor) -> torch.Tensor:
        """正向放大。"""
        return value * self.factor

    def inverse(self, value: torch.Tensor) -> torch.Tensor:
        """恢复归一化后、放大前的值。"""
        return value / self.factor
