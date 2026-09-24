"""可拆装规则网格 FNO，显式升维、逐轴补齐、谱阶段、裁剪和读出。"""

import torch
from torch import Tensor, nn
from torch.nn import functional as F

from ai4e_core.abilities.modeling.modules.feed_forward import FeedForward
from ai4e_core.abilities.modeling.modules.spectral import FourierBlock
from ai4e_core.abilities.modeling.stages.fourier import FourierStage


class FNO(nn.Module):
    """通道在前的二维/三维 FNO，默认最终谱块不激活。

    lifting/projection 消费末轴通道，operator 消费通道在前张量。默认三个
    部分真实复用公开组件。padding 为各空间轴右侧补零数，不代表物理边界。
    坐标由调用方显式拼成输入通道；完整空间域不能拆块分别计算后冒充全局谱。
    """

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        *,
        modes: tuple[int, ...],
        width: int = 32,
        depth: int = 4,
        padding: tuple[int, ...] | None = None,
        lifting_hidden: tuple[int, ...] = (),
        projection_hidden: tuple[int, ...] = (128,),
        activation: str = "gelu",
        fft_norm: str = "forward",
        dtype: torch.dtype = torch.float32,
        lifting: nn.Module | None = None,
        operator: nn.Module | None = None,
        projection: nn.Module | None = None,
    ) -> None:
        super().__init__()
        if any(type(n) is not int or n <= 0 for n in (in_channels, out_channels, width, depth)):
            raise ValueError("通道、width、depth 须为正整数")
        if not isinstance(modes, (tuple, list)) or len(modes) not in (2, 3):
            raise ValueError("modes 须声明二维或三维空间")
        if any(type(n) is not int or n <= 0 for n in modes):
            raise ValueError("modes 须为正整数")
        if dtype not in (torch.float32, torch.float64):
            raise ValueError("dtype 须为 float32 或 float64")
        self.spatial_dim, self.in_channels, self.out_channels = (
            len(modes),
            in_channels,
            out_channels,
        )
        self.width = width
        self.padding = tuple(0 for _ in modes) if padding is None else tuple(padding)
        if len(self.padding) != len(modes) or any(
            type(n) is not int or n < 0 for n in self.padding
        ):
            raise ValueError("padding 须为每空间轴一个非负整数")
        self.lifting = (
            lifting
            if lifting is not None
            else FeedForward(in_channels, width, lifting_hidden, activation).to(dtype=dtype)
        )
        self.operator = (
            operator
            if operator is not None
            else FourierStage(
                [
                    FourierBlock(
                        width,
                        width,
                        modes,
                        activation=activation if i < depth - 1 else "none",
                        fft_norm=fft_norm,
                        dtype=dtype,
                    )
                    for i in range(depth)
                ]
            )
        )
        self.projection = (
            projection
            if projection is not None
            else FeedForward(width, out_channels, projection_hidden, activation).to(dtype=dtype)
        )
        if any(
            not isinstance(m, nn.Module) for m in (self.lifting, self.operator, self.projection)
        ):
            raise TypeError("lifting/operator/projection 须为 nn.Module")

    def forward(self, value: Tensor) -> Tensor:
        """输入 [B,Cin,*S]，返回 [B,Cout,*S]；维度错配明确拒绝。"""
        if value.ndim != self.spatial_dim + 2 or value.shape[1] != self.in_channels:
            raise ValueError("FNO 输入秩或通道不相容")
        sizes = value.shape[2:]
        hidden = self.lifting(value.movedim(1, -1)).movedim(-1, 1)
        if hidden.shape != (value.shape[0], self.width, *sizes):
            raise ValueError("lifting 须保持空间轴并输出 width 通道")
        pad = tuple(n for right in reversed(self.padding) for n in (0, right))
        hidden = F.pad(hidden, pad)
        expected = hidden.shape
        hidden = self.operator(hidden)
        if hidden.shape != expected:
            raise ValueError("operator 须保持升维补齐后的完整形状")
        hidden = hidden[(slice(None), slice(None), *(slice(0, n) for n in sizes))]
        result = self.projection(hidden.movedim(1, -1)).movedim(-1, 1)
        if result.shape != (value.shape[0], self.out_channels, *sizes):
            raise ValueError("projection 须保持空间轴并输出 out_channels 通道")
        return result
