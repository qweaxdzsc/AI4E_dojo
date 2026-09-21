"""仅网络定义；可以交付两组，不含数据处理、训练或评价实现。"""

import torch
from torch import nn
from torch.nn import functional as F


class Block(nn.Sequential):
    """两层保持分辨率的卷积与 ReLU。"""

    def __init__(self, inputs, outputs):
        super().__init__(
            nn.Conv2d(inputs, outputs, 3, padding=1),
            nn.ReLU(),
            nn.Conv2d(outputs, outputs, 3, padding=1),
            nn.ReLU(),
        )


class UNet(nn.Module):
    """60 通道历史映射至 30 通道未来；100 网格跳接按实际尺寸插值。"""

    def __init__(self):
        super().__init__()
        self.enc = nn.ModuleList([Block(60, 16), Block(16, 32), Block(32, 64), Block(64, 128)])
        self.dec = nn.ModuleList([Block(192, 64), Block(96, 32), Block(48, 16)])
        self.head = nn.Conv2d(16, 30, 1)

    def forward(self, x):
        """返回 [batch, 5*6, R, Z]，通道按时间、字段排列。"""
        skips = []
        for layer in self.enc[:-1]:
            x = layer(x)
            skips.append(x)
            x = F.max_pool2d(x, 2)
        x = self.enc[-1](x)
        for layer, skip in zip(self.dec, reversed(skips), strict=True):
            x = layer(
                torch.cat(
                    [
                        F.interpolate(
                            x, size=skip.shape[-2:], mode="bilinear", align_corners=False
                        ),
                        skip,
                    ],
                    dim=1,
                )
            )
        return self.head(x)
