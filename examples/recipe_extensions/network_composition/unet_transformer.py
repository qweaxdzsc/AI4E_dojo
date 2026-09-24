"""用户示例：U-Net瓶颈显式转token并使用公开标准注意力阶段。"""

from torch import Tensor, nn

from ai4e_core.abilities.modeling.models.unet import UNet2d, UNet3d
from ai4e_core.abilities.modeling.modules.patch_embedding import PatchEmbedding, patch_centers
from ai4e_core.abilities.modeling.modules.patch_reconstruction import PatchReconstruction
from ai4e_core.abilities.modeling.modules.position_encoding import ContinuousSincosEmbed
from ai4e_core.abilities.modeling.modules.transformer import EncoderBlock
from ai4e_core.abilities.modeling.stages.transformer import TransformerEncoder


class AttentionBottleneck(nn.Module):
    """通道前空间特征→单位patch token→空间特征；不猜物理mask。"""

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        *,
        spatial_dim: int,
        dim: int = 64,
        num_heads: int = 4,
        num_layers: int = 2,
    ) -> None:
        super().__init__()
        if spatial_dim not in (2, 3) or num_layers < 1:
            raise ValueError("瓶颈维度或层数非法")
        patch = (1,) * spatial_dim
        self.spatial_dim = spatial_dim
        self.embedding = PatchEmbedding(in_channels, dim, patch)
        self.position = ContinuousSincosEmbed(dim, spatial_dim)
        self.encoder = TransformerEncoder(
            [
                EncoderBlock(dim, num_heads, feed_forward_dim=4 * dim, dropout=0.0)
                for _ in range(num_layers)
            ]
        )
        self.reconstruction = PatchReconstruction(dim, out_channels, patch)

    def forward(self, value: Tensor) -> Tensor:
        """保留各空间索引；此处有效性指内部特征，非来源流体mask。"""
        if value.ndim != self.spatial_dim + 2:
            raise ValueError("注意力瓶颈输入空间维度错误")
        tokens, ignored, info = self.embedding(value.movedim(1, -1))
        centers = patch_centers(info, device=tokens.device, dtype=tokens.dtype)
        tokens = self.encoder(
            tokens + self.position(centers).to(tokens.dtype), key_padding_mask=ignored
        )
        return self.reconstruction(tokens, info).movedim(-1, 1)


def build_model(model: dict) -> nn.Module:
    """构造二维/三维U-Net注意力瓶颈组合，保持通道前输入输出。"""
    spatial_dim = model.get("spatial_dims", 2)
    if spatial_dim not in (2, 3):
        raise ValueError("空间维度须为2/3")
    parameters = model.get("parameters", {})
    base, levels = parameters.get("base_channels", 8), parameters.get("levels", 3)
    constructor = UNet2d if spatial_dim == 2 else UNet3d
    network = constructor(
        model["in_channels"], model["out_channels"], base_channels=base, levels=levels
    )
    middle_width = base * 2 ** (levels - 1)
    middle = AttentionBottleneck(
        middle_width,
        2 * middle_width,
        spatial_dim=spatial_dim,
        dim=parameters.get("attention_dim", 64),
        num_heads=parameters.get("num_heads", 4),
        num_layers=parameters.get("attention_layers", 2),
    )
    return constructor(
        model["in_channels"],
        model["out_channels"],
        base_channels=base,
        levels=levels,
        encoder=network.encoder,
        bottleneck=middle,
        decoder=network.decoder,
        head=network.head,
    )
