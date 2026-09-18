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


def test_resolve_paths_keeps_unsplit_partition_token(tmp_path):
    """unsplit 是分片模式名，不能按配置文件相对路径展开。"""
    import importlib

    module = importlib.import_module("ai4e_core.applications.aero_cfd.configuration")
    source = Path(__file__).resolve().parents[2] / (
        "packages/ai4e-core/applications/aero_cfd/configuration.py"
    )
    exec(compile(source.read_text(), str(source), "exec"), module.__dict__)
    resolve_paths = module.resolve_paths

    raw = tmp_path / "raw"
    data = tmp_path / "data"
    run = tmp_path / "run"
    recipe = tmp_path / "recipe"
    for path in (raw, data, run, recipe):
        path.mkdir()
    config_path = recipe / "config.yaml"
    config_path.write_text("dataset:\n  partition: unsplit\n")
    resolved = resolve_paths(
        {
            "data_root": str(data),
            "run_root": str(run),
            "dataset": {"root": str(raw), "partition": "unsplit"},
            "paths": {"datasets": {"root": str(data)}},
            "normalization": {"fields": {}},
        },
        config_path,
    )
    assert resolved["dataset"]["partition"] == "unsplit"


def test_unsplit_partition_flattens_official_groups(tmp_path):
    """平台原始处理 unsplit 只出一份训练宇宙，不按官方 train/test 落盘。"""
    import importlib

    adapter = importlib.import_module("ai4e_contrib.application.datasets.shapenet_car.adapter")
    source = Path(__file__).resolve().parents[2] / (
        "packages/ai4e-contrib/application/datasets/shapenet_car/adapter.py"
    )
    exec(compile(source.read_text(), str(source), "exec"), adapter.__dict__)
    splits = load_split_lists(PARTITION)
    data = adapter.open_dataset(
        root=tmp_path, samples="all", partition="unsplit", check_exists=False
    )
    assert set(data.partitions) == {"train"}
    assert "test" not in data.partitions and "eval" not in data.partitions
    assert list(data.partitions["train"]) == [
        *splits.get("train", ()),
        *splits.get("eval", ()),
        *splits.get("test", ()),
    ]


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
