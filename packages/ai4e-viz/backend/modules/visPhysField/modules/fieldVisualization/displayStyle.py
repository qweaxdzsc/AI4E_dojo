"""透明度、面/网格模式、光照和阴影业务规则。"""

from dataclasses import dataclass


@dataclass(frozen=True)
class DisplayStyle:
    """不依赖VTK对象的物理场显示样式。"""

    representation: str = "surface"
    opacity: float = 1.0
    lighting: bool = True
    shadow: bool = False


def validate_display_style(style: DisplayStyle) -> DisplayStyle:
    """校验显示模式和透明度范围。"""

    if style.representation not in {"surface", "wireframe", "surface_with_edges"}:
        raise ValueError("未知显示模式")
    if not 0 <= style.opacity <= 1:
        raise ValueError("透明度必须位于0到1")
    return style
