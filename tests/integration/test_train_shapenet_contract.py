"""ShapeNet 契约：官方人数、压力一通道、速度三通道、排除字段不读。"""

from pathlib import Path

import pytest
import torch

from ai4e_core.abilities.data.source.split import load_split_expected, load_split_lists
from ai4e_core.applications.aero_cfd.trainprep.dataset import (
    DEFAULT_SPLIT_COUNTS,
    open_preprocessed_sample,
)
from tests.integration.test_train_dataset_read import (
    DISK_KEYS,
    FILEMAP,
    FORBIDDEN_KEYS,
    _write_sample,
)

PARTITION = (
    Path(__file__).resolve().parents[2]
    / "packages/ai4e-contrib/application/datasets/shapenet_car/partition.yaml"
)


def test_official_counts_and_declared_field_shapes(tmp_path):
    splits = load_split_lists(PARTITION)
    expected = load_split_expected(PARTITION)
    assert expected == DEFAULT_SPLIT_COUNTS
    assert len(splits["train"]) == 789 and len(splits["test"]) == 100
    sample = tmp_path / "sample"
    _write_sample(sample)
    (sample / "friction.pt").write_bytes(b"no")
    fields = open_preprocessed_sample(sample, FILEMAP)
    assert fields["surface_pressure"].shape[-1:] == (1,)
    assert fields["volume_velocity"].shape[-1:] == (3,)
    assert fields["surface_position"].shape[-1] == 3
    assert set(DISK_KEYS).issubset(fields)
    assert all(name not in fields for name in FORBIDDEN_KEYS)


def test_excluded_missing_fields_are_not_accessed(tmp_path):
    sample = tmp_path / "sample"
    _write_sample(sample)
    fields = open_preprocessed_sample(sample, FILEMAP)
    assert "friction" not in fields and "area" not in fields
    with pytest.raises(RuntimeError):
        open_preprocessed_sample(sample, {**FILEMAP, "surface_pressure": "missing.pt"})
    assert torch.isfinite(fields["surface_pressure"]).all()
