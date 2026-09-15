"""数据准备重划 train/test/eval：全部已处理样本入池，不改张量。"""

import json

import pytest
import torch

from ai4e_core.abilities.data.save.store import write_tensor_file
from ai4e_core.abilities.data.source.manifest import ManifestIndex
from ai4e_core.abilities.data.source.split import (
    default_counts,
    flatten_samples,
    resolve_split,
)
from ai4e_core.applications.aero_cfd.trainprep.preparation import open_dataset


def write_physical_manifest(root, partitions):
    """写出最小物理清单，每个样本一个坐标张量。"""
    samples = []
    for partition, names in partitions.items():
        for name in names:
            directory = root / name
            directory.mkdir()
            tensor = torch.zeros(2, 3)
            write_tensor_file(directory / "pos.pt", tensor)
            samples.append(
                {
                    "partition": partition,
                    "sample": name,
                    "written": True,
                    "path": name,
                    "filemap": {"pos": "pos.pt"},
                    "fields": {
                        "pos": {
                            "state": "physical",
                            "shape": [2, 3],
                            "dtype": str(tensor.dtype),
                        }
                    },
                }
            )
    path = root / "manifest.json"
    path.write_text(
        json.dumps(
            {
                "version": 1,
                "state": "physical",
                "partitions": partitions,
                "samples": samples,
            }
        )
    )
    return path


def test_default_counts_use_original_lengths_and_zero_missing():
    partitions = {"train": ["a", "b"], "test": ["c"]}
    assert flatten_samples(partitions) == ["a", "b", "c"]
    assert default_counts(partitions) == {"train": 2, "test": 1, "eval": 0}
    assert default_counts({"train": ["a"]}) == {"train": 1, "test": 0, "eval": 0}


def test_random_split_is_reproducible_and_original_keeps_members():
    partitions = {"train": ["a", "b"], "test": ["c"]}
    first = resolve_split(
        partitions, {"method": "random", "seed": 0, "counts": {"train": 2, "test": 0, "eval": 1}}
    )
    second = resolve_split(
        partitions, {"method": "random", "seed": 0, "counts": {"train": 2, "test": 0, "eval": 1}}
    )
    assert first == second
    assert len(first["train"]) == 2
    assert "test" not in first
    assert len(first["eval"]) == 1
    assert set(first["train"] + first["eval"]) == {"a", "b", "c"}
    kept = resolve_split(partitions, {"method": "original"})
    assert kept == {"train": ["a", "b"], "test": ["c"]}
    scoped = resolve_split(
        partitions,
        {"method": "original", "samples": ["a", "c"]},
    )
    assert scoped == {"train": ["a"], "test": ["c"]}
    drawn = resolve_split(
        partitions,
        {"method": "random", "seed": 0, "samples": ["b", "c"], "counts": {"train": 2, "test": 0, "eval": 0}},
    )
    assert set(drawn["train"]) == {"b", "c"}
    with pytest.raises(ValueError, match="指定样本不在当前清单"):
        resolve_split(partitions, {"method": "original", "samples": ["missing"]})


def test_random_split_rejects_sum_mismatch_and_empty_train():
    partitions = {"train": ["a", "b"], "test": ["c"]}
    with pytest.raises(ValueError, match="之和必须等于全部样本"):
        resolve_split(
            partitions, {"method": "random", "seed": 0, "counts": {"train": 1, "test": 1, "eval": 0}}
        )
    with pytest.raises(ValueError, match="训练分片至少需要 1"):
        resolve_split(
            partitions, {"method": "random", "seed": 0, "counts": {"train": 0, "test": 3, "eval": 0}}
        )


def test_manifest_overlay_can_read_remapped_sample(tmp_path):
    path = write_physical_manifest(tmp_path, {"train": ["car-a", "car-b"]})
    index = ManifestIndex(path)
    index.remap_partitions({"train": ["car-b"], "test": ["car-a"]})
    assert index.partitions == {"train": ["car-b"], "test": ["car-a"]}
    moved = index.read("test", 0, fields=["pos"])
    assert list(moved["pos"].shape) == [2, 3]
    kept = index.read("train", 0, fields=["pos"])
    assert list(kept["pos"].shape) == [2, 3]


def test_open_dataset_allows_train_only_manifest(tmp_path):
    path = write_physical_manifest(tmp_path, {"train": ["only"]})
    data = open_dataset({"train": {"manifest": str(path), "evaluation_split": "test"}, "trainprep": {}})
    assert list(data.index.partitions["train"]) == ["only"]
    assert "test" not in data.index.partitions


def test_open_dataset_applies_random_split(tmp_path):
    path = write_physical_manifest(tmp_path, {"train": ["a", "b"], "test": ["c"]})
    data = open_dataset(
        {
            "train": {"manifest": str(path)},
            "trainprep": {
                "split": {"method": "random", "seed": 0, "counts": {"train": 2, "test": 0, "eval": 1}}
            },
        }
    )
    assert len(data.index.partitions["train"]) == 2
    assert "test" not in data.index.partitions
    assert len(data.index.partitions["eval"]) == 1
    data.index.read("eval", 0, fields=["pos"])


def test_open_dataset_overlay_uses_stored_partitions(tmp_path):
    path = write_physical_manifest(tmp_path, {"train": ["a", "b"]})
    data = open_dataset(
        {
            "train": {"manifest": str(path)},
            "trainprep": {
                "split": {"method": "random", "seed": 0, "counts": {"train": 1, "test": 1, "eval": 0}}
            },
        },
        overlay={"train": ["b"], "eval": ["a"]},
    )
    assert data.index.partitions == {"train": ["b"], "eval": ["a"]}
    data.index.read("eval", 0, fields=["pos"])


def test_open_dataset_rejects_empty_train_split(tmp_path):
    path = write_physical_manifest(tmp_path, {"train": ["a"], "test": ["b"]})
    with pytest.raises(ValueError, match="训练分片"):
        open_dataset(
            {
                "train": {"manifest": str(path)},
                "trainprep": {
                    "split": {
                        "method": "random",
                        "seed": 0,
                        "counts": {"train": 0, "test": 2, "eval": 0},
                    }
                },
            }
        )
