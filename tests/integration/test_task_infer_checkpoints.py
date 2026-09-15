"""任务推理的检查点身份、排队快照与取消边界。"""

from pathlib import Path

import ai4e_task as task
import pytest

from tests.integration.test_task_execution import setup


def test_fixed_checkpoint_retains_selected_bytes(tmp_path, monkeypatch):
    from ai4e_task.tasks import checkpoints

    project, item = setup(tmp_path)
    folder = project / "tasks" / item["id"] / "runs/train/checkpoints"
    folder.mkdir(parents=True)
    source = folder / "latest.pt"
    source.write_bytes(b"selected-weight-bytes")
    monkeypatch.setattr(
        checkpoints,
        "get_run",
        lambda *_: {
            "id": "train",
            "task_id": item["id"],
            "run_dir": str(folder.parent),
            "stages": ["train"],
        },
    )
    revision = checkpoints.file_digest(source)
    frozen = task.freeze_checkpoint(project, item["id"], "train:latest.pt", revision)
    source.write_bytes(b"newer-training-weights")
    assert Path(frozen["path"]).read_bytes() == b"selected-weight-bytes"
    assert Path(frozen["path"]).stat().st_ino != source.stat().st_ino
    with pytest.raises(ValueError, match="revision_conflict"):
        task.freeze_checkpoint(project, item["id"], "train:latest.pt", revision)
    assert not list((project / "tasks" / item["id"] / "assets").glob(".*.tmp"))
    with pytest.raises(ValueError, match="task_mismatch"):
        task.freeze_checkpoint(project, "other", "train:latest.pt", revision)
    with pytest.raises(ValueError, match="invalid_checkpoint_identity"):
        task.freeze_checkpoint(project, item["id"], "train:../../escape.pt", revision)


def test_queued_code_is_fixed_and_cancel_never_starts(tmp_path):
    project, item = setup(tmp_path)
    queued = task.submit_run(project, item["id"], start=False, idempotency_key="queued")
    canceled = task.submit_run(project, item["id"], start=False)
    assert task.get_run(project, queued["id"])["status"] == "queued"
    task.stop_run(project, canceled["id"])
    assert task.start_captured_run(project, canceled["id"])["status"] == "stopped"
    config = task.read_configuration(project, item["id"])
    task.save_configuration(project, item["id"], {"score": 99}, revision=config["revision"])
    task.start_captured_run(project, queued["id"])
    done = task.wait_run(project, queued["id"])
    assert done["status"] == "succeeded"
    assert done["summary"]["reports"]["train"]["score"] == 2
    assert task.start_captured_run(project, queued["id"])["pid"] == done["pid"]
    assert len(task.get_lineage(project)) == 1
