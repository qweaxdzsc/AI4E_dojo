"""流式均值方差归一化，供训练数据逐批累计。"""

from __future__ import annotations

import torch
from torch import nn


class RunningNormalizer(nn.Module):
    """按最后一维累计有限样本，并支持可恢复正反变换。"""

    def __init__(self, size: int, *, epsilon: float = 1e-8, max_accumulations: int = 1_000_000):
        super().__init__()
        if size <= 0 or epsilon <= 0 or max_accumulations <= 0:
            raise ValueError("归一化维度、epsilon 和累计上限必须为正")
        self.size = size
        self.epsilon = epsilon
        self.max_accumulations = max_accumulations
        self.register_buffer("count", torch.zeros((), dtype=torch.float64))
        self.register_buffer("sum", torch.zeros(size, dtype=torch.float64))
        self.register_buffer("sum_squared", torch.zeros(size, dtype=torch.float64))
        self.register_buffer("accumulations", torch.zeros((), dtype=torch.long))

    def accumulate(self, value: torch.Tensor) -> None:
        """累计一批样本；达到上限后保持冻结统计。"""
        if value.ndim < 1 or value.shape[-1] != self.size:
            raise ValueError("累计值最后一维与归一化维度不一致")
        if not torch.isfinite(value).all():
            raise ValueError("累计值包含非有限数")
        if int(self.accumulations) >= self.max_accumulations:
            return
        flat = value.detach().reshape(-1, self.size).to(torch.float64)
        self.count.add_(flat.shape[0])
        self.sum.add_(flat.sum(dim=0))
        self.sum_squared.add_(flat.square().sum(dim=0))
        self.accumulations.add_(1)

    def statistics(self, value: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        """返回匹配输入设备和精度的均值与标准差。"""
        if int(self.count) == 0:
            return value.new_zeros(self.size), value.new_full((self.size,), self.epsilon)
        mean = self.sum / self.count
        variance = (self.sum_squared / self.count - mean.square()).clamp_min(0)
        return mean.to(value), variance.sqrt().clamp_min(self.epsilon).to(value)

    def forward(self, value: torch.Tensor, *, accumulate: bool = False) -> torch.Tensor:
        """按当前统计归一化，并可先累计本批输入。"""
        if accumulate:
            self.accumulate(value)
        mean, std = self.statistics(value)
        return (value - mean) / std

    def inverse(self, value: torch.Tensor) -> torch.Tensor:
        """使用当前统计把归一化值还原到原空间。"""
        mean, std = self.statistics(value)
        return value * std + mean
