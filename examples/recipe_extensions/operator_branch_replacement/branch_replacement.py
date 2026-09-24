"""用户分支：将经典MLP与公开前馈块重组，算子主干和读出保持公开连接。"""

import math

from torch import nn

from ai4e_core.abilities.modeling.models.deeponet import DeepONet
from ai4e_core.abilities.modeling.models.mlp import MLP
from ai4e_core.abilities.modeling.modules.feed_forward import FeedForward


class ResidualBranch(nn.Module):
    """传感器压缩后进行潜空间残差细化，参数均按普通模块注册。"""

    def __init__(self, input_width, output_width):
        super().__init__()
        self.encode = MLP(input_width, output_width, hidden_features=(32,), activation="tanh")
        self.refine = FeedForward(output_width, output_width, (32,), "tanh")

    def forward(self, x):
        """固定传感器次序由调用方承担，输出潜变量保持样本轴。"""
        encoded = self.encode(x)
        return encoded + self.refine(encoded)


def build_model(model):
    """返回真正消费新分支的DeepONet，可直接替换components.model。"""
    if model["family"] != "deeponet":
        raise ValueError("分支重组只消费DeepONet局部约定")
    params = dict(model["parameters"])
    stride = params.pop("sensor_stride")
    width = math.prod(len(range(0, n, stride)) for n in model["grid_shape"]) * model["in_channels"]
    outputs = model["out_channels"]
    return DeepONet(
        width,
        model["spatial_dims"],
        out_channels=outputs,
        multi_output="split_branch" if outputs > 1 else None,
        branch=ResidualBranch(width, params["latent_dim"] * outputs),
        **params,
    )
