"""公共多尺度阶段组成的二维/三维U-Net，开放四个实际构造位置。

默认三级、GELU、线性插值，是场预测变体，不冒称原分割论文设置。
"""

from torch import Tensor, nn

from ..modules.convolution import ConvBlock2d, ConvBlock3d
from ..modules.skip_fusion import SkipFusion
from ..modules.spatial_resampling import SpatialDownsample
from ..stages.convolution import ConvStage
from ..stages.multiscale import MultiScaleEncoder, SkipDecoder


class UNet(nn.Module):
    """多尺度场预测，编码器显式交付浅到深跳连及尺寸。"""

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        *,
        spatial_dim: int,
        base_channels: int = 8,
        levels: int = 3,
        encoder: nn.Module | None = None,
        bottleneck: nn.Module | None = None,
        decoder: nn.Module | None = None,
        head: nn.Module | None = None,
    ) -> None:
        super().__init__()
        if spatial_dim not in (2, 3) or any(
            isinstance(n, bool) or not isinstance(n, int) or n < 1
            for n in (in_channels, out_channels, base_channels, levels)
        ):
            raise ValueError("U-Net维度、通道或层数非法")
        block = ConvBlock2d if spatial_dim == 2 else ConvBlock3d
        conv = nn.Conv2d if spatial_dim == 2 else nn.Conv3d
        self.spatial_dim, self.in_channels = spatial_dim, in_channels
        widths = [base_channels * 2**i for i in range(levels)]

        def double(inc: int, out: int) -> ConvStage:
            return ConvStage([block(inc, out), block(out, out)])

        self.encoder = (
            encoder
            if encoder is not None
            else MultiScaleEncoder(
                stages=[
                    double(in_channels if i == 0 else widths[i - 1], width)
                    for i, width in enumerate(widths)
                ],
                downsamplers=[SpatialDownsample(spatial_dim) for _ in widths],
            )
        )
        self.bottleneck = (
            bottleneck if bottleneck is not None else double(widths[-1], 2 * widths[-1])
        )
        self.decoder = (
            decoder
            if decoder is not None
            else SkipDecoder([SkipFusion(double(3 * width, width)) for width in reversed(widths)])
        )
        self.head = head if head is not None else conv(base_channels, out_channels, 1)

    def forward_features(self, value: Tensor) -> tuple[Tensor, list[Tensor], list[tuple[int, ...]]]:
        """返回解码特征、浅到深跳连及尺寸，方便独立消费。"""
        if value.ndim != self.spatial_dim + 2 or value.shape[1] != self.in_channels:
            raise ValueError("U-Net输入维度或通道不相容")
        bottom, skips, sizes = self.encoder(value)
        return self.decoder(self.bottleneck(bottom), skips, sizes), skips, sizes

    def forward(self, value: Tensor) -> Tensor:
        """由注入的四部分预测，默认输出保持输入空间尺寸。"""
        features, _, _ = self.forward_features(value)
        return self.head(features)


class UNet2d(UNet):
    """二维三级场U-Net。"""

    def __init__(self, in_channels: int, out_channels: int, **kwargs) -> None:
        super().__init__(in_channels, out_channels, spatial_dim=2, **kwargs)


class UNet3d(UNet):
    """三维三级场U-Net，三空间轴均下采样。"""

    def __init__(self, in_channels: int, out_channels: int, **kwargs) -> None:
        super().__init__(in_channels, out_channels, spatial_dim=3, **kwargs)
