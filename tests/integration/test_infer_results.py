"""推理文件作用域与请求门禁，不把无输出的请求作为有效批次。"""

from pathlib import Path

import pytest
from ai4e_task.tasks.inference_results import _member

from ai4e_spec.artifacts import InferenceRequest


def test_result_members_cannot_escape_run(tmp_path):
    data = tmp_path / "data"
    data.mkdir()
    outside = tmp_path / "other.pt"
    outside.write_bytes(b"another run")
    run = {"data_dir": str(data), "run_dir": str(tmp_path / "run")}
    for path in (outside, data / ".." / "other.pt"):
        with pytest.raises(ValueError, match="outside_run"):
            _member(path, run)
    (data / "linked.pt").symlink_to(outside)
    with pytest.raises(ValueError, match="outside_run"):
        _member(data / "linked.pt", run)
    with pytest.raises(ValueError, match="missing"):
        _member(data / "missing.pt", run)
    own = data / "prediction.pt"
    own.write_bytes(b"owned")
    assert Path(_member(own, run)["path"]) == own


@pytest.mark.parametrize(
    "patch",
    [
        {"samples": ["a", "a"]},
        {"device": "cuda:-1"},
        {"options": []},
        {"options": {"query_chunk_size": True}},
        {"output_path": "/outside"},
        {"options": {"evaluate": False, "save_predictions": False, "export_vtk": False}},
    ],
)
def test_invalid_batch_choices_are_rejected(patch):
    request = {
        "expected_revision": "config",
        "checkpoints": [{"id": "r:last.pt", "revision": "sha"}],
        "samples": ["a"],
    }
    with pytest.raises(ValueError):
        InferenceRequest.from_dict({**request, **patch})
