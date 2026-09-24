"""显式谱计算块序列；网络阶段不认识业务阶段或数据集。"""

from ai4e_core.abilities.modeling.stages.convolution import ConvStage


class FourierStage(ConvStage):
    """复用现有注册与顺序调用机制；最后一块的激活由该块自身决定。"""
