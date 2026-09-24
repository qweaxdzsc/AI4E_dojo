"""用户示例：用公开残差阶段替换U-Net编码器与瓶颈，保留跳连解码。"""

from torch import nn

from ai4e_core.abilities.modeling.models.unet import UNet2d, UNet3d
from ai4e_core.abilities.modeling.modules.residual import BasicResidualBlock2d, BasicResidualBlock3d
from ai4e_core.abilities.modeling.modules.spatial_resampling import SpatialDownsample
from ai4e_core.abilities.modeling.stages.convolution import ResidualStage
from ai4e_core.abilities.modeling.stages.multiscale import MultiScaleEncoder


def build_model(model: dict) -> nn.Module:
    """显式空间维度与通道构造残差U-Net；输入/输出为通道在前。"""
    dim = model.get("spatial_dims", 2)
    if dim not in (2, 3):
        raise ValueError("空间维度须为2/3")
    inc, out = model["in_channels"], model["out_channels"]
    parameters = model.get("parameters", {})
    base, levels = parameters.get("base_channels", 8), parameters.get("levels", 3)
    # 先由公开构造器检查参数，复用默认解码和头，不复制其计算。
    network = (UNet2d if dim == 2 else UNet3d)(inc, out, base_channels=base, levels=levels)
    block = BasicResidualBlock2d if dim == 2 else BasicResidualBlock3d
    widths = [base * 2**i for i in range(levels)]
    encoder = MultiScaleEncoder(
        stages=[
            ResidualStage([block(inc if i == 0 else widths[i - 1], w), block(w, w)])
            for i, w in enumerate(widths)
        ],
        downsamplers=[SpatialDownsample(dim) for _ in widths],
    )
    bottleneck = ResidualStage(
        [block(widths[-1], 2 * widths[-1]), block(2 * widths[-1], 2 * widths[-1])]
    )
    return (UNet2d if dim == 2 else UNet3d)(
        inc,
        out,
        base_channels=base,
        levels=levels,
        encoder=encoder,
        bottleneck=bottleneck,
        decoder=network.decoder,
        head=network.head,
    )
