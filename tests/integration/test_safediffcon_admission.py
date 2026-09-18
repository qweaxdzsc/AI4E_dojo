"""参考准入工具的真实文件验证：拒绝损坏数据、冲突副本和覆盖原始证据。"""

import json
import subprocess
import zipfile

import h5py
import numpy as np
import pyarrow as pa
import pytest
from pyarrow import ipc

from tools.verification.safediffcon.admission import (
    arrow_sources,
    audit_burgers,
    audit_tokamak,
    capture_source,
    digest_file,
)


def burgers_files(root, *, nonfinite=False):
    for split in ("train", "cal", "test"):
        with h5py.File(root / f"burgers_{split}.h5", "w") as stream:
            group = stream.create_group(split)
            state = np.zeros((2, 11, 128), dtype=np.float32)
            state[1, 3, 6] = np.nan if nonfinite else 0.81
            group["pde_11-128"] = state
            group["pde_11-128_f"] = np.zeros((2, 10, 128), dtype=np.float32)


def test_burgers_scans_values_without_modifying_source(tmp_path):
    burgers_files(tmp_path)
    before = {p.name: digest_file(p) for p in tmp_path.iterdir()}
    result = audit_burgers(tmp_path, counts={"train": 2, "cal": 2, "test": 2})
    assert result["splits"]["train"]["unsafe_samples"] == 1
    assert before == {p.name: digest_file(p) for p in tmp_path.iterdir()}


def test_burgers_rejects_bad_values_and_wrong_count(tmp_path):
    burgers_files(tmp_path, nonfinite=True)
    with pytest.raises(ValueError, match="非有限"):
        audit_burgers(tmp_path, counts={"train": 2})
    with pytest.raises(ValueError, match="形状"):
        audit_burgers(tmp_path)


def arrow_bytes(*, count=3, action_shape=(121, 9)):
    states = np.ones((122, 8))
    states[:, 4] = 5.0
    rows = [
        {
            "outputs": states.tolist(),
            "actions": np.zeros(action_shape).tolist(),
            "targets": np.zeros((122, 3)).tolist(),
        }
        for _ in range(count)
    ]
    table = pa.Table.from_pylist(rows)
    sink = pa.BufferOutputStream()
    with ipc.new_stream(sink, table.schema) as writer:
        writer.write_table(table)
    return sink.getvalue().to_pybytes()


def test_arrow_zip_and_plain_copies_and_target_semantics(tmp_path):
    name = "data-00000-of-00001.arrow"
    content = arrow_bytes()
    (tmp_path / name).write_bytes(content)
    with zipfile.ZipFile(tmp_path / "download.zip", "w") as bundle:
        bundle.writestr("Tokamak/tokamak_dataset/" + name, content)
    result = audit_tokamak(tmp_path, counts=(1, 1, 1), shards=1)
    assert len(result["sources"][0]["copies"]) == 2
    assert result["splits"]["test"]["outputs_vs_targets_objective"] == 2
    assert result["splits"]["train"]["unsafe_samples"] == 0
    assert result["target_semantics"].startswith("unresolved")


def test_arrow_rejects_missing_conflicting_and_wrong_shape(tmp_path):
    with pytest.raises(FileNotFoundError, match="缺失"):
        arrow_sources(tmp_path)
    name = "data-00000-of-00001.arrow"
    (tmp_path / name).write_bytes(arrow_bytes(action_shape=(120, 9)))
    with pytest.raises(ValueError, match="形状"):
        audit_tokamak(tmp_path, counts=(1, 1, 1), shards=1)
    with zipfile.ZipFile(tmp_path / "download.zip", "w") as bundle:
        bundle.writestr(name, arrow_bytes())
    with pytest.raises(ValueError, match="冲突"):
        arrow_sources(tmp_path, shards=1)


def test_arrow_requires_exact_sample_count(tmp_path):
    (tmp_path / "data-00000-of-00001.arrow").write_bytes(arrow_bytes(count=2))
    with pytest.raises(ValueError, match="总样本"):
        audit_tokamak(tmp_path, counts=(1, 1, 1), shards=1)


def test_snapshot_captures_actual_patch_and_refuses_overwrite(tmp_path):
    source = tmp_path / "upstream"
    source.mkdir()
    names = (
        "1D/model/trainer.py",
        "1D/posttrain/post_train.py",
        "1D/inference/inference_ft.py",
        "tokamak/inference/pipeline.py",
        "tokamak/kstar_solver.py",
        "LICENSE",
    )
    for name in names:
        path = source / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("original\n")

    def git(*args):
        subprocess.run(["git", "-C", str(source), *args], check=True, capture_output=True)

    git("init")
    git("add", ".")
    git("-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "-m", "base")
    (source / names[0]).write_text("actual modified source\n")
    (source / "untracked.py").write_text("record but do not execute\n")
    target = tmp_path / "snapshot"
    manifest = capture_source(source, target)
    assert (target / names[0]).read_text() == "actual modified source\n"
    assert "untracked.py" in manifest["untracked"]
    assert not (target / "untracked.py").exists()
    assert "actual modified source" in (target / "source.patch").read_text()
    assert json.loads((target / "source.json").read_text())["files"] == manifest["files"]
    with pytest.raises(FileExistsError):
        capture_source(source, target)
    with pytest.raises(ValueError):
        capture_source(source, source / "snapshot")
