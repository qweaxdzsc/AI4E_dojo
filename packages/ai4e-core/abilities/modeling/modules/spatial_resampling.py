"""显式尺寸的空间降采样与插值投影，不猜测物理坐标。"""

from collections.abc import Sequence

from torch import Tensor, nn
from torch.nn import functional as F


def resize_spatial(value: Tensor, size: Sequence[int]) -> Tensor:
    """按给定空间尺寸线性插值，不对齐角点；不改变批与通道轴。"""
    size = tuple(size)
    if (
        value.ndim not in (4, 5)
        or len(size) != value.ndim - 2
        or any(isinstance(n, bool) or not isinstance(n, int) or n < 1 for n in size)
    ):
        raise ValueError("插值维度或目标尺寸非法")
    return F.interpolate(
        value, size=size, mode="bilinear" if value.ndim == 4 else "trilinear", align_corners=False
    )


class SpatialDownsample(nn.Module):
    """最大池化并可接通道投影；轴长不足时拒绝，不静默填充。"""

    def __init__(self, spatial_dim: int, *, projection: nn.Module | None = None) -> None:
        super().__init__()
        if spatial_dim not in (2, 3):
            raise ValueError("空间维度须为2/3")
        self.spatial_dim = spatial_dim
        self.pool = (nn.MaxPool2d if spatial_dim == 2 else nn.MaxPool3d)(2)
        self.projection = projection if projection is not None else nn.Identity()

    def forward(self, value: Tensor) -> Tensor:
        """各空间轴缩小二倍后应用显式投影。"""
        if value.ndim != self.spatial_dim + 2 or min(value.shape[2:]) < 2:
            raise ValueError("下采样输入维度错误或空间轴过小")
        return self.projection(self.pool(value))


class SpatialUpsample(nn.Module):
    """插值到声明尺寸后应用可训练投影。"""

    def __init__(self, *, projection: nn.Module | None = None) -> None:
        super().__init__()
        self.projection = projection if projection is not None else nn.Identity()

    def forward(self, value: Tensor, size: Sequence[int]) -> Tensor:
        """目标尺寸由对应跳连或调用者显式交付。"""
        return self.projection(resize_spatial(value, size))
