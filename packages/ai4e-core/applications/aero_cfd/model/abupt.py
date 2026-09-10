"""按新模型声明设置贡献模型，不包含具体网络实现。"""


def build(factory, config: dict, *, batch_size: int = 1):
    """模型声明由 recipe 提供，固定布局批次数必须为正。"""
    if batch_size < 1:
        raise ValueError("批次必须为正")
    from ai4e_core.abilities.modeling.construction import construct

    return construct(factory, config)[0]
