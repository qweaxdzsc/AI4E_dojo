"""均值标准差变换：参数校验与可微正反变换。"""

from dataclasses import dataclass

import torch


@dataclass(frozen=True)
class Standardization:
    """按最后一个通道维应用冻结的均值与标准差。"""

    mean: tuple[float, ...]
    std: tuple[float, ...]
    arithmetic: str = "shift_scale"

    def __post_init__(self):
        """拒绝非有限统计、空参数及非正标准差。"""
        if self.arithmetic not in {"divide", "shift_scale"}:
            raise ValueError("未知归一化运算约定")
        if (
            not self.mean
            or len(self.mean) != len(self.std)
            or not torch.isfinite(torch.tensor([*self.mean, *self.std])).all()
            or min(self.std) <= 0
        ):
            raise ValueError("均值和标准差必须有限、维度一致且标准差为正")

    def _parameters(self, value: torch.Tensor):
        if value.ndim < 2 or value.shape[-1] != len(self.mean):
            raise ValueError("字段通道数与统计参数不一致")
        return value.new_tensor(self.mean), value.new_tensor(self.std)

    def apply(self, value: torch.Tensor) -> torch.Tensor:
        """将物理值转换至标准化空间，保留梯度。"""
        mean, std = self._parameters(value)
        if self.arithmetic == "divide":
            return (value - mean) / std
        return (value - mean) * torch.reciprocal(std.clamp(min=1e-6))

    def inverse(self, value: torch.Tensor) -> torch.Tensor:
        """仅依靠冻结参数恢复物理值。"""
        mean, std = self._parameters(value)
        if self.arithmetic == "divide":
            return value * std + mean
        return value * (1.0 / torch.reciprocal(std.clamp(min=1e-6))) + mean
