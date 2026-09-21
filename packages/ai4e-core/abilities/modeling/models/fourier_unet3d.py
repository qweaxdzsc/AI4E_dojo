"""二维空间加时间的谱/U-Net 算子，输入仅包含已知历史。

采用 PCNO 的谱、局部空间及可选全局融合思路重新实现二维变体；
不兼容地热四维权重，不宣称与原始网络数值等价。
"""

import math

import torch
from torch import nn
from torch.nn import functional as F


class SpectralConv3d(nn.Module):
    """对 X/Y/T 计算实数 FFT 的四象限低频线性映射。"""

    def __init__(self, width, modes):
        super().__init__()
        self.modes = tuple(modes)
        self.weight = nn.Parameter(torch.randn(4, width, width, *modes, dtype=torch.cfloat) / width)

    def forward(self, value):
        """将 B/C/X/Y/T 张量映射到相同形状。"""
        mx, my, mt = self.modes
        if 2 * mx > value.shape[2] or 2 * my > value.shape[3] or mt > value.shape[4] // 2 + 1:
            raise ValueError("谱模态超过输入分辨率")
        spectrum = torch.fft.rfftn(value, dim=(-3, -2, -1))
        output = torch.zeros_like(spectrum)
        for i, (sx, sy) in enumerate(
            (
                (slice(0, mx), slice(0, my)),
                (slice(-mx, None), slice(0, my)),
                (slice(0, mx), slice(-my, None)),
                (slice(-mx, None), slice(-my, None)),
            )
        ):
            output[:, :, sx, sy, :mt] = torch.einsum(
                "bixyt,ioxyt->boxyt", spectrum[:, :, sx, sy, :mt], self.weight[i]
            )
        return torch.fft.irfftn(output, s=value.shape[-3:], dim=(-3, -2, -1))


class SpatialUNet2d(nn.Module):
    """二维空间局部特征；时间片共享权重，不沿时间池化。"""

    def __init__(self, width):
        super().__init__()

        def block(inc, out):
            return nn.Sequential(
                nn.Conv2d(inc, out, 3, padding=1),
                nn.GroupNorm(math.gcd(4, out), out),
                nn.GELU(),
                nn.Conv2d(out, out, 3, padding=1),
                nn.GELU(),
            )

        self.encoder = block(width, width)
        self.bottom = block(width, 2 * width)
        self.decoder = block(3 * width, width)

    def forward(self, value):
        """计算保留原空间分辨率的局部特征。"""
        encoded = self.encoder(value)
        bottom = self.bottom(F.avg_pool2d(encoded, 2))
        up = F.interpolate(bottom, size=value.shape[-2:], mode="bilinear", align_corners=False)
        return self.decoder(torch.cat((encoded, up), dim=1))


class FourierUNet3d(nn.Module):
    """历史 B/H/X/Y/C 到未来 B/T/X/Y/C；时间坐标为预测窗口内相对位置。"""

    def __init__(
        self,
        in_channels,
        out_channels,
        history=3,
        horizon=12,
        width=8,
        modes=(4, 4, 4),
        blocks=4,
        global_dim=0,
    ):
        super().__init__()
        if (
            min(in_channels, out_channels, history, horizon, width, blocks, *modes) < 1
            or global_dim < 0
        ):
            raise ValueError("网络维度非法")
        self.history, self.horizon, self.in_channels = history, horizon, in_channels
        self.global_dim = global_dim
        self.lift = nn.Linear(history * in_channels + 3, width)
        self.global_lift = nn.Linear(global_dim, width) if global_dim else None
        self.spectral = nn.ModuleList(SpectralConv3d(width, modes) for _ in range(blocks))
        self.local = nn.ModuleList(nn.Conv3d(width, width, 1) for _ in range(blocks))
        self.norm = nn.ModuleList(nn.GroupNorm(math.gcd(4, width), width) for _ in range(blocks))
        self.unet = SpatialUNet2d(width)
        self.alpha = nn.Parameter(torch.tensor(0.1))
        self.project = nn.Sequential(
            nn.Linear(width, 4 * width), nn.GELU(), nn.Linear(4 * width, out_channels)
        )

    def forward(self, history, global_parameters=None):
        """不接收目标或未来几何；可选全局参数须由调用者显式给定。"""
        if (
            history.ndim != 5
            or history.shape[1] != self.history
            or history.shape[-1] != self.in_channels
        ):
            raise ValueError("历史张量形状不相容")
        b, _, x, y, _ = history.shape
        t = self.horizon
        known = (
            history.permute(0, 2, 3, 1, 4)
            .reshape(b, x, y, -1)
            .unsqueeze(3)
            .expand(-1, -1, -1, t, -1)
        )
        axes = [
            torch.linspace(0, 1, n, device=history.device, dtype=history.dtype) for n in (x, y, t)
        ]
        coordinates = (
            torch.stack(torch.meshgrid(*axes, indexing="ij"), -1)
            .unsqueeze(0)
            .expand(b, -1, -1, -1, -1)
        )
        value = self.lift(torch.cat((known, coordinates), dim=-1))
        if self.global_lift is not None:
            if global_parameters is None or global_parameters.shape != (b, self.global_dim):
                raise ValueError("全局参数缺失或形状错误")
            value = value + self.global_lift(global_parameters)[:, None, None, None, :]
        elif global_parameters is not None:
            raise ValueError("未配置全局参数维数")
        value = value.permute(0, 4, 1, 2, 3).contiguous()
        spatial = value.permute(0, 4, 1, 2, 3).reshape(b * t, -1, x, y)
        spatial = self.unet(spatial).reshape(b, t, -1, x, y).permute(0, 2, 3, 4, 1)
        for spectral, local, norm in zip(self.spectral, self.local, self.norm):
            value = F.gelu(norm(spectral(value) + local(value) + self.alpha * spatial))
        return self.project(value.permute(0, 4, 2, 3, 1))
