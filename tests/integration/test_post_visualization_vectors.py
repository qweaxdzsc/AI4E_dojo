"""恒定矢量场上的箭头方向、流线轨迹与种子可重复性。"""

import numpy as np
import pytest

from ai4e_core.abilities.postproc.visualization import glyph_mesh, seed_points, streamline_mesh
from tests.integration.test_post_visualization_fields import grid


def test_glyph_preserves_named_vector():
    mesh = grid()
    result = glyph_mesh(mesh, field="U", stride=100)
    assert result.n_points > 0
    np.testing.assert_allclose(result["U"], np.tile([1.0, 0.0, 0.0], (result.n_points, 1)))
    assert mesh.n_points == 1331


def test_straight_streamlines_and_seeds():
    mesh = grid()
    result = streamline_mesh(
        mesh,
        field="U",
        seeds={"kind": "points", "points": [[0.1, 0.5, 0.5]]},
        direction="forward",
        length=0.4,
    )
    assert result.n_cells == 1
    np.testing.assert_allclose(result.points[:, 1:], 0.5)
    assert result.points[-1, 0] == pytest.approx(0.5, abs=0.03)
    for kind in ("sphere", "plane"):
        a = seed_points(kind=kind, center=[0.5] * 3, count=9)
        b = seed_points(kind=kind, center=[0.5] * 3, count=9)
        np.testing.assert_array_equal(a.points, b.points)
    with pytest.raises(ValueError):
        streamline_mesh(
            mesh.extract_surface(), field="U", seeds={"kind": "points", "points": [[0.1, 0.5, 0.5]]}
        )
