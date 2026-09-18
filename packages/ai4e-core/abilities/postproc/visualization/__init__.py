"""脚本三维分析能力；导入门面不加载 PyVista 或创建渲染窗口。"""

from .fields import field_values, scalar_mesh
from .probe import probe_points, sample_line
from .render import render_field, render_profile
from .sections import clip_mesh, contour_mesh, slice_mesh
from .vectors import glyph_mesh, seed_points, streamline_mesh

__all__ = [
    "clip_mesh",
    "contour_mesh",
    "field_values",
    "glyph_mesh",
    "probe_points",
    "render_field",
    "render_profile",
    "sample_line",
    "scalar_mesh",
    "seed_points",
    "slice_mesh",
    "streamline_mesh",
]
