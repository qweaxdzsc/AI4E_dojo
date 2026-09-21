"""将全局参数映射并广播为空间时间特征。

源自 Code Ocean capsule 8000337 v1.0，GPL-3.0；来源及许可证见 PCNO source.json。
"""

from torch import nn

class GlobalFeatureFusion(nn.Module):
    """将全局参数映射并广播为空间时间特征：GlobalFeatureFusion；保留来源算法、参数与权重布局。"""

    def __init__(self, global_dim, target_channels):
        super(GlobalFeatureFusion, self).__init__()
        self.mlp = nn.Sequential(nn.Linear(global_dim, 64), nn.ReLU(), nn.Linear(64, target_channels))

    def forward(self, global_params, shape_to_expand):
        B, C, X, Y, Z, T = shape_to_expand
        fused = self.mlp(global_params)
        return fused.view(B, C, 1, 1, 1, 1).expand(B, C, X, Y, Z, T)
