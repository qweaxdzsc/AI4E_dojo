"""几何可视化模块的视角状态和 O3DV 表现命名测试。"""

import pytest

from modules.visGeometry import GeometryViewState, normalize_geometry_view
from modules.visGeometry.o3dv import representation_name


def test_geometry_view_normalizes_duplicate_node_ids() -> None:
    """视角状态应去重并保持节点原始顺序。"""

    normalized = normalize_geometry_view(GeometryViewState(
        projection="orthographic",
        selected_node_ids=("blade", "hub", "blade"),
        hidden_node_ids=("shell", "shell"),
    ))
    assert normalized.selected_node_ids == ("blade", "hub")
    assert normalized.hidden_node_ids == ("shell",)
    assert representation_name("wing.surface.ply") == "wing.surface.glb"


def test_geometry_view_rejects_unknown_projection() -> None:
    """模块必须拒绝 O3DV 无法解释的投影类型。"""

    with pytest.raises(ValueError):
        normalize_geometry_view(GeometryViewState(projection="fisheye"))
