"""小输入ResNet18场预测变体：3核入口、无入口池化、线性场头。

阶段2/2/2/2；不是原ImageNet分类头。输出显式插值回原空间尺寸。
"""

from torch import Tensor, nn

from ..modules.convolution import ConvBlock2d, ConvBlock3d
from ..modules.residual import BasicResidualBlock2d, BasicResidualBlock3d
from ..modules.spatial_resampling import resize_spatial
from ..stages.convolution import ConvStage, ResidualStage


class ResNet(nn.Module):
    """默认宽度16的四阶段残差编码器，可独立替换编码器/读出。"""

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        *,
        spatial_dim: int,
        base_channels: int = 16,
        encoder: nn.Module | None = None,
        head: nn.Module | None = None,
    ) -> None:
        super().__init__()
        if spatial_dim not in (2, 3) or any(
            isinstance(n, bool) or not isinstance(n, int) or n < 1
            for n in (in_channels, out_channels, base_channels)
        ):
            raise ValueError("残差网络维度或通道非法")
        block = BasicResidualBlock2d if spatial_dim == 2 else BasicResidualBlock3d
        convblock = ConvBlock2d if spatial_dim == 2 else ConvBlock3d
        conv = nn.Conv2d if spatial_dim == 2 else nn.Conv3d
        self.spatial_dim, self.in_channels = spatial_dim, in_channels
        if encoder is None:
            layers = [
                convblock(in_channels, base_channels, normalization="batch", activation="relu")
            ]
            previous = base_channels
            for i in range(4):
                width = base_channels * 2**i
                layers.append(
                    ResidualStage(
                        [block(previous, width, stride=1 if i == 0 else 2), block(width, width)]
                    )
                )
                previous = width
            encoder = ConvStage(layers)
        self.encoder = encoder
        self.head = head if head is not None else conv(8 * base_channels, out_channels, 1)

    def forward_features(self, value: Tensor) -> Tensor:
        """返回最后一级低分辨率特征，不执行场读出。"""
        if value.ndim != self.spatial_dim + 2 or value.shape[1] != self.in_channels:
            raise ValueError("ResNet输入维度或通道不相容")
        return self.encoder(value)

    def forward(self, value: Tensor) -> Tensor:
        """线性场头后插值回输入尺寸，明确区别分类网络。"""
        return resize_spatial(self.head(self.forward_features(value)), value.shape[2:])


class ResNet2d(ResNet):
    """二维小输入ResNet18场预测变体。"""

    def __init__(self, in_channels: int, out_channels: int, **kwargs) -> None:
        super().__init__(in_channels, out_channels, spatial_dim=2, **kwargs)


class ResNet3d(ResNet):
    """三维小输入ResNet18场预测变体。"""

    def __init__(self, in_channels: int, out_channels: int, **kwargs) -> None:
        super().__init__(in_channels, out_channels, spatial_dim=3, **kwargs)
