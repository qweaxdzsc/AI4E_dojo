"""几何派生：点到最近顶点、点到网格表面、表面法向与公共表面门禁。"""

from ai4e_core.abilities.geometry.mesh_sdf import mesh_signed_distance
from ai4e_core.abilities.geometry.nearest import nearest_vertex_distance_and_direction
from ai4e_core.abilities.geometry.surface import require_surface_mesh
from ai4e_core.abilities.geometry.surface_normals import (
    surface_point_normals,
    surface_point_normals_with_mask,
)

__all__ = [
    "mesh_signed_distance",
    "nearest_vertex_distance_and_direction",
    "require_surface_mesh",
    "surface_point_normals",
    "surface_point_normals_with_mask",
]
