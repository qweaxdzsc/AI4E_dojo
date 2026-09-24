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


def test_queued_run_rejects_changed_application_dependency(tmp_path, monkeypatch):
    """提交后外部应用依赖变化，worker 写失败终态且不执行脚本。"""
    import os

    source = recipe(tmp_path)
    external = tmp_path / "external"
    external.mkdir()
    (external / "run_dependency.py").write_text("VALUE = 1\n")
    (source / "custom_app.py").write_text(
        "from run_dependency import VALUE\ndef inspect(request):\n    return {'value': VALUE}\n"
    )
    cfg = OmegaConf.load(source / "config.yaml")
    cfg.components = {"application": "custom_app"}
    OmegaConf.save(cfg, source / "config.yaml")
    monkeypatch.setenv("PYTHONPATH", str(external) + os.pathsep + os.environ.get("PYTHONPATH", ""))
    project = tmp_path / "project"
    task.create_project(project)
    item = task.new_task(project, "captured", source=source)
    queued = task.submit_run(project, item["id"], start=False)
    (external / "run_dependency.py").write_text("VALUE = 2\n")
    task.start_captured_run(project, queued["id"])
    result = task.wait_run(project, queued["id"])
    assert result["status"] == "failed", result
    assert "application_source_changed" in json.dumps(result)


def test_resume_missing_captured_source_does_not_backfill_history(tmp_path):
    """有恢复声明但缺应用来源的旧记录保持不可用，不补写当前应用。"""
    from ai4e_task.storage.database import transaction
    from ai4e_task.storage.records import fetch, put

    project, item = setup(tmp_path)
    queued = task.submit_run(project, item["id"], start=False)
    historical = fetch(project, "run", queued["id"])
    historical["task_description"] = {"description": {"resume_inputs": ["inputs.train.resume"]}}
    with transaction(project) as db:
        put(db, "run", historical, replace=True)
    with pytest.raises(ValueError, match="captured_application_source_missing"):
        task.resume_run(project, queued["id"])
    assert fetch(project, "run", queued["id"]) == historical


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
    assert result["metrics"]["test/score"]["status"] == "available"
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


def _legacy_aero_recipe(tmp_path):
    """旧官方外流入口：声明 ShapeNet，但不写 configuration_adapter，且拒 workers。"""
    source = tmp_path / "legacy-aero"
    source.mkdir()
    raw = tmp_path / "legacy-raw"
    raw.mkdir()
    (raw / "sample.txt").write_text("input")
    (source / "configuration.py").write_text(
        """from ai4e_core.base.config import load_config
from omegaconf import OmegaConf

def load_configuration(path, overrides=None):
    cfg = load_config(path, overrides)
    raw = OmegaConf.to_container(OmegaConf.create(cfg), resolve=True).get("rawprep") or {}
    if "workers" in raw:
        raise ValueError(f"未知 rawprep 配置: {sorted(['workers'])}")
    return cfg
"""
    )
    (source / "pipeline.py").write_text(
        """from configuration import load_configuration
from ai4e_core import run
from ai4e_core.run.training import TrainingRun

def execute(cfg):
    TrainingRun().report({"ok": 1, "workers": cfg.rawprep.get("workers")})

if __name__ == "__main__":
    raise SystemExit(run.launch({"test": execute}, script=__file__, config_loader=load_configuration))
"""
    )
    OmegaConf.save(
        OmegaConf.create(
            {
                "dataset": {"root": str(raw)},
                "data_root": str(tmp_path / "legacy-out"),
                "run_root": str(tmp_path / "legacy-runs"),
                "paths": {"datasets": {"root": "${data_root}"}},
                "pipeline": {"stages": ["test"]},
                "rawprep": {"workers": 10},
                "score": 1.0,
                "delay": 0.0,
                "fail": False,
            }
        ),
        source / "config.yaml",
    )
    (source / "task-entry.json").write_text(
        json.dumps(
            {
                "script": "pipeline.py",
                "config": "config.yaml",
                "components": {
                    "dataset": "ai4e_contrib.application.datasets.shapenet_car",
                    "model": "ai4e_contrib.ability.model.abupt.component",
                },
                "platform_case": "shapenet_car_abupt",
                "inputs": {"dataset.root": "dataset"},
                "outputs": {
                    "run_root": "{run_root}",
                    "data_root": "{data_dir}",
                    "paths.datasets.root": "{data_dir}",
                },
            }
        )
    )
    return source


def test_legacy_descriptor_cannot_change_loader_behavior(tmp_path):
    """不因旧描述或官方身份静默改写用户加载器。"""
    project = tmp_path / "legacy-project"
    task.create_project(project)
    item = task.new_task(project, "legacy", source=_legacy_aero_recipe(tmp_path))
    run = task.wait_run(project, task.submit_run(project, item["id"])["id"])
    assert run["status"] == "failed"
    assert "未知 rawprep 配置" in run["error"]
    request = json.loads((project / run["request_path"]).read_text())
    assert "configuration_adapter" not in request["entry"]


def test_queued_input_change_fails_before_user_code(tmp_path):
    """排队后外部输入变动，执行收据失败且用户流程没有写摘要。"""
    project, item = setup(tmp_path)
    queued = task.submit_run(project, item["id"], start=False)
    request = json.loads((project / queued["request_path"]).read_text())
    from ai4e_task.tasks.assets import asset_path

    asset = next(iter(request["context"]["assets"].values()))
    path = asset_path(project, asset)
    if path.is_dir():
        (path / "changed.txt").write_text("changed after capture")
    else:
        path.write_bytes(b"changed after capture")
    task.start_captured_run(project, queued["id"])
    result = task.wait_run(project, queued["id"])
    assert result["status"] == "failed", result
    assert "asset_changed" in result["error"]
    assert not (Path(result["run_dir"]) / "summary.json").exists()
