"""显式参考统计量与随包文件数值对照，不只做往返。"""

from pathlib import Path

import pytest
import torch
import yaml

from ai4e_contrib.application.datasets import shapenet_car
from ai4e_core.abilities.data.stats.load import load_statistics
from ai4e_core.applications.aero_cfd.trainprep.normalization import bind_normalization

STATS = Path(shapenet_car.MANIFEST_PATH).with_name("statistics.yaml")


def test_reference_statistics_match_shipped_file():
    shipped = load_statistics(STATS)
    raw = yaml.safe_load(STATS.read_text())
    for key in (
        "raw_pos_min",
        "raw_pos_max",
        "surface_pressure_mean",
        "surface_pressure_std",
        "volume_velocity_mean",
        "volume_velocity_std",
        "volume_sdf_mean",
        "volume_sdf_std",
    ):
        assert shipped[key] == raw[key]
    config = {
        "normalization": {
            "execute": True,
            "statistics": str(STATS),
            "fields": {
                "surface_pressure": {"method": "zscore"},
                "volume_velocity": {"method": "zscore"},
                "volume_sdf": {"method": "zscore"},
                "surface_position": {"method": "coordinate"},
                "volume_position": {"method": "coordinate"},
            },
        }
    }
    manifest = {"partitions": {"train": ["a"]}, "statistics": {"path": str(STATS)}}
    bound = bind_normalization(config, manifest)
    pressure = bound.record["fields"]["surface_pressure"]["parameters"]
    assert pressure["mean"] == raw["surface_pressure_mean"]
    assert pressure["std"] == raw["surface_pressure_std"]
    box = bound.record["fields"]["surface_position"]["parameters"]
    assert box["minimum"] == raw["raw_pos_min"]
    assert box["maximum"] == raw["raw_pos_max"]
    value = torch.tensor([[raw["surface_pressure_mean"][0]]], dtype=torch.float32)
    normalized = bound.transforms["surface_pressure"].apply(value)
    assert float(normalized) == pytest.approx(0.0, abs=1e-5)
    restored = bound.inverse("surface_pressure", normalized)
    torch.testing.assert_close(restored, value)
