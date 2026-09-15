"""矢量箭头、流线密度和缩放业务规则。"""

from dataclasses import dataclass


@dataclass(frozen=True)
class VectorFieldOptions:
    """矢量场展示参数，字段分量语义由数据画像提供。"""

    field_name: str
    scale: float = 1.0
    density: float = 1.0


def validate_vector_field(options: VectorFieldOptions) -> VectorFieldOptions:
    """校验矢量缩放和密度，避免生成无意义或过载的Glyph。"""

    if not options.field_name.strip() or options.scale <= 0 or options.density <= 0:
        raise ValueError("矢量字段不能为空，缩放和密度必须大于零")
    return options


def execute_vector(mesh, node: dict):
    """将矢量显示业务参数交付真实 VTK 内核。"""
    from modules.visEngine import apply_filter
    params = node.get('parameters', {})
    validate_vector_field(VectorFieldOptions(params['field']['name'], scale=float(params.get('scale', .1))))
    return apply_filter(mesh, node)
