"""按显式次序组合卷积或残差块；不是业务运行阶段。"""

from collections.abc import Sequence

from torch import Tensor, nn


class ConvStage(nn.Module):
    """有序特征块序列，所有子块均被PyTorch注册。"""

    def __init__(self, blocks: Sequence[nn.Module]) -> None:
        super().__init__()
        if not blocks or any(not isinstance(block, nn.Module) for block in blocks):
            raise ValueError("阶段需要非空网络块列表")
        self.blocks = nn.ModuleList(blocks)

    def forward(self, value: Tensor) -> Tensor:
        """按构造顺序调用，每个块独立承担其张量约定。"""
        for block in self.blocks:
            value = block(value)
        return value


class ResidualStage(ConvStage):
    """显式残差块序列；保留每块自己的主支、捷径和状态。"""
