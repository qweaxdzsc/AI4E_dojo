"""WDNO 原版切片的泄漏、冻结与漂移门禁。"""

import json

import pytest

from tools.verification.wdno.protocol import digest, validate_indices, verify, write_json


def test_trajectory_representatives_reject_leakage_and_duplicates():
    partitions = {
        "train": list(range(18000)),
        "validation": list(range(18000, 20000)),
        "test": list(range(4000)),
    }
    validate_indices(partitions)
    partitions["validation"][0] = 0
    with pytest.raises(ValueError, match="泄漏"):
        validate_indices(partitions)
    partitions["validation"] = list(range(18000, 20000))
    partitions["test"][-1] = 0
    with pytest.raises(ValueError, match="唯一"):
        validate_indices(partitions)


def test_frozen_source_and_test_selection_drift_rejected(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "model.py").write_text("value = 1\n")
    write_json(tmp_path / "source.json", {"files": {"model.py": digest(source / "model.py")}})
    write_json(tmp_path / "indices.json", {"test": [1, 2]})
    write_json(tmp_path / "protocol.json", {"indices_sha256": digest(tmp_path / "indices.json")})
    verify(tmp_path)
    (source / "model.py").write_text("value = 2\n")
    with pytest.raises(ValueError, match="源码"):
        verify(tmp_path)
    (source / "model.py").write_text("value = 1\n")
    write_json(tmp_path / "indices.json", {"test": [2, 3]})
    with pytest.raises(ValueError, match="名单"):
        verify(tmp_path)


def test_atomic_evidence_rejects_nonfinite(tmp_path):
    target = tmp_path / "report.json"
    write_json(target, {"completed": 2})
    with pytest.raises(ValueError):
        write_json(target, {"mse": float("nan")})
    assert json.loads(target.read_text()) == {"completed": 2}
