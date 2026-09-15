"""标量云图、层数、范围和调用配置业务规则。"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ScalarCloudOptions:
    """云图业务配置；颜色表的渲染实现由一级Trame适配器完成。"""

    field_name: str
    levels: int = 16
    value_range: tuple[float, float] | None = None


def validate_scalar_cloud(options: ScalarCloudOptions) -> ScalarCloudOptions:
    """校验云图字段、色阶和可选数值范围。"""

    if not options.field_name.strip():
        raise ValueError("云图字段不能为空")
    if options.levels < 2:
        raise ValueError("云图层数不能少于2")
    if options.value_range and options.value_range[0] > options.value_range[1]:
        raise ValueError("云图范围下界不能大于上界")
    return options


def prepare_scalar(mesh, field: dict):
    """物理场云图选取显式归属、分量或模长。"""
    from modules.visEngine import scalar_mesh
    return scalar_mesh(mesh, field)
