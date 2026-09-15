"""STEP、STL、DXF、CSV/JSON和GLB转换用例入口。

当前产品已经稳定使用的是VTK兼容几何到GLB的转换，因此先通过兼容适配器公开该能力；
Excel中尚未实现的转换能力不会在目录重构阶段伪造。
"""

from .converter import convert_to_glb as _convert_to_glb


def convert_to_glb(source_path: str, output_path: str) -> str:
    """把现有VTK可读几何转换为O3DV消费的GLB文件。"""

    return _convert_to_glb(source_path, output_path)
