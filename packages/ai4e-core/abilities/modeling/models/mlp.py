"""完整多层感知机：直接组合共享前馈块，保留普通模块替换位置。"""

import torch
from torch import nn

from ai4e_core.abilities.modeling.modules.feed_forward import FeedForward


class MLP(nn.Module):
    """末轴回归网络；默认三个 64 宽 GELU 隐藏层和线性输出。

    显式 ``feed_forward`` 替代整个特征映射，正常注册其参数、设备与模式。
    注入时隐藏参数不再参与构造，输入输出宽度仍定义本地消费约定。
    """

    def __init__(
        self,
        in_features: int,
        out_features: int,
        hidden_features: tuple[int, ...] = (64, 64, 64),
        activation: str = "gelu",
        feed_forward: nn.Module | None = None,
    ) -> None:
        super().__init__()
        if any(type(width) is not int or width <= 0 for width in (in_features, out_features)):
            raise ValueError("输入和输出宽度须为正整数")
        self.in_features = in_features
        self.out_features = out_features
        self.feed_forward = (
            FeedForward(in_features, out_features, hidden_features, activation)
            if feed_forward is None
            else feed_forward
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """保持前导维度，将 ``[...,Cin]`` 映射为 ``[...,Cout]``。"""
        if x.ndim < 1 or x.shape[-1] != self.in_features:
            raise ValueError(f"MLP 输入末轴须为 {self.in_features}")
        prediction = self.feed_forward(x)
        if prediction.shape != (*x.shape[:-1], self.out_features):
            raise ValueError("替换前馈的输出须保持前导维度及声明的输出宽度")
        return prediction
