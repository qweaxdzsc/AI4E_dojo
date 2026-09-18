"""WDNO公共研究约定：新旧配置、冲突、真实直接/Task闭环及资产比较。"""

import json
from copy import deepcopy
from pathlib import Path

import pytest
import yaml
from ai4e_task.templates.materialize import read_entry

from ai4e_contrib.application.spatiotemporal_pde.wdno.configuration import (
    load_configuration,
    validate,
)
from ai4e_contrib.application.spatiotemporal_pde.wdno.handoff import split_inputs
from ai4e_contrib.application.spatiotemporal_pde.wdno.migration import migrate_legacy
from tests.integration.test_wdno_recipe import fixture
from tools.verification.wdno.task_replay import exercise

ROOT = Path(__file__).resolve().parents[2]
RECIPE = ROOT / "recipes/wdno"


@pytest.mark.parametrize("selection", [[], ["missing"], ["train", "train"], ["post", "infer"]])
def test_range_rejected_by_all_entrypoints(tmp_path, selection):
    cfg = yaml.safe_load((RECIPE / "config.yaml").read_text())
    cfg["pipeline"]["stages"] = selection
    with pytest.raises(ValueError):
        validate(cfg)
    path = tmp_path / "config.yaml"
    path.write_text(yaml.safe_dump(cfg))
    with pytest.raises(ValueError):
        load_configuration(path)
    with pytest.raises(ValueError):
        load_configuration(RECIPE / "config.yaml", ["pipeline.stages=" + json.dumps(selection)])


@pytest.mark.parametrize(
    "old", ["data.output", "data.prepared", "train.resume", "infer.checkpoint", "post.results"]
)
def test_old_and_new_keys_cannot_coexist(tmp_path, old):
    from omegaconf import OmegaConf

    cfg = OmegaConf.load(RECIPE / "config.yaml")
    OmegaConf.update(cfg, old, None, force_add=True)
    with pytest.raises(ValueError, match="旧配置键"):
        validate(cfg)
    path = tmp_path / "config.yaml"
    OmegaConf.save(cfg, path)
    with pytest.raises(ValueError, match="旧配置键"):
        load_configuration(path)
    with pytest.raises(ValueError, match="旧配置键"):
        load_configuration(RECIPE / "config.yaml", [old + "=null"])


def test_paths_entry_discovery_and_explicit_migration(tmp_path, monkeypatch):
    current = yaml.safe_load((RECIPE / "config.yaml").read_text())
    old = deepcopy(current)
    old.pop("inputs")
    old["data"] = {
        "protocol": "source.json",
        "indices": "indices.json",
        "output": "data",
        "physical": None,
        "prepared": {"train": "train.json", "validation": "val.json", "test": "test.json"},
    }
    old.pop("data_root")
    old["train"]["resume"] = "latest.pt"
    old["infer"]["checkpoint"] = "latest.pt"
    old["post"] = {"results": None}
    snapshot = deepcopy(old)
    new = migrate_legacy(old, base=tmp_path)
    assert old == snapshot
    assert new["inputs"]["train"]["resume"] == str(tmp_path / "latest.pt")
    path = tmp_path / "config.yaml"
    path.write_text(yaml.safe_dump(new))
    monkeypatch.chdir(tmp_path.parent)
    cfg = load_configuration(path, ["pipeline.stages=[post]", "inputs.post.test=other.json"])
    assert cfg["inputs"]["post"]["test"] == str(tmp_path / "other.json")
    assert cfg["pipeline"]["stages"] == ["post"]
    entry = read_entry(tmp_path)
    assert entry["script"] == "pipeline.py" and entry["resume_key"] == "inputs.train.resume"
    assert "inputs.train.resume" in entry["inputs"]
    assert not (tmp_path / "task-entry.json").exists()
    cfg["pipeline"]["stages"] = ["pipeline"]
    with pytest.raises(ValueError):
        validate(cfg)


def test_explicit_predecessor_conflicts_and_missing_inputs():
    cfg = load_configuration(RECIPE / "config.yaml")
    with pytest.raises(ValueError, match="缺少输入"):
        split_inputs(cfg, "train")
    prepared = {"train": "/a", "validation": "/v", "test": "/t"}
    assert split_inputs(cfg, "train", prepared) == prepared
    cfg["inputs"]["train"]["preparation"] = "/wrong"
    with pytest.raises(ValueError, match="输入冲突"):
        split_inputs(cfg, "train", prepared)


