"""四维实数 FFT 谱卷积，八个频域角块。

源自 Code Ocean capsule 8000337 v1.0，GPL-3.0；来源及许可证见 PCNO source.json。
"""

import torch
from torch import nn

class SpectralConv4d(nn.Module):
    """四维实数 FFT 谱卷积，八个频域角块：SpectralConv4d；保留来源算法、参数与权重布局。"""

    def __init__(self, in_channels, out_channels, modes1, modes2, modes3, modes4):
        super(SpectralConv4d, self).__init__()
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.modes1 = modes1
        self.modes2 = modes2
        self.modes3 = modes3
        self.modes4 = modes4
        self.scale = 1 / (in_channels * out_channels)

        def cw():
            return self.scale * torch.rand(in_channels, out_channels, self.modes1, self.modes2, self.modes3, self.modes4, dtype=torch.cfloat)
        self.weights = nn.ParameterList([nn.Parameter(cw()) for _ in range(8)])

    def compl_mul4d(self, input, weights):
        return torch.einsum('bixyzt,ioxyzt->boxyzt', input, weights)

    def forward(self, x):
        B = x.shape[0]
        x = x.contiguous().to(dtype=torch.float32)
        x_ft = torch.fft.rfftn(x, dim=[-4, -3, -2, -1])
        out_ft = torch.zeros(B, self.out_channels, x.size(-4), x.size(-3), x.size(-2), x.size(-1) // 2 + 1, dtype=torch.cfloat, device=x.device)
        idx = lambda i: (slice(None), slice(None), slice(None, self.modes1) if i & 1 == 0 else slice(-self.modes1, None), slice(None, self.modes2) if i & 2 == 0 else slice(-self.modes2, None), slice(None, self.modes3) if i & 4 == 0 else slice(-self.modes3, None), slice(None, self.modes4))
        for i in range(8):
            out_ft[idx(i)] = self.compl_mul4d(x_ft[idx(i)], self.weights[i])
        x = torch.fft.irfftn(out_ft, s=x.shape[-4:])
        return x
