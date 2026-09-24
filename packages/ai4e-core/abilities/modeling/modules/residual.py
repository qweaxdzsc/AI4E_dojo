"""基本及瓶颈残差特征块，采用后激活和显式投影捷径。

基本块遵循ResNet-v1，瓶颈步长位于中间3卷积（v1.5）；三维为维度提升变体。
"""

from torch import Tensor, nn

from .convolution import ConvBlock2d, ConvBlock3d


class BasicResidualBlock(nn.Module):
    """两次3卷积后加恒等/投影捷径，再执行ReLU。"""

    expansion = 1

    def __init__(
        self, in_channels: int, channels: int, *, spatial_dim: int, stride: int = 1
    ) -> None:
        super().__init__()
        if spatial_dim not in (2, 3):
            raise ValueError("空间维度须为2/3")
        block = ConvBlock2d if spatial_dim == 2 else ConvBlock3d
        self.first = block(
            in_channels, channels, stride=stride, normalization="batch", activation="relu"
        )
        self.second = block(channels, channels, normalization="batch", activation="none")
        self.shortcut = (
            nn.Identity()
            if stride == 1 and in_channels == channels
            else block(
                in_channels,
                channels,
                kernel_size=1,
                stride=stride,
                normalization="batch",
                activation="none",
            )
        )
        self.activation = nn.ReLU()

    def forward(self, value: Tensor) -> Tensor:
        """同一输入分别进入主支与捷径，相加后激活。"""
        return self.activation(self.second(self.first(value)) + self.shortcut(value))


class Bottleneck(nn.Module):
    """1/3/1卷积瓶颈，输出通道为内部宽度四倍。"""

    expansion = 4

    def __init__(
        self, in_channels: int, channels: int, *, spatial_dim: int, stride: int = 1
    ) -> None:
        super().__init__()
        if spatial_dim not in (2, 3):
            raise ValueError("空间维度须为2/3")
        block = ConvBlock2d if spatial_dim == 2 else ConvBlock3d
        self.first = block(
            in_channels, channels, kernel_size=1, normalization="batch", activation="relu"
        )
        self.second = block(
            channels, channels, stride=stride, normalization="batch", activation="relu"
        )
        self.third = block(
            channels, 4 * channels, kernel_size=1, normalization="batch", activation="none"
        )
        self.shortcut = (
            nn.Identity()
            if stride == 1 and in_channels == 4 * channels
            else block(
                in_channels,
                4 * channels,
                kernel_size=1,
                stride=stride,
                normalization="batch",
                activation="none",
            )
        )
        self.activation = nn.ReLU()

    def forward(self, value: Tensor) -> Tensor:
        """执行主支、捷径和后激活，不重排归一化。"""
        return self.activation(self.third(self.second(self.first(value))) + self.shortcut(value))


class BasicResidualBlock2d(BasicResidualBlock):
    """二维基本残差块。"""

    def __init__(self, in_channels: int, channels: int, *, stride: int = 1) -> None:
        super().__init__(in_channels, channels, spatial_dim=2, stride=stride)


class BasicResidualBlock3d(BasicResidualBlock):
    """三维基本残差块。"""

    def __init__(self, in_channels: int, channels: int, *, stride: int = 1) -> None:
        super().__init__(in_channels, channels, spatial_dim=3, stride=stride)


class Bottleneck2d(Bottleneck):
    """二维瓶颈残差块。"""

    def __init__(self, in_channels: int, channels: int, *, stride: int = 1) -> None:
        super().__init__(in_channels, channels, spatial_dim=2, stride=stride)


class Bottleneck3d(Bottleneck):
    """三维瓶颈残差块。"""

    def __init__(self, in_channels: int, channels: int, *, stride: int = 1) -> None:
        super().__init__(in_channels, channels, spatial_dim=3, stride=stride)
