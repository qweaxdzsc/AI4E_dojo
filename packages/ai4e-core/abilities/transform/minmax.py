"""通用 Min-Max 冻结变换；坐标兼容入口复用相同算术。"""

from dataclasses import dataclass

import torch


@dataclass(frozen=True)
class MinMax:
    """映射到零至 scale；常量分量映射到零，反变换恢复常量。"""

    minimum: tuple[float, ...]
    maximum: tuple[float, ...]
    scale: float = 1.0
    check_range: bool = False
    tolerance: float = 1e-6
    arithmetic: str = "shift_scale"

    def __post_init__(self):
        lo, hi = torch.tensor(self.minimum), torch.tensor(self.maximum)
        if (
            not self.minimum
            or lo.shape != hi.shape
            or not torch.isfinite(lo).all()
            or not torch.isfinite(hi).all()
            or (hi < lo).any()
            or self.scale <= 0
            or not torch.isfinite(torch.tensor([self.scale, self.tolerance])).all()
            or self.tolerance < 0
            or self.arithmetic not in {"divide", "shift_scale"}
        ):
            raise ValueError("Min-Max 边界、尺度或算术声明非法")

    def _parameters(self, value):
        if value.ndim < 2 or len(self.minimum) not in (1, value.shape[-1]):
            raise ValueError("字段维度与 Min-Max 边界不一致")
        return value.new_tensor(self.minimum), value.new_tensor(self.maximum)

    def apply(self, value, *, check_range=None):
        """使用冻结边界缩放，范围检查不截断物理值。"""
        lo, hi = self._parameters(value)
        span = torch.where(hi == lo, torch.ones_like(hi), hi - lo)
        result = (
            (value - lo) * (self.scale / span)
            if self.arithmetic == "shift_scale"
            else (value - lo) / span * self.scale
        )
        enabled = self.check_range if check_range is None else check_range
        if not torch.isfinite(result).all():
            raise ValueError("字段包含非有限值")
        if enabled and (
            (result < -self.tolerance).any() or (result > self.scale + self.tolerance).any()
        ):
            raise ValueError("字段超出归一化边界")
        return result

    def inverse(self, value):
        """恢复物理值及常量分量。"""
        lo, hi = self._parameters(value)
        span = torch.where(hi == lo, torch.ones_like(hi), hi - lo)
        result = (
            value * (1.0 / (self.scale / span)) + lo
            if self.arithmetic == "shift_scale"
            else value / self.scale * span + lo
        )
        return torch.where(hi == lo, lo, result)
