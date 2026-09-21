"""PCNO 圆柱方法变体构造，计算实现位于 core；不改地热入口。"""
from ai4e_core.abilities.modeling.models.fourier_unet3d import FourierUNet3d


def build_model(*, branch="fluid", case="double_cylinder", **kwargs):
    """绑定已知历史字段与预测分支，不填充缺失的物性参数。"""
    if case == "double_cylinder" and branch in ("fluid","structure"):
        return FourierUNet3d(in_channels=4,out_channels=3 if branch == "fluid" else 1,**kwargs)
    if case == "cylinder_flow" and branch == "fluid":
        # 速度2、节点类别one-hot9、几何有效域1；坐标由核心网络显式加入。
        return FourierUNet3d(in_channels=12,out_channels=2,**kwargs)
    raise ValueError("不支持的圆柱案例或分支")
