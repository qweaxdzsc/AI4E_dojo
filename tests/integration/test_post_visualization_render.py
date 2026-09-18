"""真实离屏渲染的视角、色带、尺寸及剖面缺失段。"""

import numpy as np

from ai4e_core.abilities.postproc.visualization import render_field, render_profile, sample_line
from ai4e_core.applications.aero_cfd.post import bind_mesh, read_fields
from ai4e_core.applications.aero_cfd.post.field_rendering import render_field as render_bound
from tests.integration.test_post_visualization_fields import field_sample, grid


def test_camera_color_and_dimensions_change_pixels():
    mesh = grid()
    before = mesh.point_data["p"].copy()
    first = render_field(mesh, field="p", size=(320, 240))
    second = render_field(mesh, field="p", size=(320, 240), camera="xy", cmap="magma", opacity=0.5)
    assert first.shape == second.shape == (240, 320, 3)
    assert first.std() > 10 and np.mean(np.abs(first.astype(float) - second)) > 5
    np.testing.assert_array_equal(before, mesh.point_data["p"])


def test_prediction_truth_share_range_and_camera():
    mesh = bind_mesh(read_fields(field_sample()), domain="volume")
    p = render_bound(
        mesh, field="volume:velocity:prediction", component="magnitude", size=(320, 240)
    )
    t = render_bound(mesh, field="volume:velocity:truth", component="magnitude", size=(320, 240))
    assert p["parameters"]["clim"] == t["parameters"]["clim"]
    assert p["parameters"]["camera"] == t["parameters"]["camera"]


def test_curve_image_retains_invalid_profile():
    profile = sample_line(grid(), start=[-0.5, 0.5, 0.5], end=[1.5, 0.5, 0.5], fields=["p"])
    pixels = render_profile(profile, field="p", size=(320, 240))
    assert pixels.shape == (240, 320, 4) and pixels.std() > 10
    assert not profile["valid"][0]


def test_vector_profile_requires_explicit_component():
    import pytest

    profile = sample_line(grid(), start=[0, 0.5, 0.5], end=[1, 0.5, 0.5], fields=["U"])
    with pytest.raises(ValueError, match="显式选择"):
        render_profile(profile, field="U")
