"""完整循环回归模型：输入映射、循环阶段与输出映射显式组合。"""

import torch
from torch import nn

from ai4e_core.abilities.modeling.stages.recurrent import RecurrentStage


class RNN(nn.Module):
    """默认 Identity→两层 Elman tanh 循环→Linear 的序列回归模型。

    三个映射可分别注入普通模块；替换后的宽度交接由调用方明确。
    模型返回整个序列与末状态，不猜测时间目标或只取最后时刻。
    """

    def __init__(
        self,
        in_features: int,
        out_features: int,
        hidden_size: int = 32,
        num_layers: int = 2,
        input_mapping: nn.Module | None = None,
        recurrent_stage: nn.Module | None = None,
        output_mapping: nn.Module | None = None,
    ) -> None:
        super().__init__()
        if any(
            type(value) is not int or value <= 0
            for value in (in_features, out_features, hidden_size, num_layers)
        ):
            raise ValueError("输入、输出、隐藏宽度与层数须为正整数")
        self.in_features = in_features
        self.out_features = out_features
        self.input_mapping = nn.Identity() if input_mapping is None else input_mapping
        self.recurrent_stage = (
            RecurrentStage(in_features, hidden_size, num_layers)
            if recurrent_stage is None
            else recurrent_stage
        )
        self.output_mapping = (
            nn.Linear(hidden_size, out_features) if output_mapping is None else output_mapping
        )

    def forward(
        self, x: torch.Tensor, state: torch.Tensor | None = None
    ) -> tuple[torch.Tensor, torch.Tensor]:
        """接收 ``[B,T,Cin]`` 和显式状态，返回 ``[B,T,Cout]`` 及新状态。

        输入映射须保留批次/时间轴；输出映射须保持序列长度。独立样本应省略
        state，同一序列续段才显式传回；本模型不保存或分离状态。
        """
        if x.ndim != 3 or x.shape[-1] != self.in_features or x.shape[1] == 0:
            raise ValueError(f"RNN 输入须为非空时间 [B,T,{self.in_features}]")
        features = self.input_mapping(x)
        if features.ndim != 3 or features.shape[:2] != x.shape[:2]:
            raise ValueError("输入映射须保留批次和时间轴")
        features, next_state = self.recurrent_stage(features, state)
        prediction = self.output_mapping(features)
        if prediction.shape != (*x.shape[:2], self.out_features):
            raise ValueError("输出映射须保留批次、时间轴及声明的输出宽度")
        return prediction, next_state
