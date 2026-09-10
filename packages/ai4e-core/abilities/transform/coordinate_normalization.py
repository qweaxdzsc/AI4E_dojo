"""共享边界坐标缩放：正反变换与显式范围门禁。"""

from dataclasses import dataclass

import torch


@dataclass(frozen=True)
class CoordinateNormalization:
    """将共享物理边界映射到非居中的零至 scale 区间。"""

    minimum: tuple[float, ...]
    maximum: tuple[float, ...]
    scale: float = 1000.0
    check_range: bool = True
    tolerance: float = 1e-6
    arithmetic: str = "shift_scale"

    def __post_init__(self):
        """检查边界有限、跨度为正，允许一个共享边界或逐坐标边界。"""
        if self.arithmetic not in {"divide", "shift_scale"}:
            raise ValueError("未知坐标运算约定")
        lo, hi = torch.tensor(self.minimum), torch.tensor(self.maximum)
        if (
            not self.minimum
            or lo.shape != hi.shape
            or not torch.isfinite(lo).all()
            or not torch.isfinite(hi).all()
            or not (hi > lo).all()
            or not torch.isfinite(torch.tensor([self.scale, self.tolerance])).all()
            or self.scale <= 0
            or self.tolerance < 0
        ):
            raise ValueError("坐标边界必须有限且跨度为正")

    def _parameters(self, value):
        if value.ndim < 2 or len(self.minimum) not in (1, value.shape[-1]):
            raise ValueError("坐标维度与边界不一致")
        return value.new_tensor(self.minimum), value.new_tensor(self.maximum)

    def apply(self, value: torch.Tensor, *, check_range: bool | None = None) -> torch.Tensor:
        """缩放坐标；范围检查不截断数值，可按调用关掉门禁。"""
        lo, hi = self._parameters(value)
        result = (
            (value - lo) * (self.scale / (hi - lo))
            if self.arithmetic == "shift_scale"
            else (value - lo) / (hi - lo) * self.scale
        )
        if not torch.isfinite(result).all():
            raise ValueError("坐标包含非有限值")
        enabled = self.check_range if check_range is None else check_range
        if enabled and (
            (result < -self.tolerance).any() or (result > self.scale + self.tolerance).any()
        ):
            raise ValueError("坐标超出归一化边界")
        return result

    def inverse(self, value: torch.Tensor) -> torch.Tensor:
        """恢复原物理坐标。"""
        lo, hi = self._parameters(value)
        return (
            value * (1.0 / (self.scale / (hi - lo))) + lo
            if self.arithmetic == "shift_scale"
            else value / self.scale * (hi - lo) + lo
        )
