"""规则二维/三维张量的实傅里叶卷积与谱—局部计算块。

根据 Li 等 arXiv:2010.08895 的截断谱算子独立实现。不是旧 GPL 谱实现的
重命名；NeuralOperator MIT 参考的频率和权重映射在独立验证工具中维护。
"""

from itertools import product

import torch
from torch import Tensor, nn

from ai4e_core.abilities.modeling.modules.convolution import ConvBlock


class SpectralConv(nn.Module):
    """截断实频谱上的通道映射，无偏置。

    modes 前 d-1 轴每侧保留 m 个频率，即 [0,m)、[-m,0)；最后 rFFT
    轴保留 [0,m)。不静默裁断越界模式。weight_parts 是末轴为实/虚部的
    实数参数，weight 是复数视图；常规 float/double/to 不会丢虚部。
    """

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        modes: tuple[int, ...],
        *,
        fft_norm: str = "forward",
        dtype: torch.dtype = torch.float32,
    ) -> None:
        super().__init__()
        if not isinstance(modes, (tuple, list)) or len(modes) not in (2, 3):
            raise ValueError("modes 须为二维或三维元组")
        if any(type(n) is not int or n <= 0 for n in (in_channels, out_channels, *modes)):
            raise ValueError("通道和保留模式须为正整数")
        if fft_norm not in ("forward", "backward", "ortho"):
            raise ValueError("fft_norm 须为 forward/backward/ortho")
        if dtype not in (torch.float32, torch.float64):
            raise ValueError("谱卷积仅支持 float32/float64 实数精度")
        self.in_channels, self.out_channels = in_channels, out_channels
        self.modes, self.fft_norm = tuple(modes), fft_norm
        self.spatial_dim = len(modes)
        self.signs = tuple(product((False, True), repeat=self.spatial_dim - 1))
        shape = (len(self.signs), in_channels, out_channels, *modes, 2)
        self.weight_parts = nn.Parameter(
            torch.randn(shape, dtype=dtype) / (in_channels * out_channels)
        )

    @property
    def weight(self) -> Tensor:
        """复数权重视图；需写入时用 no_grad 下的 copy_，梯度读取 weight_parts。"""
        return torch.view_as_complex(self.weight_parts)

    def forward(self, value: Tensor) -> Tensor:
        """将实数 [B,Cin,*S] 映射为 [B,Cout,*S]，显式保留奇偶尺寸。"""
        if value.ndim != self.spatial_dim + 2 or value.shape[1] != self.in_channels:
            raise ValueError("谱输入秩或通道不相容")
        if (
            value.dtype not in (torch.float32, torch.float64)
            or value.dtype != self.weight_parts.dtype
        ):
            raise ValueError("谱输入和权重须使用相同 float32/float64 精度")
        sizes = value.shape[2:]
        if any(2 * m > n for m, n in zip(self.modes[:-1], sizes[:-1], strict=True)):
            raise ValueError("完整频率轴两侧模式交叠或越界")
        if self.modes[-1] > sizes[-1] // 2 + 1:
            raise ValueError("rFFT 非负模式越界")
        dims = tuple(range(-self.spatial_dim, 0))
        spectrum = torch.fft.rfftn(value, dim=dims, norm=self.fft_norm)
        mapped = spectrum.new_zeros(value.shape[0], self.out_channels, *spectrum.shape[2:])
        for corner, negative in enumerate(self.signs):
            region = tuple(
                slice(-m, None) if neg else slice(0, m)
                for m, neg in zip(self.modes[:-1], negative, strict=True)
            ) + (slice(0, self.modes[-1]),)
            index = (slice(None), slice(None), *region)
            mapped[index] = torch.einsum("bi...,io...->bo...", spectrum[index], self.weight[corner])
        return torch.fft.irfftn(mapped, s=sizes, dim=dims, norm=self.fft_norm)


class FourierBlock(nn.Module):
    """谱卷积与逐点局部分支相加，再施加显式激活。

    两支可替换为普通模块，必须输出相同布局；默认局部支复用 ConvBlock。
    """

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        modes: tuple[int, ...],
        *,
        activation: str = "gelu",
        fft_norm: str = "forward",
        dtype: torch.dtype = torch.float32,
        spectral: nn.Module | None = None,
        local: nn.Module | None = None,
    ) -> None:
        super().__init__()
        if activation not in ("gelu", "relu", "none"):
            raise ValueError("activation 须为 gelu/relu/none")
        self.spectral = (
            spectral
            if spectral is not None
            else SpectralConv(in_channels, out_channels, modes, fft_norm=fft_norm, dtype=dtype)
        )
        self.local = (
            local
            if local is not None
            else ConvBlock(
                in_channels,
                out_channels,
                spatial_dim=len(modes),
                kernel_size=1,
                normalization="none",
                activation="none",
            ).to(dtype=dtype)
        )
        if not isinstance(self.spectral, nn.Module) or not isinstance(self.local, nn.Module):
            raise TypeError("spectral/local 须为 nn.Module")
        self.activation = {"gelu": nn.GELU, "relu": nn.ReLU, "none": nn.Identity}[activation]()

    def forward(self, value: Tensor) -> Tensor:
        """保留空间布局，两分支不允许依靠隐式广播相加。"""
        spectral, local = self.spectral(value), self.local(value)
        if spectral.shape != local.shape:
            raise ValueError("谱分支与局部分支输出形状须完全相同")
        return self.activation(spectral + local)
