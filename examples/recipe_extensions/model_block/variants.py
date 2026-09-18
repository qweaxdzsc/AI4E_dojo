"""AB-UPT 内部前馈激活变体；普通本地构造器，无框架注册。"""

import hashlib
from pathlib import Path

from torch import nn

from ai4e_contrib.ability.model.abupt import component as base
from ai4e_contrib.ability.model.abupt.model import construct as original

SOURCE = base.SOURCE + ":variants.silu:" + hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def __getattr__(name):
    """未修改的组件能力直接委托原公开组件，不复制数据/推理装配。"""
    return getattr(base, name)


def construct(**parameters):
    """构建原模型后替换物理块前馈激活，发生在优化器创建之前。"""
    model = original(**parameters)
    for block in model.blocks:
        block.mlp.act = nn.SiLU()
    return model


def describe(model):
    """形状不变也须区分算法身份；本地文件变化拒绝沿用旧恢复合同。"""
    return {**base.describe(model), "variant": SOURCE}


construct.describe = describe
