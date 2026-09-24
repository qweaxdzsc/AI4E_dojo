"""末轴前馈计算：旧 Mlp 保留 AB-UPT 算术，新 FeedForward 复用投影组件。

旧 Mlp 的来源与 ENPL 许可见贡献组件 LICENSE；新增 FeedForward 为本地连接，
其组合的 projected_mlp 实现保留 NVIDIA Apache-2.0 来源，不重标旧代码许可。
"""

import torch
from torch import nn

from ai4e_core.abilities.modeling.modules.projected_mlp import Mlp as ProjectedMlp
from ai4e_core.abilities.modeling.modules.projected_mlp import get_activation


class Mlp(nn.Module):
    """MLP as used in transformers nn.Linear(dim, dim * 4) -> GELU -> nn.Linear(dim * 4, dim).

    Args:
        dim: Input dimension of the MLP.
    """

    def __init__(self, dim: int):
        super().__init__()
        self.fc1 = nn.Linear(dim, dim * 4)
        self.act = nn.GELU()
        self.fc2 = nn.Linear(dim * 4, dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.fc1(x)
        x = self.act(x)
        x = self.fc2(x)
        return x


class FeedForward(nn.Module):
    """共享多层前馈块，保持输入的所有前导维度。

    参数 ``hidden_features`` 是各隐藏宽度；``activation`` 使用投影模块的显式
    激活名称。每个隐藏层执行线性、激活、dropout，末层仅线性及可选
    ``final_activation``，不对末层附加 dropout。默认有偏置，无归一化或残差。
    旧 Mlp 的结构和权重键不受此类影响。
    """

    def __init__(
        self,
        in_features: int,
        out_features: int,
        hidden_features: tuple[int, ...] = (64,),
        activation: str = "gelu",
        final_activation: str | None = None,
        dropout: float = 0.0,
    ) -> None:
        super().__init__()
        if not isinstance(hidden_features, (tuple, list)):
            raise TypeError("hidden_features 须为隐藏宽度序列")
        widths = (in_features, *hidden_features, out_features)
        if any(type(width) is not int or width <= 0 for width in widths):
            raise ValueError("输入、输出和隐藏宽度须为正整数")
        if not isinstance(dropout, (int, float)) or not 0 <= dropout <= 1:
            raise ValueError("dropout 须在 [0, 1] 内")
        self.in_features = in_features
        self.out_features = out_features
        self.projection = ProjectedMlp(
            in_features=in_features,
            out_features=out_features,
            hidden_features=list(hidden_features),
            act_layer=activation,
            drop=float(dropout),
            final_dropout=False,
            use_batchnorm=False,
            spectral_norm=False,
        )
        self.final_activation = (
            nn.Identity() if final_activation is None else get_activation(final_activation)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """将 ``[..., in_features]`` 映射到 ``[..., out_features]``。

        不展平样本、节点或网格轴；末轴不匹配时抛出 ValueError。
        """
        if x.ndim < 1 or x.shape[-1] != self.in_features:
            raise ValueError(f"前馈输入末轴须为 {self.in_features}，实际 {tuple(x.shape)}")
        return self.final_activation(self.projection(x))
