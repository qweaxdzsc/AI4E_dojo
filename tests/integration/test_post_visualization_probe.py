"""剖面解析值与域外采样的缺失语义。"""

import numpy as np

from ai4e_core.abilities.postproc.visualization import probe_points, sample_line
from tests.integration.test_post_visualization_fields import grid


def test_line_values_distance_and_invalid_samples():
    profile = sample_line(
        grid(), start=[-0.5, 0.5, 0.5], end=[1.5, 0.5, 0.5], count=21, fields=["p"]
    )
    valid = profile["valid"]
    assert not valid[0] and not valid[-1] and valid.sum() == 11
    np.testing.assert_allclose(
        profile["fields"]["p"][valid], profile["positions"][valid, 0] + 2.5, atol=1e-6
    )
    np.testing.assert_allclose(profile["distance"], np.linspace(0, 2, 21))


def test_cell_probe_does_not_choose_same_named_point_field():
    result = probe_points(grid(), positions=[[0.5] * 3], fields=["p"], association="cell")
    assert result["fields"]["p"][0] == 42.0


def test_application_probe_statistics_preserves_excluded_points():
    from ai4e_core.applications.aero_cfd import post
    from tests.integration.test_post_visualization_fields import field_sample

    mesh = post.bind_mesh(post.read_fields(field_sample()), domain="volume")
    probe = post.probe_field(
        mesh, fields=["volume:velocity:prediction"], positions=[[-1, 0.5, 0.5], [0.5, 0.5, 0.5]]
    )
    stats = post.region_statistics(probe, field="volume:velocity:prediction", component="magnitude")
    assert stats["count"] == stats["excluded"] == 1
    assert stats["mean"] == 1.0 and stats["region"] == "probe"
