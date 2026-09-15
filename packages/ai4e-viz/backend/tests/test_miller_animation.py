from pathlib import Path

import numpy as np
from vtk.util import numpy_support

from modules.visPhysField.modules.fieldVisualization.timelineAnimation import MillerFieldAnimation


def test_miller_temporal_field_updates_scalars_without_rebuilding_topology():
    source = Path(__file__).resolve().parents[2] / "resources" / "examples" / "miller_tokamak_timeseries_240frames.npz"
    animation = MillerFieldAnimation(source)
    points = animation.surface.GetPoints()
    scalars = animation.scalars
    before = numpy_support.vtk_to_numpy(scalars).copy()

    metadata = animation.set_frame(0)
    after = numpy_support.vtk_to_numpy(animation.scalars)

    assert animation.frame_count == 240
    assert animation.frames.shape == (240, 148, 176)
    assert animation.surface.GetPoints() is points
    assert animation.scalars is scalars
    assert metadata["index"] == 0
    assert not np.allclose(before, after)
    assert tuple(animation.global_range) == (float(animation.frames.min()), float(animation.frames.max()))
