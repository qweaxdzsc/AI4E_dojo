"""具名准备统计和轨迹布局不绑定 GeoTransolver。"""

import numpy as np
import torch

from ai4e_core.abilities.transform.field_encoding import (
    position_statistics,
)
from ai4e_core.abilities.transform.trajectory import flatten_trajectory, restore_trajectory


def test_statistics_match_reference_order():
    rng = np.random.default_rng(1)
    x = rng.normal(size=(5, 11, 13, 3)).astype("float32")
    stats = position_statistics({"x": x}, name="x")["x"]
    mean = torch.zeros(3)
    square = torch.zeros(3)
    for sample in torch.from_numpy(x):
        mean += sample.mean((0, 1)) / 5
        square += (sample * sample).mean((0, 1)) / 5
    np.testing.assert_array_equal(stats["mean"], mean.numpy())
    np.testing.assert_array_equal(
        stats["std"], (torch.sqrt(torch.clamp(square - mean * mean, min=0) + 1e-8) + 1e-8).numpy()
    )


def test_trajectory_roundtrip_and_initial_add():
    x = torch.randn(2, 10, 7, 5)
    torch.testing.assert_close(restore_trajectory(flatten_trajectory(x), 10, 5), x)
    initial = torch.randn(2, 7, 3)
    result = restore_trajectory(torch.zeros(2, 7, 50), 10, 5, initial=initial, initial_channels=3)
    torch.testing.assert_close(result[..., :3], initial[:, None].expand(-1, 10, -1, -1))


def test_failed_mesh_prediction_never_publishes_complete_manifest(tmp_path, monkeypatch):
    import json

    from ai4e_core.abilities.data.save import vtkhdf
    from ai4e_core.abilities.data.save.array_manifest import save_arrays
    from ai4e_core.abilities.sampling.structured_grid import grid_faces
    from ai4e_core.applications.parametric_pde.infer import predict_fields

    data = {
        "target": np.ones((2, 4, 1), dtype="float32"),
        "physical_target": np.ones((2, 1, 4, 1), dtype="float32"),
        "coordinates": np.zeros((2, 4, 2), dtype="float32"),
        "faces": np.tile(grid_faces((2, 2)), (2, 1)),
        "entity_ids": np.tile(np.arange(4), (2, 1)),
    }
    prepared = tmp_path / "prepared"
    prepared.mkdir()
    save_arrays(prepared / "test", data, kind="named-field-inputs-v1", metadata={"ids": ["a", "b"]})
    index = prepared / "manifest.json"
    index.write_text(
        json.dumps({"kind": "named-field-preparation-v1", "splits": {"test": "test/manifest.json"}})
    )
    model = torch.nn.Identity()

    def broken(*args, **kwargs):
        raise RuntimeError("mesh failed")

    monkeypatch.setattr(vtkhdf, "write_vtkhdf", broken)
    import pytest

    with pytest.raises(RuntimeError, match="mesh failed"):
        predict_fields(
            model,
            index,
            tmp_path / "fixed",
            split="test",
            batch=lambda ids: {"input": torch.ones(len(ids), 4, 1)},
            input_names=("input",),
            decode=lambda raw, item: raw[:, None],
            batch_size=1,
            fields=["u"],
            units=["1"],
            times=[0],
            provenance={},
        )
    assert not (tmp_path / "fixed/manifest.json").exists()
    assert (tmp_path / "fixed/manifest.pending.json").exists()
