"""项目、new/fork、快照与幂等发布的行为验收。"""

import json
from concurrent.futures import ThreadPoolExecutor

import ai4e_task as task
import pytest
from omegaconf import OmegaConf


def recipe(tmp_path):
    """不导入训练模型的普通用户入口，仍使用真实 core 会话。"""
    source = tmp_path / "template"
    source.mkdir()
    raw = tmp_path / "raw"
    raw.mkdir()
    (raw / "sample.txt").write_text("input")
    (source / "pipeline.py").write_text("""from ai4e_core import run
from ai4e_core.run.training import TrainingRun
import time

def execute(cfg):
    time.sleep(float(cfg.delay))
    if cfg.fail:
        raise ValueError("requested failure")
    TrainingRun().report({"score": float(cfg.score)})

if __name__ == "__main__":
    raise SystemExit(run.launch({"test": execute}, script=__file__))
""")
    OmegaConf.save(
        OmegaConf.create(
            {
                "dataset": {"root": str(raw)},
                "data_root": str(tmp_path / "out"),
                "run_root": str(tmp_path / "old-runs"),
                "paths": {"datasets": {"root": "${data_root}"}},
                "pipeline": {"stages": ["test"]},
                "score": 2.0,
                "delay": 0.0,
                "fail": False,
            }
        ),
        source / "config.yaml",
    )
    entry = {
        "script": "pipeline.py",
        "config": "config.yaml",
        "inputs": {"dataset.root": "dataset"},
        "outputs": {
            "run_root": "{run_root}",
            "data_root": "{data_dir}",
            "paths.datasets.root": "{data_dir}",
        },
        "metrics": [
            {
                "name": "score",
                "path": ["reports", "train", "score"],
                "quantity": {
                    "field": "pressure",
                    "domain": "surface",
                    "unit": "1",
                    "split": "test",
                    "statistic": "mean",
                },
            }
        ],
    }
    (source / "task-entry.json").write_text(json.dumps(entry))
    return source


def test_new_fork_version_tree_and_current_edit(tmp_path):
    project = tmp_path / "project"
    task.create_project(project)
    source = recipe(tmp_path)
    task.register_template(project, "demo", source)
    first = task.new_task(project, "root", source="demo", idempotency_key="new-1")
    assert task.new_task(project, "root", source="demo", idempotency_key="new-1") == first
    folder = project / "tasks" / first["id"]
    cfg = OmegaConf.load(folder / "recipe/config.yaml")
    cfg.score = 3
    OmegaConf.save(cfg, folder / "recipe/config.yaml")
    assert task.compare_worktree(project, first["id"])["files"]
    child = task.fork_task(project, first["id"], idempotency_key="fork-1")
    assert task.fork_task(project, first["id"], idempotency_key="fork-1") == child
    assert child["parent_version_id"] == first["version_id"]
    assert task.compare_versions(project, first["version_id"], child["version_id"])["files"]
    task.new_task(project, "another root")
    assert len(task.get_lineage(project)) == 3
    assert len(task.get_lineage(project, first["version_id"])) == 2
    copied = project / "tasks" / child["id"] / "recipe/config.yaml"
    before = copied.read_text()
    (folder / "recipe/config.yaml").write_text("changed: true")
    assert copied.read_text() == before
    assert not list((project / "tasks" / child["id"] / "runs").iterdir())
    with pytest.raises(ValueError, match="idempotency_conflict"):
        task.new_task(project, "different", source=source, idempotency_key="new-1")


def test_concurrent_idempotency_and_failed_copy(tmp_path, monkeypatch):
    project = tmp_path / "p"
    task.create_project(project)
    source = recipe(tmp_path)
    with ThreadPoolExecutor(max_workers=4) as pool:
        values = list(
            pool.map(
                lambda _: task.new_task(project, "same", source=source, idempotency_key="k"),
                range(4),
            )
        )
    assert len({v["id"] for v in values}) == 1
    from ai4e_task.tasks import create

    def fail(*args, **kwargs):
        raise OSError("copy failed")

    monkeypatch.setattr(create, "materialize", fail)
    with pytest.raises(OSError):
        task.new_task(project, "broken", source=source)
    assert len(task.list_tasks(project)) == 1
    assert len(list((project / "tasks").iterdir())) == 1
    assert not list((project / ".dojo").glob("*.tmp"))


def test_path_gate_and_empty_entry(tmp_path):
    project = tmp_path / "p"
    task.create_project(project)
    first = task.new_task(project, "empty")
    with pytest.raises(ValueError, match="entry_required"):
        task.submit_run(project, first["id"])
    with pytest.raises(ValueError):
        task.register_shared(project, "../escape", tmp_path, copy=False)
    with pytest.raises(FileExistsError):
        task.create_project(project)
