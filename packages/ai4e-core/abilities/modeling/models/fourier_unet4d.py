"""四维谱算子和共享三维 U-Net 特征组合；一次 U-Net 结果供四层重复使用。

源自 Code Ocean capsule 8000337 v1.0，GPL-3.0；来源及许可证见 PCNO source.json。
"""

import torch
from torch import nn
from torch.nn import functional as F
from ai4e_core.abilities.modeling.modules.fourier4d import SpectralConv4d
from ai4e_core.abilities.modeling.modules.unet_volume import UNet3D_Lite
from ai4e_core.abilities.modeling.modules.global_features import GlobalFeatureFusion

class Block4dWithUNet(nn.Module):
    """四维谱算子和共享三维 U-Net 特征组合；一次 U-Net 结果供四层重复使用：Block4dWithUNet；保留来源算法、参数与权重布局。"""

    def __init__(self, width, width2, modes1, modes2, modes3, modes4, out_dim):
        super(Block4dWithUNet, self).__init__()
        self.width = width
        self.width2 = width2
        self.out_dim = out_dim
        self.padding = 8
        self.Z_padding = 2
        self.conv_layers = nn.ModuleList([SpectralConv4d(width, width, modes1, modes2, modes3, modes4) for _ in range(4)])
        self.linear_layers = nn.ModuleList([nn.Conv1d(width, width, 1) for _ in range(4)])
        self.norm_layers = nn.ModuleList([nn.GroupNorm(num_groups=8, num_channels=width) for _ in range(4)])
        self.unet = UNet3D_Lite(width, base_channels=width // 2)
        self.alpha = nn.Parameter(torch.ones(1) * 0.1)
        self.fc1 = nn.Linear(width, width2)
        self.fc2 = nn.Linear(width2, out_dim)

    def forward(self, x):
        B, C, X, Y, Z, T = x.shape
        x_unet = x.permute(0, 5, 1, 2, 3, 4).contiguous()
        x_unet = x_unet.view(B * T, C, X, Y, Z)
        unet_out = self.unet(x_unet)
        unet_out = unet_out.view(B, T, C, X, Y, Z).permute(0, 2, 3, 4, 5, 1).contiguous()
        for conv, lin, norm in zip(self.conv_layers, self.linear_layers, self.norm_layers):
            x1 = conv(x)
            x2 = lin(x.view(B, self.width, -1)).view(B, self.width, X, Y, Z, T)
            gated_unet_out = self.alpha * unet_out
            x = x1 + x2 + gated_unet_out
            x = norm(x)
            x = F.gelu(x)
        x = x[:, :, self.padding * 2:-self.padding * 2, self.padding * 2:-self.padding * 2, self.Z_padding:-self.Z_padding, self.padding:-self.padding]
        x = x.permute(0, 2, 3, 4, 5, 1)
        x = self.fc1(x)
        x = F.gelu(x)
        x = self.fc2(x)
        return x

class FNO4dUNet(nn.Module):
    """四维谱算子和共享三维 U-Net 特征组合；一次 U-Net 结果供四层重复使用：FNO4dUNet；保留来源算法、参数与权重布局。"""

    def __init__(self, modes1, modes2, modes3, modes4, width, in_dim):
        super(FNO4dUNet, self).__init__()
        self.padding = 8
        self.fc0 = nn.Linear(in_dim, width)
        self.conv = Block4dWithUNet(width, width * 4, modes1, modes2, modes3, modes4, out_dim=1)

    def forward(self, x):
        x = self.fc0(x)
        x = x.permute(0, 5, 1, 2, 3, 4)
        x = F.pad(x, [self.padding] * 2 + [self.padding * 2] * 2 + [self.padding * 2] * 2 + [self.padding] * 2)
        x = self.conv(x)
        return x.squeeze(-1)

class FNO4dUNet_WithGlobalFusion(nn.Module):
    """四维谱算子和共享三维 U-Net 特征组合；一次 U-Net 结果供四层重复使用：FNO4dUNet_WithGlobalFusion；保留来源算法、参数与权重布局。"""

    def __init__(self, modes1, modes2, modes3, modes4, width, in_dim, global_dim):
        super(FNO4dUNet_WithGlobalFusion, self).__init__()
        self.fno_core = FNO4dUNet(modes1, modes2, modes3, modes4, width, in_dim)
        self.global_fusion = GlobalFeatureFusion(global_dim, width)
        self.fusion_conv1d = nn.Conv1d(2 * width, width, kernel_size=1)
        self.norm_fusion = nn.GroupNorm(num_groups=8, num_channels=width)

    def forward(self, x, global_params):
        x = self.fno_core.fc0(x)
        x = x.permute(0, 5, 1, 2, 3, 4).contiguous()
        x = F.pad(x, [8, 8, 2, 2, 16, 16, 16, 16])
        global_feat = self.global_fusion(global_params, x.shape)
        x = torch.cat([x, global_feat], dim=1)
        B, C2, Xp, Yp, Zp, Tp = x.shape
        L = Xp * Yp * Zp * Tp
        x = x.reshape(B, C2, L)
        x = self.fusion_conv1d(x)
        x = self.norm_fusion(x)
        x = x.reshape(B, -1, Xp, Yp, Zp, Tp).contiguous()
        x = self.fno_core.conv(x)
        return x.squeeze(-1)
