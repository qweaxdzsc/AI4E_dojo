"""共享覆盖的失败收据、取消、未知进程与 CLI 单次许可。"""

import json
import os
import signal
import subprocess
import sys
import time

import ai4e_task as task
import pytest

from tests.integration.test_task_shared_execution import run_success, setup_shared


def test_cli_overwrite_is_single_use(tmp_path):
    project, item, _ = setup_shared(tmp_path)
    run_success(project, item)
    command = [sys.executable, "-m", "ai4e_task", "run", item["id"], "--project", str(project)]
    rejected = subprocess.run(command, capture_output=True, text=True, check=False)
    assert rejected.returncode != 0
    result = subprocess.run(command + ["--overwrite"], capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr
    run = task.wait_run(project, json.loads(result.stdout)["id"])
    assert run["status"] == "succeeded", run
    assert subprocess.run(command, capture_output=True, check=False).returncode != 0


def test_cancel_and_unknown_process_never_publish(tmp_path):
    project, item, _ = setup_shared(tmp_path)
    run = task.submit_run(project, item["id"], overrides=["delay=30"])
    deadline = time.monotonic() + 10
    while not (project / "shared/datasets/sample_data/asset.json").exists():
        assert time.monotonic() < deadline
        time.sleep(0.05)
    stopped = task.stop_run(project, run["id"])
    assert stopped["status"] == "stopped"
    assert task.get_shared_dataset(project, "sample_data")["status"] == "unavailable"
    run = task.submit_run(project, item["id"], overrides=["delay=30"], overwrite=True)
    request = project / run["request_path"]
    while not (request.parent / "started.json").exists():
        time.sleep(0.05)
    os.kill(run["pid"], signal.SIGKILL)
    time.sleep(0.2)
    assert task.get_run(project, run["id"])["status"] == "unknown"
    with pytest.raises(ValueError, match="shared_dataset_busy"):
        task.submit_run(project, item["id"], overwrite=True)
    assert task.get_shared_dataset(project, "sample_data")["status"] != "available"


def test_incomplete_publication_fails_and_old_receipt_stays_fixed(tmp_path):
    project, item, _ = setup_shared(tmp_path)
    original = run_success(project, item)
    receipt = original["shared_publications"]
    script = project / "tasks" / item["id"] / "recipe/pipeline.py"
    script.write_text(script.read_text().replace('"train": ["one"]', '"train": ["one", "missing"]'))
    failed = task.wait_run(project, task.submit_run(project, item["id"], overwrite=True)["id"])
    assert failed["status"] == "failed" and "incomplete_partitions" in failed["error"]
    assert task.get_shared_dataset(project, "sample_data")["status"] == "available"
    assert task.get_run(project, original["id"])["shared_publications"] == receipt
    assert task.run_physical_manifest(project, original) is not None


def test_restart_reconciles_failed_publication_without_claiming_success(tmp_path, monkeypatch):
    from ai4e_task.storage import shared_datasets
    from ai4e_task.storage.database import transaction
    from ai4e_task.storage.records import get, put

    project, item, _ = setup_shared(tmp_path)
    run = run_success(project, item)
    with transaction(project) as db:
        slot = get(db, "shared_build", "sample_data")
        put(db, "shared_build", {**slot, "status": "building"}, replace=True)

    def fail(*_):
        raise OSError("publication disk failure")

    monkeypatch.setattr(shared_datasets, "publish", fail)
    assert task.get_run(project, run["id"])["status"] == "failed"
    assert task.get_run(project, run["id"])["status"] == "failed"
    assert task.get_shared_dataset(project, "sample_data")["status"] == "unavailable"
