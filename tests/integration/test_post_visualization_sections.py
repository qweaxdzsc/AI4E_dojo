"""切片、剖切和等值面的解析值与输入门禁。"""

import numpy as np
import pytest

from ai4e_core.abilities.postproc.visualization import clip_mesh, contour_mesh, slice_mesh
from tests.integration.test_post_visualization_fields import grid


def test_plane_and_clip_analytic():
    mesh = grid()
    mesh["original_point_id"] = np.arange(mesh.n_points)
    cut = slice_mesh(mesh, origin=[0.5, 0, 0], normal=[1, 0, 0])
    np.testing.assert_allclose(cut.points[:, 0], 0.5)
    np.testing.assert_allclose(cut.point_data["p"], cut.points @ [1.0, 2.0, 3.0])
    assert "original_point_id" not in cut.point_data
    for keep, expected in [("positive", "min"), ("negative", "max")]:
        result = clip_mesh(mesh, origin=[0.5, 0, 0], normal=[1, 0, 0], keep=keep)
        assert getattr(result.points[:, 0], expected)() == pytest.approx(0.5)
    with pytest.raises(ValueError):
        slice_mesh(mesh, origin=[2, 0, 0], normal=[1, 0, 0])
    with pytest.raises(ValueError):
        slice_mesh(mesh, origin=[0, 0, 0], normal=[0, 0, 0])


def test_contours_and_dimension_gate():
    mesh = grid()
    surface = contour_mesh(mesh, field="p", values=[3.0])
    np.testing.assert_allclose(surface.points @ [1.0, 2.0, 3.0], 3.0, atol=1e-6)
    section = slice_mesh(mesh, origin=[0.5, 0, 0], normal=[1, 0, 0])
    line = contour_mesh(section, field="p", values=[3.0], kind="contour")
    assert line.n_cells > 0
    with pytest.raises(ValueError):
        contour_mesh(section, field="p", values=[3.0])
    with pytest.raises(ValueError):
        contour_mesh(mesh, field="p", values=[42.0], association="cell")
