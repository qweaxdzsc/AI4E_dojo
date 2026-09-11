"""物理 PT 交接：值、行身份和样本条件保持独立。"""

import json

import pytest
import torch

from ai4e_core.abilities.data.save.store import write_named_tensors
from ai4e_core.abilities.data.source.physical import PhysicalView


def physical_fixture(tmp_path):
    """写两份不等点数样本，以检出把条件误按点累计的实现。"""
    records = []
    layout = {
        "domains": {"surface": {"position": "pos", "fields": {"p": "p"}, "ids": "ids"}},
        "conditions": {"condition": 1},
    }
    for i, count in enumerate((4, 8)):
        fields = {
            "pos": torch.arange(count * 3).reshape(count, 3).float(),
            "p": torch.arange(count).float() + i,
            "ids": torch.arange(count),
            "condition": torch.tensor([[float(i * 2)]]),
        }
        filemap = {k: k + ".pt" for k in fields}
        write_named_tensors(tmp_path / str(i), fields, filemap)
        records.append(
            {
                "sample": str(i),
                "partition": "train",
                "path": str(i),
                "written": True,
                "filemap": filemap,
                "fields": {
                    k: {"shape": list(v.shape), "dtype": str(v.dtype), "state": "physical"}
                    for k, v in fields.items()
                },
            }
        )
    manifest = {
        "version": 1,
        "state": "physical",
        "partitions": {"train": ["0", "1"]},
        "samples": records,
        "physical_layout": layout,
    }
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest))
    return PhysicalView(path)


def test_roundtrip_and_conditions(tmp_path):
    view = physical_fixture(tmp_path)
    sample = view.read("train")
    assert sample["fields"]["p"].shape == (4, 1)
    assert sample["conditions"]["condition"].shape == (1, 1)
    assert sample["domains"]["surface"]["identity_basis"] == "source"
    original = view.content_digest()
    sample["fields"]["p"].zero_()
    assert view.content_digest() == original
    assert view.read("train")["fields"]["p"].sum() == 6


def test_condition_statistics_are_per_sample(tmp_path):
    from ai4e_core.abilities.data.stats.physical import freeze

    view = physical_fixture(tmp_path)
    norm = freeze(
        view,
        {
            "normalization": {
                "execute": True,
                "fields": {
                    "condition": {"method": "zscore", "scope": "condition"},
                    "p": {"method": "zscore"},
                    "pos": {"method": "identity"},
                },
            }
        },
    )
    assert norm.record["fields"]["condition"]["parameters"] == {"mean": [1.0], "std": [1.0]}


def test_missing_field_and_duplicate_ids(tmp_path):
    view = physical_fixture(tmp_path)
    torch.save(torch.tensor([0, 0, 2, 3]), tmp_path / "0/ids.pt")
    with pytest.raises(ValueError, match="train/0/surface"):
        view.read("train")
    path = tmp_path / "manifest.json"
    manifest = json.loads(path.read_text())
    manifest["physical_layout"]["domains"]["surface"]["position"] = "missing"
    path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="train/0/missing"):
        PhysicalView(path).read("train")