def test_real_direct_and_task_training_restore_and_extension(tmp_path):
    config = fixture(tmp_path / "seed-recipe")
    result = exercise(tmp_path / "paired", config)
    assert result["passed"] and result["updates"] == [2, 3]
    assert result["prediction_max_abs"] == 0


def test_actual_original_data_and_historical_checkpoint_delivery():
    import os

    root_value = os.environ.get("DOJO_WDNO_TASK_ROOT")
    if not root_value:
        pytest.skip("需要显式真实原数据与历史检查点补验目录")
    root = Path(root_value)
    result = json.loads((root / "real-data/acceptance.json").read_text())
    assert result["passed"] and result["real_original_data"] and result["updates"] == [2, 3]
    assert result["prediction_max_abs"] == 0
    assert all("task-conventions" in p for p in result["runtime"]["modules"].values())
    historical = json.loads((root / "historical/acceptance.json").read_text())
    assert historical["passed"] and historical["resume_from"] == 2000
    assert historical["updates"] == 2001 and historical["checkpoint_contract_equal"]
    assert historical["training_states_equal"]
    for record in historical["evaluation"].values():
        assert record == {"samples": 16, "max_abs": 0.0}


@pytest.mark.parametrize("case", ["recipe", "example", "extension"])
def test_new_task_runs_each_stage_and_resumes(tmp_path, case):
    from tools.verification.wdno.task_replay import staged_exercise

    config = fixture(tmp_path / "staged-source")
    result = staged_exercise(tmp_path / "staged", config, case=case)
    assert result["passed"] and result["updates"] == [2, 3]
    assert result["version_count"] == 1
    assert [row["label"] for row in result["runs"]] == [
        "rawprep",
        "trainprep",
        "train",
        "infer",
        "post",
        "resume",
    ]
    assert result["post_without_model"] and result["prediction_unchanged_by_post"]
    assert set(result["failures"]) == {"train", "infer", "post"}


def test_current_original_data_staged_delivery():
    import os

    value = os.environ.get("DOJO_WDNO_STAGED_ROOT")
    if not value:
        pytest.skip("需要本次原数据新建Task分阶段实跑目录")
    root = Path(value)
    result = json.loads((root / "acceptance.json").read_text())
    summaries = json.loads((root / "summaries.json").read_text())
    assert result["passed"] and result["real_original_data"]
    assert result["updates"] == [2, 3] and result["version_count"] == 1
    assert len({row["id"] for row in result["runs"]}) == 6
    for row in result["runs"]:
        assert row["status"] == "succeeded" and row["task_id"] == result["task_id"]
        actual = json.loads(
            (Path(result["project"]) / row["run_path"] / "summary.json").read_text()
        )
        assert actual == summaries[row["label"]]["task"]
    assert result["training_states_equal"] and result["prediction_max_abs"] == 0
    assert set(result["failures"]) == {"train", "infer", "post"}
    assert result["post_without_model"] and result["prediction_unchanged_by_post"]


@pytest.mark.parametrize("interruption", [KeyboardInterrupt, TimeoutError])
def test_wait_interruption_stops_detached_task(monkeypatch, interruption):
    from tools.verification.wdno import task_replay

    stopped = []

    def interrupted(*args, **kwargs):
        if interruption is TimeoutError:
            return {"status": "running"}
        raise interruption()

    monkeypatch.setattr(task_replay.task, "wait_run", interrupted)
    monkeypatch.setattr(
        task_replay.task,
        "stop_run",
        lambda project, run_id, **kw: stopped.append(run_id) or {"status": "stopped"},
    )
    with pytest.raises(interruption):
        task_replay.wait_task("project", "only-this-run")
    assert stopped == ["only-this-run"]


def test_timeout_stops_actual_task_worker(tmp_path):
    import ai4e_task as task

    from tools.verification.wdno.task_replay import wait_task

    code = tmp_path / "slow-recipe"
    cfg = fixture(code)
    cfg["pipeline"]["stages"] = ["rawprep"]
    (code / "pipeline.py").write_text("""import time
from configuration import load_configuration
from ai4e_core import run

def slow(cfg):
    time.sleep(30)

def pipeline(cfg):
    return run.stage("rawprep", slow, cfg)

if __name__ == "__main__":
    raise SystemExit(run.launch(pipeline, script=__file__, config_loader=load_configuration))
""")
    project = tmp_path / "stop-project"
    task.create_project(project)
    current = task.new_task(project, "slow-wdno-test", source=code, configuration=cfg)
    record = task.submit_run(project, current["id"])
    with pytest.raises(TimeoutError):
        wait_task(project, record["id"], timeout=0.1)
    assert task.get_run(project, record["id"])["status"] == "stopped"
