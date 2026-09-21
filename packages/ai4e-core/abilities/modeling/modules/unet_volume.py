"""三维 U-Net，仅在前两个空间轴池化。

源自 Code Ocean capsule 8000337 v1.0，GPL-3.0；来源及许可证见 PCNO source.json。
"""

import torch
from torch import nn

class UNet3D_Lite(nn.Module):
    """三维 U-Net，仅在前两个空间轴池化：UNet3D_Lite；保留来源算法、参数与权重布局。"""

    def __init__(self, in_channels, base_channels=32):
        super(UNet3D_Lite, self).__init__()
        self.enc1 = nn.Sequential(nn.Conv3d(in_channels, base_channels, 3, padding=1), nn.GroupNorm(num_groups=4, num_channels=base_channels), nn.ReLU(), nn.Conv3d(base_channels, base_channels, 3, padding=1), nn.GroupNorm(num_groups=4, num_channels=base_channels), nn.ReLU())
        self.pool1 = nn.MaxPool3d(kernel_size=(2, 2, 1))
        self.enc2 = nn.Sequential(nn.Conv3d(base_channels, base_channels * 2, 3, padding=1), nn.GroupNorm(num_groups=4, num_channels=base_channels * 2), nn.ReLU(), nn.Conv3d(base_channels * 2, base_channels * 2, 3, padding=1), nn.GroupNorm(num_groups=4, num_channels=base_channels * 2), nn.ReLU())
        self.pool2 = nn.MaxPool3d(kernel_size=(2, 2, 1))
        self.bottom = nn.Sequential(nn.Conv3d(base_channels * 2, base_channels * 4, 3, padding=1), nn.GroupNorm(num_groups=4, num_channels=base_channels * 4), nn.ReLU(), nn.Conv3d(base_channels * 4, base_channels * 2, 3, padding=1), nn.GroupNorm(num_groups=4, num_channels=base_channels * 2), nn.ReLU())
        self.up1 = nn.ConvTranspose3d(base_channels * 2, base_channels * 2, kernel_size=(2, 2, 1), stride=(2, 2, 1))
        self.dec1 = nn.Sequential(nn.Conv3d(base_channels * 4, base_channels * 2, 3, padding=1), nn.GroupNorm(num_groups=4, num_channels=base_channels * 2), nn.ReLU())
        self.up2 = nn.ConvTranspose3d(base_channels * 2, base_channels, kernel_size=(2, 2, 1), stride=(2, 2, 1))
        self.dec2 = nn.Sequential(nn.Conv3d(base_channels * 2, base_channels, 3, padding=1), nn.GroupNorm(num_groups=4, num_channels=base_channels), nn.ReLU())
        self.out_conv = nn.Conv3d(base_channels, in_channels, 1)

    def forward(self, x):
        e1 = self.enc1(x)
        e2 = self.enc2(self.pool1(e1))
        b = self.bottom(self.pool2(e2))
        up1_crop = self.center_crop(self.up1(b), e2)
        d1 = self.dec1(torch.cat([e2, up1_crop], dim=1))
        up2_crop = self.center_crop(self.up2(d1), e1)
        d2 = self.dec2(torch.cat([e1, up2_crop], dim=1))
        out = self.out_conv(d2)
        return out

    def center_crop(self, source, target):
        _, _, h, w, d = target.shape
        src_h, src_w, src_d = source.shape[2:]
        crop_h = (src_h - h) // 2
        crop_w = (src_w - w) // 2
        crop_d = (src_d - d) // 2
        return source[:, :, crop_h:crop_h + h, crop_w:crop_w + w, crop_d:crop_d + d]
