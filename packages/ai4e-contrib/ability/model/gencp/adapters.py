"""GenCP 两种网络的显式构造，允许研究者替换普通构造函数。"""


def construct(settings):
    """根据已展开参数构造原网络，参数不在 core 解释。"""
    options = dict(settings)
    backbone = options.pop("backbone")
    if backbone == "cno":
        from .cno import CNO3d

        return CNO3d(**options)
    if backbone == "sit_fno":
        from .sit_fno import SiT_FNO

        return SiT_FNO(**options)
    raise ValueError(f"未知 GenCP 骨干 {backbone}")
