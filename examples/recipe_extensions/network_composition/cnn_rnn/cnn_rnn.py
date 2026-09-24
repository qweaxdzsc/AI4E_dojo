"""用户示例：逐帧共享空间编码，逐空间位置显式循环，预测下一帧。"""

from torch import Tensor, nn

from ai4e_core.abilities.modeling.modules.convolution import ConvBlock2d
from ai4e_core.abilities.modeling.stages.convolution import ConvStage
from ai4e_core.abilities.modeling.stages.recurrent import RecurrentStage


class CNNRNN(nn.Module):
    """输入[B,T,H,W,C]；空间点进入循环批轴，时间始终为T。"""

    def __init__(
        self,
        in_channels: int = 4,
        out_channels: int = 4,
        spatial_channels: int = 16,
        hidden_size: int = 32,
        num_layers: int = 2,
    ) -> None:
        super().__init__()
        self.in_channels = in_channels
        self.spatial = ConvStage(
            [
                ConvBlock2d(in_channels, spatial_channels),
                ConvBlock2d(spatial_channels, spatial_channels),
            ]
        )
        self.recurrent = RecurrentStage(spatial_channels, hidden_size, num_layers)
        self.head = nn.Linear(hidden_size, out_channels)

    def forward_with_state(
        self, value: Tensor, state: Tensor | None = None
    ) -> tuple[Tensor, Tensor]:
        """返回[B,H,W,Cout]与[L,B*H*W,Hid]；续接须保持原空间身份。"""
        if value.ndim != 5 or value.shape[-1] != self.in_channels or min(value.shape[:4]) < 1:
            raise ValueError("CNN-RNN输入须为非空[B,T,H,W,C]")
        batch, time, height, width, channels = value.shape
        frames = value.reshape(batch * time, height, width, channels).movedim(-1, 1)
        encoded = self.spatial(frames).movedim(1, -1).reshape(batch, time, height, width, -1)
        series = encoded.permute(0, 2, 3, 1, 4).reshape(batch * height * width, time, -1)
        sequence, next_state = self.recurrent(series, state)
        return self.head(sequence[:, -1]).reshape(batch, height, width, -1), next_state

    def forward(self, value: Tensor) -> Tensor:
        """每次默认从零状态开始，不跨样本保存隐式状态。"""
        prediction, _ = self.forward_with_state(value)
        return prediction


def build_model(model: dict) -> nn.Module:
    """按明确字段创建空间循环组合，四物理通道为默认。"""
    parameters = model.get("parameters", {})
    return CNNRNN(
        in_channels=model.get("in_channels", 4),
        out_channels=model.get("out_channels", 4),
        spatial_channels=parameters.get("spatial_channels", 16),
        hidden_size=parameters.get("hidden_size", 32),
        num_layers=parameters.get("num_layers", 2),
    )
