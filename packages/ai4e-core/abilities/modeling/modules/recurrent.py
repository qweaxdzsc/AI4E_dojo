"""单层循环特征计算：复用 PyTorch RNN，状态显式交接且不跨样本缓存。"""

import torch
from torch import nn


class RecurrentBlock(nn.Module):
    """单向 Elman 循环块，支持 tanh 或 relu，零缺省初始状态。

    直接使用原生单层 RNN 的双偏置和数值语义，不复制循环单元公式。
    ``in_features`` 为输入末轴宽度，``hidden_size`` 为循环特征宽度。
    """

    def __init__(self, in_features: int, hidden_size: int, nonlinearity: str = "tanh") -> None:
        super().__init__()
        if any(type(width) is not int or width <= 0 for width in (in_features, hidden_size)):
            raise ValueError("输入和隐藏宽度须为正整数")
        if nonlinearity not in {"tanh", "relu"}:
            raise ValueError("循环激活仅支持 tanh 或 relu")
        self.in_features = in_features
        self.hidden_size = hidden_size
        self.recurrent = nn.RNN(
            in_features, hidden_size, num_layers=1, nonlinearity=nonlinearity, batch_first=True
        )

    def forward(
        self, x: torch.Tensor, state: torch.Tensor | None = None
    ) -> tuple[torch.Tensor, torch.Tensor]:
        """输入 ``[B,T,C]`` 及可选 ``[1,B,H]``，返回序列与末状态。

        空时间轴、错误形状、状态设备或精度不一致均抛出 ValueError。
        不自动搬移状态、不分离其梯度；截断反向传播由调用方显式决定。
        """
        if x.ndim != 3 or x.shape[-1] != self.in_features or x.shape[1] == 0:
            raise ValueError(f"循环输入须为非空时间 [B,T,{self.in_features}]")
        if state is not None:
            if state.shape != (1, x.shape[0], self.hidden_size):
                raise ValueError("单层循环状态须为 [1,B,H]")
            if state.device != x.device or state.dtype != x.dtype:
                raise ValueError("循环状态须与输入处于相同设备和精度")
        return self.recurrent(x, state)
