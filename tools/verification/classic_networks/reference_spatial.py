"""独立PyTorch空间网络参考；不导入Dojo计算或其模块结构。

参考实现独立表达本轮明确的场预测变体。残差顺序核对torchvision v0.23.0；
版本、许可及论文差异见reference_spatial_sources.json。此文件不是上游原模型复现。
"""

from collections.abc import Mapping

import torch
from torch import Tensor, nn
from torch.nn import functional as F


def layer(
    dim: int,
    inc: int,
    out: int,
    kernel: int = 3,
    stride: int = 1,
    batch: bool = False,
    relu: bool = False,
    linear: bool = False,
) -> nn.Sequential:
    """直接用PyTorch原语表达参考卷积，不复用产品块。"""
    conv = nn.Conv2d if dim == 2 else nn.Conv3d
    norm = nn.BatchNorm2d if dim == 2 else nn.BatchNorm3d
    items = [conv(inc, out, kernel, stride, kernel // 2, bias=not batch)]
    if batch:
        items.append(norm(out))
    if not linear:
        items.append(nn.ReLU() if relu else nn.GELU())
    return nn.Sequential(*items)


class ReferenceResidual(nn.Module):
    """独立后激活基本/瓶颈残差，v1.5步长位置明确。"""

    def __init__(
        self, dim: int, inc: int, width: int, stride: int = 1, bottleneck: bool = False
    ) -> None:
        super().__init__()
        out = width * (4 if bottleneck else 1)
        if bottleneck:
            self.path = nn.Sequential(
                layer(dim, inc, width, 1, batch=True, relu=True),
                layer(dim, width, width, 3, stride, batch=True, relu=True),
                layer(dim, width, out, 1, batch=True, linear=True),
            )
        else:
            self.path = nn.Sequential(
                layer(dim, inc, width, 3, stride, batch=True, relu=True),
                layer(dim, width, out, batch=True, linear=True),
            )
        self.skip = (
            nn.Identity()
            if inc == out and stride == 1
            else layer(dim, inc, out, 1, stride, batch=True, linear=True)
        )

    def forward(self, x: Tensor) -> Tensor:
        """独立计算主支和捷径。"""
        return F.relu(self.path(x) + self.skip(x))


class ReferenceCNN(nn.Module):
    """独立同尺度卷积场网络。"""

    def __init__(self, dim: int, inc: int, out: int, width: int, depth: int) -> None:
        super().__init__()
        conv = nn.Conv2d if dim == 2 else nn.Conv3d
        self.body = nn.Sequential(
            *[layer(dim, inc if i == 0 else width, width) for i in range(depth)]
        )
        self.output = conv(width, out, 1)

    def forward(self, x: Tensor) -> Tensor:
        """返回相同空间尺寸场。"""
        return self.output(self.body(x))


class ReferenceResNet(nn.Module):
    """独立2/2/2/2小入口残差场网络，分类池化头不参与。"""

    def __init__(self, dim: int, inc: int, out: int, width: int) -> None:
        super().__init__()
        self.dim = dim
        blocks = [layer(dim, inc, width, batch=True, relu=True)]
        previous = width
        for i in range(4):
            current = width * 2**i
            blocks.extend(
                [
                    ReferenceResidual(dim, previous, current, 1 if i == 0 else 2),
                    ReferenceResidual(dim, current, current),
                ]
            )
            previous = current
        self.body = nn.Sequential(*blocks)
        self.output = (nn.Conv2d if dim == 2 else nn.Conv3d)(8 * width, out, 1)

    def forward(self, x: Tensor) -> Tensor:
        """场头之后插值，与冻结变体相同。"""
        return F.interpolate(
            self.output(self.body(x)),
            size=x.shape[2:],
            mode="bilinear" if self.dim == 2 else "trilinear",
            align_corners=False,
        )


class ReferenceUNet(nn.Module):
    """独立双卷积U-Net：不调用产品编码器、跳连或尺寸转换。"""

    def __init__(self, dim: int, inc: int, out: int, width: int, levels: int) -> None:
        super().__init__()
        self.dim = dim
        widths = [width * 2**i for i in range(levels)]

        def pair(a: int, b: int) -> nn.Sequential:
            return nn.Sequential(layer(dim, a, b), layer(dim, b, b))

        self.encoders = nn.ModuleList(
            [pair(inc if i == 0 else widths[i - 1], w) for i, w in enumerate(widths)]
        )
        self.middle = pair(widths[-1], 2 * widths[-1])
        self.decoders = nn.ModuleList([pair(3 * w, w) for w in reversed(widths)])
        self.output = (nn.Conv2d if dim == 2 else nn.Conv3d)(width, out, 1)

    def forward(self, x: Tensor) -> Tensor:
        """用原语显式编码、池化、插值和拼接。"""
        skips = []
        for encode in self.encoders:
            x = encode(x)
            skips.append(x)
            x = F.max_pool2d(x, 2) if self.dim == 2 else F.max_pool3d(x, 2)
        x = self.middle(x)
        for decode, skip in zip(self.decoders, reversed(skips), strict=True):
            x = F.interpolate(
                x,
                size=skip.shape[2:],
                mode="bilinear" if self.dim == 2 else "trilinear",
                align_corners=False,
            )
            x = decode(torch.cat((skip, x), dim=1))
        return self.output(x)


def build_reference_model(
    family: str, spatial_dim: int, in_channels: int, out_channels: int, **parameters
) -> nn.Module:
    """构造独立参考，只接受冻结的三个网络族及2/3空间维。"""
    if spatial_dim not in (2, 3):
        raise ValueError("参考空间维须为2/3")
    accepted = {
        "cnn": {"hidden_channels", "hidden_layers"},
        "resnet": {"base_channels"},
        "unet": {"base_channels", "levels"},
    }
    if family not in accepted:
        raise ValueError("未知参考网络族")
    if set(parameters) - accepted[family]:
        raise ValueError("参考包含未声明参数")
    if family == "cnn":
        return ReferenceCNN(
            spatial_dim,
            in_channels,
            out_channels,
            parameters.get("hidden_channels", 16),
            parameters.get("hidden_layers", 4),
        )
    if family == "resnet":
        return ReferenceResNet(
            spatial_dim, in_channels, out_channels, parameters.get("base_channels", 16)
        )
    return ReferenceUNet(
        spatial_dim,
        in_channels,
        out_channels,
        parameters.get("base_channels", 8),
        parameters.get("levels", 3),
    )


def copy_weights(source: nn.Module | Mapping[str, Tensor], target: nn.Module) -> None:
    """按冻结构造的状态顺序转移权重和BN缓冲，严格检查数量及形状。

    两边使用不同模块命名，必须记录映射；此函数不计算网络或拟合参数。
    """
    state = source.state_dict() if isinstance(source, nn.Module) else source
    target_state = target.state_dict()
    if len(state) != len(target_state):
        raise ValueError("参考权重项数不相同")
    mapped = {}
    for (_, value), (name, expected) in zip(state.items(), target_state.items(), strict=True):
        if value.shape != expected.shape or value.dtype != expected.dtype:
            raise ValueError(f"参考权重映射不相容: {name}")
        mapped[name] = value.detach().clone()
    target.load_state_dict(mapped, strict=True)
