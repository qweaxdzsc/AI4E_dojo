"""静态外流 MeshGraphNet 的 Task 托管、恢复与资产验收。"""

from __future__ import annotations

from pathlib import Path

import ai4e_task as task
import torch
import yaml

from tests.integration.test_meshgraphnet_aero_examples import setup_meshgraphnet_case


def _checkpoint(run: dict) -> Path:
    return Path(run["run_dir"]) / "checkpoints/last.pt"


def _assert_state_equal(left, right):
    if isinstance(left, dict):
        assert left.keys() == right.keys()
        for key in left:
            _assert_state_equal(left[key], right[key])
    elif isinstance(left, (list, tuple)):
        assert len(left) == len(right)
        for first, second in zip(left, right, strict=True):
            _assert_state_equal(first, second)
    elif torch.is_tensor(left):
        assert torch.equal(left, right)
    else:
        assert left == right


def test_task_runs_copied_meshgraphnet_and_forks_checkpoint_asset(tmp_path):
    """Task 不解释图结构，并把固定检查点作为内部资产复制到派生任务。"""
    case, _platform = setup_meshgraphnet_case(tmp_path / "source", "shapenet_car_meshgraphnet")
    project = tmp_path / "project"
    task.create_project(project)
    item = task.new_task(project, "shape-meshgraphnet", source=case)
    first = task.wait_run(project, task.submit_run(project, item["id"])["id"], timeout=90)
    assert first["status"] == "succeeded", task.read_log(project, first["id"])
    assert _checkpoint(first).is_file()
    assert Path(first["run_dir"], "artifacts/physical-predictions.json").is_file()

    child = task.fork_task(project, item["id"], copy_checkpoints=True, run_id=first["id"])
    copied = [value for value in child["copied_outputs"].values() if value["kind"] == "checkpoint"]
    assert copied
    source_state = torch.load(_checkpoint(first), map_location="cpu", weights_only=False)
    copied_state = torch.load(project / copied[0]["path"], map_location="cpu", weights_only=False)
    assert source_state["epoch"] == copied_state["epoch"] == 1


def test_task_configuration_can_raise_training_target_for_real_resume(tmp_path):
    """固定更新语义下提高目标轮次，恢复状态与连续训练严格一致。"""
    case, _platform = setup_meshgraphnet_case(tmp_path / "source", "nasa_crm_meshgraphnet")
    # warmup_cosine 的首轮学习率依赖最终更新预算；本用例只验证恢复本身，
    # 因而使用与目标轮次无关的 constant 调度，避免把改变训练计划误判为恢复偏差。
    source_config = yaml.safe_load((case / "config.yaml").read_text())
    source_config["train"]["scheduler"] = "constant"
    (case / "config.yaml").write_text(yaml.safe_dump(source_config, sort_keys=False))
    project = tmp_path / "project"
    task.create_project(project)
    item = task.new_task(project, "nasa-meshgraphnet", source=case)
    first = task.wait_run(project, task.submit_run(project, item["id"])["id"], timeout=90)
    assert first["status"] == "succeeded", task.read_log(project, first["id"])
    current = task.read_configuration(project, item["id"])
    config = current["config"]
    config["pipeline"]["stages"] = ["train"]
    config["train"]["max_epochs"] = 2
    config["inputs"]["train"]["preparation"] = str(
        Path(first["run_dir"]) / "artifacts/preparation.json"
    )
    config["inputs"]["train"]["resume"] = str(_checkpoint(first))
    task.replace_configuration(project, item["id"], config, revision=current["revision"])
    second = task.wait_run(project, task.submit_run(project, item["id"])["id"], timeout=90)
    assert second["status"] == "succeeded", task.read_log(project, second["id"])
    state = torch.load(_checkpoint(second), map_location="cpu", weights_only=False)
    assert state["epoch"] == 2
    effective = yaml.safe_load(Path(second["run_dir"], "inputs/config.yaml").read_text())
    assert effective["inputs"]["train"]["resume"] == str(_checkpoint(first))

    continuous_config = yaml.safe_load((case / "config.yaml").read_text())
    continuous_config["pipeline"]["stages"] = ["trainprep", "train"]
    continuous_config["train"]["max_epochs"] = 2
    (case / "config.yaml").write_text(yaml.safe_dump(continuous_config, sort_keys=False))
    continuous_task = task.new_task(project, "nasa-continuous", source=case)
    continuous = task.wait_run(
        project, task.submit_run(project, continuous_task["id"])["id"], timeout=90
    )
    assert continuous["status"] == "succeeded", task.read_log(project, continuous["id"])
    uninterrupted = torch.load(_checkpoint(continuous), map_location="cpu", weights_only=False)
    for key in ("model", "optimizer", "scheduler"):
        _assert_state_equal(state[key], uninterrupted[key])
    assert (state["epoch"], state["updates"]) == (
        uninterrupted["epoch"],
        uninterrupted["updates"],
    )
