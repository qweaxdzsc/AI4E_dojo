"""有序多尺度编码和跳连解码，尺寸与特征显式交接。"""

from collections.abc import Sequence

from torch import Tensor, nn


class MultiScaleEncoder(nn.Module):
    """各级先提特征、保存跳连，再下采样；返回浅到深的特征列表。"""

    def __init__(self, stages: Sequence[nn.Module], downsamplers: Sequence[nn.Module]) -> None:
        super().__init__()
        if not stages or len(stages) != len(downsamplers):
            raise ValueError("编码阶段与下采样数量须非空且一致")
        self.stages = nn.ModuleList(stages)
        self.downsamplers = nn.ModuleList(downsamplers)

    def forward(self, value: Tensor) -> tuple[Tensor, list[Tensor], list[tuple[int, ...]]]:
        """返回底部输入、浅到深跳连及空间尺寸；不脱离梯度。"""
        if value.ndim not in (4, 5):
            raise ValueError("编码输入须为二维/三维空间张量")
        features, sizes = [], []
        for stage, downsample in zip(self.stages, self.downsamplers, strict=True):
            value = stage(value)
            features.append(value)
            sizes.append(tuple(value.shape[2:]))
            value = downsample(value)
        return value, features, sizes


class SkipDecoder(nn.Module):
    """融合模块按深到浅注册，消费编码器浅到深的有序交接。"""

    def __init__(self, up_fusions: Sequence[nn.Module]) -> None:
        super().__init__()
        if not up_fusions:
            raise ValueError("解码融合列表不得为空")
        self.up_fusions = nn.ModuleList(up_fusions)

    def forward(
        self, value: Tensor, skip_features: Sequence[Tensor], spatial_sizes: Sequence[Sequence[int]]
    ) -> Tensor:
        """逐层验证尺寸和浅深关系，不用列表截断隐藏缺失层。"""
        if len(skip_features) != len(self.up_fusions) or len(spatial_sizes) != len(skip_features):
            raise ValueError("解码与跳连层数不一致")
        for i, (skip, size) in enumerate(zip(skip_features, spatial_sizes, strict=True)):
            if tuple(skip.shape[2:]) != tuple(size) or skip.ndim != value.ndim:
                raise ValueError("跳连维度或尺寸声明错误")
            if i and any(a > b for a, b in zip(size, spatial_sizes[i - 1], strict=True)):
                raise ValueError("跳连列表必须按浅到深空间尺寸排序")
        for fusion, skip, size in zip(
            self.up_fusions, reversed(skip_features), reversed(spatial_sizes), strict=True
        ):
            value = fusion(value, skip, size)
        return value
