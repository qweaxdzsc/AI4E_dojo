"""补充运行恢复、共享身份、快照不可变及 CLI 一致性。"""

import json
import subprocess
import sys

import ai4e_task as task
import pytest
from ai4e_task.storage.files import write_json

from tests.integration.test_task_management import recipe


def test_shared_identity_and_tampered_version(tmp_path):
    project = tmp_path / "p"
    task.create_project(project)
    source = recipe(tmp_path)
    shared = task.register_shared(project, "datasets/demo", tmp_path / "raw", kind="dataset")
    first = task.new_task(project, "root", source=source)
    assert first["assets"]["inputs.test.dataset"]["id"] == shared["id"]
    snapshot = project / "tasks" / first["id"] / ".dojo/snapshots/creation/config.yaml"
    snapshot.write_text("tampered: true")
    with pytest.raises(ValueError, match="snapshot_changed"):
        task.fork_task(project, first["id"], source="version")


def test_resume_uses_captured_code_and_keeps_version(tmp_path):
    project = tmp_path / "p"
    task.create_project(project)
    source = recipe(tmp_path)
    from omegaconf import OmegaConf

    cfg = OmegaConf.load(source / "config.yaml")
    cfg.components = {"application": "management"}
    OmegaConf.save(cfg, source / "config.yaml")
    (source / "management.py").write_text(
        'def inspect(request):\n'
        '    return {"schema_version": 1, "stages": ["train", "test"], '
        '"inputs": {"inputs.train.resume": {"kind": "checkpoint"}, '
        '"inputs.test.dataset": {"kind": "dataset"}}, '
        '"resume_inputs": ["inputs.train.resume"], "operations": [], "shared_outputs": {}}\n')
    script = source / "pipeline.py"
    script.write_text(
        script.read_text().replace(
            'session.report({"score": float(cfg.score)})',
            'TrainingRun().checkpoint("latest", {"score": float(cfg.score)})\n    session.report({"score": float(cfg.score)})',
        )
    )
    first = task.new_task(project, "root", source=source)
    a = task.submit_run(project, first["id"])
    a = task.wait_run(project, a["id"])
    assert a["status"] == "succeeded", a
    (project / "tasks" / first["id"] / "recipe/pipeline.py").write_text(
        'raise RuntimeError("edited")'
    )
    b = task.resume_run(project, a["id"])
    b = task.wait_run(project, b["id"])
    assert b["status"] == "succeeded", b
    assert b["lineage"]["resumed_from"] == a["id"]
    assert len(task.get_lineage(project)) == 1


def test_cli_and_incompatible_quantity(tmp_path):
    project = tmp_path / "p"
    task.create_project(project)
    source = recipe(tmp_path)
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ai4e_task",
            "new",
            "demo",
            "--from",
            str(source),
            "--project",
            str(project),
            "--json",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    first = json.loads(result.stdout)
    a = task.submit_run(project, first["id"])
    a = task.wait_run(project, a["id"])
    script = project / "tasks" / first["id"] / "recipe/pipeline.py"
    script.write_text(script.read_text().replace('"unit": "1"', '"unit": "Pa"'))
    b = task.submit_run(project, first["id"])
    b = task.wait_run(project, b["id"])
    assert (
        task.compare_runs(project, a["id"], b["id"])["metrics"]["test/score"]["status"] == "incompatible"
    )
    assert len(task.get_lineage(project)) == 1


def test_explicit_crash_recovery_does_not_remove_registered_task(tmp_path):
    project = tmp_path / "p"
    task.create_project(project)
    first = task.new_task(project, "real")
    orphan = project / "tasks" / "orphan"
    orphan.mkdir()
    write_json(orphan / "task.json", {"id": "orphan"})
    result = task.recover_project(project)
    assert result["removed"] == ["tasks/orphan"]
    assert (project / "tasks" / first["id"]).is_dir()


def test_declared_missing_comparison_condition_is_not_available(tmp_path):
    project = tmp_path / "p"
    task.create_project(project)
    source = recipe(tmp_path)
    # 未交付指标索引时，不用运行报告中的 score 冒充可比指标。
    script = source / "pipeline.py"
    text = script.read_text()
    begin = text.index('    session.record_metric(')
    end = text.index('\n\nif __name__', begin)
    script.write_text(text[:begin] + text[end:])
    first = task.new_task(project, "missing-sampling", source=source)
    a = task.wait_run(project, task.submit_run(project, first["id"])["id"])
    b = task.wait_run(project, task.submit_run(project, first["id"])["id"])
    assert a["status"] == b["status"] == "succeeded"
    assert task.compare_runs(project, a["id"], b["id"])["metrics"] == {}
