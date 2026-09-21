"""PCNO 单分支组合；两个独立网络保留作者 state_dict 布局。

源自 Code Ocean capsule 8000337 v1.0，GPL-3.0；来源及许可证见 PCNO source.json。
"""

from torch import nn
from ai4e_core.abilities.modeling.models.fourier_unet4d import FNO4dUNet_WithGlobalFusion

class EnhancedP_T_Net(nn.Module):
    """PCNO 单分支组合；两个独立网络保留作者 state_dict 布局：EnhancedP_T_Net；保留来源算法、参数与权重布局。"""

    def __init__(self, modes1, modes2, modes3, modes4, width_p, width_T, in_dim=14, global_dim=4, train_mode='pres'):
        super(EnhancedP_T_Net, self).__init__()
        assert train_mode in ['pres', 'temp'], "train_mode must be either 'pres' or 'temp'"
        self.train_mode = train_mode
        self.pressure_net = None
        self.temperature_net = None
        if train_mode == 'pres':
            self.pressure_net = FNO4dUNet_WithGlobalFusion(modes1, modes2, modes3, modes4, width_p, in_dim, global_dim)
        elif train_mode == 'temp':
            self.temperature_net = FNO4dUNet_WithGlobalFusion(modes1, modes2, modes3, modes4, width_T, in_dim, global_dim)

    def forward(self, x, global_params):
        if self.train_mode == 'pres':
            return self.pressure_net(x, global_params)
        elif self.train_mode == 'temp':
            return self.temperature_net(x, global_params)
