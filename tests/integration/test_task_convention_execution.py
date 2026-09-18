"""无逐模型描述文件的真实任务子进程验收。"""

import json
from pathlib import Path

import ai4e_task as task
import pytest


def recipe(tmp_path):
    folder = tmp_path / "recipe"
    folder.mkdir()
    (folder / "config.yaml").write_text(
        "run_root: ../runs\ndata_root: ../data\npipeline:\n  stages: [post]\n"
        "inputs:\n  post:\n    results: null\nscore: 2\n"
    )
    (folder / "pipeline.py").write_text('''from pathlib import Path
from ai4e_core import run
from ai4e_core.base.config.conventions import load_recipe_config

def post(cfg):
    session = run.TrainingRun()
    path = session.output_dir("post") / "result.txt"
    path.write_text(str(cfg.score))
    session.record_asset("result", path, kind="other", stage="post")
    session.record_metric("score", cfg.score, stage="post", assets=[path], semantics={
        "field": "scalar", "unit": "1", "split": "test", "statistic": "mean", "data_identity": "sample1"})

def pipeline(cfg):
    if "post" in cfg.pipeline.stages:
        run.stage("post", post, cfg)

if __name__ == "__main__":
    raise SystemExit(run.launch(pipeline, script=__file__, config_loader=load_recipe_config))
''')
    return folder


def test_new_execute_fork_compare_without_descriptor(tmp_path):
    project = tmp_path / "project"
    task.create_project(project)
    source = recipe(tmp_path)
    first = task.new_task(project, "first", source=source)
    a = task.submit_run(project, first["id"])
    a = task.wait_run(project, a["id"], timeout=30)
    assert a["status"] == "succeeded", a
    assert a["research_status"] == "completed"
    assert Path(a["data_dir"], "post/result.txt").read_text() == "2"
    fork = task.fork_task(project, first["id"])
    b = task.submit_run(project, fork["id"], overrides=["score=3"])
    b = task.wait_run(project, b["id"], timeout=30)
    assert b["status"] == "succeeded", b
    comparison = task.compare_runs(project, a["id"], b["id"])
    assert comparison["metrics"]["post/score"]["status"] == "available"
    Path(b["data_dir"], "post/result.txt").write_text("tampered")
    comparison = task.compare_runs(project, a["id"], b["id"])
    assert comparison["metrics"]["post/score"]["status"] == "missing"
    assert len(task.get_lineage(project)) == 2


def test_only_selected_inputs_are_captured_and_missing_fails(tmp_path):
    project = tmp_path / "project"
    task.create_project(project)
    source = recipe(tmp_path)
    first = task.new_task(project, "first", source=source)
    success = task.submit_run(project, first["id"], overrides=["inputs.train.preparation=/missing"])
    assert task.wait_run(project, success["id"])["status"] == "succeeded"
    with pytest.raises(FileNotFoundError):
        task.submit_run(project, first["id"], overrides=["inputs.post.results=/missing"])


def test_unmanaged_process_and_broken_claimed_session(tmp_path):
    project = tmp_path / "project"
    task.create_project(project)
    source = recipe(tmp_path)
    (source / "pipeline.py").write_text("raise SystemExit(0)\n")
    first = task.new_task(project, "plain", source=source)
    a = task.submit_run(project, first["id"])
    a = task.wait_run(project, a["id"])
    assert a["status"] == "succeeded", a
    assert a["research_status"] == "unavailable"
    code = Path(task.get_task(project, first["id"])["directory"]) / "recipe/pipeline.py"
    code.write_text('from ai4e_core.run.writer import RunWriter\nfrom ai4e_core.run.provenance import MANAGED\nRunWriter.create(MANAGED.get()["context"].run_dir + "/..")\n')
    b = task.submit_run(project, first["id"])
    b = task.wait_run(project, b["id"])
    assert b["status"] == "failed", b
    assert "entry_did_not_complete" in b["error"]


def test_optional_operation_missing_and_descriptor_ignored(tmp_path):
    from ai4e_task.tasks.operations import operation_target
    from ai4e_task.templates.materialize import read_entry

    source = recipe(tmp_path)
    (source / "task-entry.json").write_text(json.dumps({"script": "wrong.py"}))
    assert read_entry(source)["script"] == "pipeline.py"
    with pytest.raises(ValueError, match="operation_unavailable"):
        operation_target(source, "inspect")
