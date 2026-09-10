"""本地执行、快照隔离、状态核对、比较及导入验收。"""

import json
import time
from pathlib import Path

import ai4e_task as task
import pytest
from omegaconf import OmegaConf

from tests.integration.test_task_management import recipe


def setup(tmp_path):
    project = tmp_path / "p"
    task.create_project(project)
    source = recipe(tmp_path)
    first = task.new_task(project, "root", source=source)
    return project, first


def test_execution_snapshot_version_identity_and_comparison(tmp_path):
    project, first = setup(tmp_path)
    a = task.submit_run(project, first["id"], idempotency_key="run-one")
    cfgpath = project / "tasks" / first["id"] / "recipe/config.yaml"
    cfg = OmegaConf.load(cfgpath)
    cfg.score = 5
    OmegaConf.save(cfg, cfgpath)
    b = task.submit_run(project, first["id"])
    a, b = task.wait_run(project, a["id"]), task.wait_run(project, b["id"])
    assert a["status"] == b["status"] == "succeeded", (a, b)
    assert a["summary"]["reports"]["train"]["score"] == 2
    assert b["summary"]["reports"]["train"]["score"] == 5
    assert len(task.get_lineage(project)) == 1
    assert a["lineage"]["version_id"] == first["version_id"]
    assert Path(a["run_dir"]).parent == project / "tasks" / first["id"] / "runs"
    assert Path(a["data_dir"]).parent == project / "tasks" / first["id"] / "data"
    result = task.compare_runs(project, a["id"], b["id"], save=True)
    assert result["metrics"]["score"]["status"] == "available"
    assert result["files"]
    assert task.import_run(project, a["run_dir"])["id"] == a["id"]
    assert task.submit_run(project, first["id"], idempotency_key="run-one")["id"] == a["id"]


def test_failure_stop_unknown_and_incompatible(tmp_path):
    project, first = setup(tmp_path)
    run = task.submit_run(project, first["id"], overrides=["fail=true"])
    result = task.wait_run(project, run["id"])
    assert result["status"] == "failed", result
    assert "requested failure" in task.read_log(project, run["id"])
    slow = task.submit_run(project, first["id"], overrides=["delay=30"])
    request = project / slow["request_path"]
    deadline = time.monotonic() + 15
    while not (request.parent / "started.json").exists() and time.monotonic() < deadline:
        time.sleep(0.1)
    stopped = task.stop_run(project, slow["id"], timeout=15)
    assert stopped["status"] == "stopped", stopped
    # 已确认退出但缺失完成收据：只能待核对。
    (request.parent / "finished.json").unlink()
    assert task.get_run(project, slow["id"])["status"] == "unknown"
    assert len(task.get_lineage(project)) == 1


def test_script_start_failure_and_import_conflict(tmp_path):
    project, first = setup(tmp_path)
    code = project / "tasks" / first["id"] / "recipe/pipeline.py"
    code.write_text('raise RuntimeError("before core")')
    run = task.submit_run(project, first["id"])
    result = task.wait_run(project, run["id"])
    assert result["status"] == "failed"
    assert result["summary"]["failed"]
    other = tmp_path / "other"
    task.create_project(other)
    task.import_run(other, result["run_dir"])
    # 同 ID 的不同目录内容不能覆盖第一次导入。
    import shutil

    conflicting = tmp_path / "conflict"
    shutil.copytree(result["run_dir"], conflicting)
    (conflicting / "summary.json").write_text(json.dumps({"failed": False}))
    with pytest.raises(ValueError, match="run_content_conflict"):
        task.import_run(other, conflicting)
