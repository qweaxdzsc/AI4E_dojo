"""纯可视化内核公开门面。

本模块没有Router、URL、Server、Repository和业务配置。
"""

from .cache import KernelCache
from .performance import evenly_spaced_indices
from .physicalField import scalar_range

__all__ = ["KernelCache", "evenly_spaced_indices", "scalar_range"]

from .filters import apply_filter, field_array, scalar_mesh, streamline_style, style_streamline_mesh
from .sampling import probe, entity, sample_line
from .renderPasses import apply_paraview_light_kit, enable_shadows, paraview_light_kit_defaults
from .sampling import pick_ray
from .cache import reuse_geometry
from .seeds import (
    build_seed_source,
    extract_named_region,
    is_surface_mesh,
    list_named_regions,
    project_surface_vectors,
    seed_defaults,
    seed_preview_mesh,
    seed_type,
    snap_seed_points,
)
from .planeWidget import (
    HANDLE_COLORS,
    align_plane_normal,
    move_plane,
    pick_plane_handle,
    plane_widget_geometry,
)
from .seedWidget import move_seed, seed_widget_geometry
from .lineWidget import line_widget_geometry, move_line, pick_line_handle
