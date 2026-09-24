"""由公共卷积块和顺序阶段组成的二维/三维场预测网络。"""

from torch import Tensor, nn

from ..modules.convolution import ConvBlock2d, ConvBlock3d
from ..stages.convolution import ConvStage


class CNN(nn.Module):
    """保持空间尺寸的卷积网络，可替换编码器及输出头。"""

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        *,
        spatial_dim: int,
        hidden_channels: int = 16,
        hidden_layers: int = 4,
        encoder: nn.Module | None = None,
        head: nn.Module | None = None,
    ) -> None:
        super().__init__()
        if spatial_dim not in (2, 3) or any(
            isinstance(n, bool) or not isinstance(n, int) or n < 1
            for n in (in_channels, out_channels, hidden_channels, hidden_layers)
        ):
            raise ValueError("网络维度和通道/层数必须合法")
        block = ConvBlock2d if spatial_dim == 2 else ConvBlock3d
        conv = nn.Conv2d if spatial_dim == 2 else nn.Conv3d
        self.spatial_dim, self.in_channels = spatial_dim, in_channels
        self.encoder = (
            encoder
            if encoder is not None
            else ConvStage(
                [
                    block(in_channels if i == 0 else hidden_channels, hidden_channels)
                    for i in range(hidden_layers)
                ]
            )
        )
        self.head = head if head is not None else conv(hidden_channels, out_channels, 1)

    def forward_features(self, value: Tensor) -> Tensor:
        """直接读取空间特征，保留反向传播。"""
        if value.ndim != self.spatial_dim + 2 or value.shape[1] != self.in_channels:
            raise ValueError("CNN输入维度或通道不相容")
        return self.encoder(value)

    def forward(self, value: Tensor) -> Tensor:
        """预测通道在前的场，默认保持输入空间尺寸。"""
        return self.head(self.forward_features(value))


class CNN2d(CNN):
    """二维普通卷积网络。"""

    def __init__(self, in_channels: int, out_channels: int, **kwargs) -> None:
        super().__init__(in_channels, out_channels, spatial_dim=2, **kwargs)


class CNN3d(CNN):
    """三维普通卷积网络。"""

    def __init__(self, in_channels: int, out_channels: int, **kwargs) -> None:
        super().__init__(in_channels, out_channels, spatial_dim=3, **kwargs)
