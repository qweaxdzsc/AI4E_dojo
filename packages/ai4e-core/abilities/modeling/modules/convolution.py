"""中立二维/三维卷积特征块，显式固定卷积、归一化、激活顺序。"""

from torch import Tensor, nn


class ConvBlock(nn.Module):
    """卷积后归一化再激活；奇数卷积核采用对称零填充。"""

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        *,
        spatial_dim: int,
        kernel_size: int = 3,
        stride: int = 1,
        normalization: str = "none",
        activation: str = "gelu",
    ) -> None:
        super().__init__()
        if (
            spatial_dim not in (2, 3)
            or any(
                isinstance(n, bool) or not isinstance(n, int) or n < 1
                for n in (in_channels, out_channels, kernel_size, stride)
            )
            or kernel_size % 2 != 1
        ):
            raise ValueError("通道、步长须为正整数，空间维度须为2/3且卷积核须为奇数")
        if normalization not in ("none", "batch") or activation not in ("none", "gelu", "relu"):
            raise ValueError("不支持的归一化或激活")
        conv = nn.Conv2d if spatial_dim == 2 else nn.Conv3d
        norm = nn.BatchNorm2d if spatial_dim == 2 else nn.BatchNorm3d
        self.spatial_dim, self.in_channels = spatial_dim, in_channels
        self.conv = conv(
            in_channels,
            out_channels,
            kernel_size,
            stride,
            padding=kernel_size // 2,
            bias=normalization == "none",
        )
        self.norm = norm(out_channels) if normalization == "batch" else nn.Identity()
        self.activation = {"none": nn.Identity, "relu": nn.ReLU, "gelu": nn.GELU}[activation]()

    def forward(self, value: Tensor) -> Tensor:
        """接收[B,C,*空间]浮点张量，返回通道在前的特征。"""
        if value.ndim != self.spatial_dim + 2 or value.shape[1] != self.in_channels:
            raise ValueError("卷积输入维度或通道不相容")
        if not value.is_floating_point():
            raise ValueError("卷积输入必须是浮点张量")
        return self.activation(self.norm(self.conv(value)))


class ConvBlock2d(ConvBlock):
    """二维卷积特征块；输入[B,C,H,W]。"""

    def __init__(self, in_channels: int, out_channels: int, **kwargs) -> None:
        super().__init__(in_channels, out_channels, spatial_dim=2, **kwargs)


class ConvBlock3d(ConvBlock):
    """三维卷积特征块；输入[B,C,X,Y,Z]。"""

    def __init__(self, in_channels: int, out_channels: int, **kwargs) -> None:
        super().__init__(in_channels, out_channels, spatial_dim=3, **kwargs)
