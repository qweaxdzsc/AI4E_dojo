"""多层循环网络阶段：组合公开循环块，独立于业务阶段与训练运行器。"""

from collections.abc import Sequence

import torch
from torch import nn

from ai4e_core.abilities.modeling.modules.recurrent import RecurrentBlock


class RecurrentStage(nn.Module):
    """按层顺序组合等隐藏宽度的循环块，状态为 ``[L,B,H]``。

    ``blocks`` 可显式提供普通网络模块；每块须返回序列和单层末状态。
    不同层之间无 dropout 或隐式状态变换，缺省数学等同原生多层 tanh RNN。
    """

    def __init__(
        self,
        in_features: int,
        hidden_size: int = 32,
        num_layers: int = 2,
        blocks: Sequence[nn.Module] | None = None,
    ) -> None:
        super().__init__()
        if any(
            type(value) is not int or value <= 0 for value in (in_features, hidden_size, num_layers)
        ):
            raise ValueError("输入、隐藏宽度和层数须为正整数")
        if blocks is not None and len(blocks) != num_layers:
            raise ValueError("显式循环块数量须与 num_layers 一致")
        self.in_features = in_features
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.blocks = nn.ModuleList(
            blocks
            if blocks is not None
            else [
                RecurrentBlock(in_features if layer == 0 else hidden_size, hidden_size)
                for layer in range(num_layers)
            ]
        )

    def forward(
        self, x: torch.Tensor, state: torch.Tensor | None = None
    ) -> tuple[torch.Tensor, torch.Tensor]:
        """运行序列，返回 ``[B,T,H]`` 特征和可继续使用的 ``[L,B,H]`` 状态。

        输入、总状态及显式替换块的返回形状不符合局部约定时抛出 ValueError。
        """
        if x.ndim != 3 or x.shape[-1] != self.in_features or x.shape[1] == 0:
            raise ValueError(f"循环阶段输入须为非空时间 [B,T,{self.in_features}]")
        if state is not None:
            if state.shape != (self.num_layers, x.shape[0], self.hidden_size):
                raise ValueError("多层循环状态须为 [L,B,H]")
            if state.device != x.device or state.dtype != x.dtype:
                raise ValueError("循环状态须与输入处于相同设备和精度")
        expected_sequence = (x.shape[0], x.shape[1], self.hidden_size)
        expected_state = (1, x.shape[0], self.hidden_size)
        states = []
        for layer, block in enumerate(self.blocks):
            x, next_state = block(x, None if state is None else state[layer : layer + 1])
            if x.shape != expected_sequence or next_state.shape != expected_state:
                raise ValueError("替换循环块须返回 [B,T,H] 序列及 [1,B,H] 状态")
            states.append(next_state)
        return x, torch.cat(states, dim=0)
