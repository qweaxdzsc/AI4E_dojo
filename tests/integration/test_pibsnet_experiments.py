"""真实短训的全测试周期评价，验证零基轮次调度和模式恢复。"""

import torch

from ai4e_contrib.application.datasets.parametric import component
from tests.integration.test_pibsnet_training import configuration_for, run_stages


def test_generalization_evaluation_schedule_and_full_test_set(tmp_path):
    component("neumann_diffusion").generate(
        {"output": str(tmp_path / "data"), "train": 2, "test": 3, "nx": 9, "nt": 7}
    )
    cfg = configuration_for("neumann_diffusion", tmp_path)
    cfg["train"].update(max_epochs=3, evaluation={"enabled": True, "interval": 2})
    assert run_stages(cfg, ["trainprep", "train", "post"]) == 0
    state = torch.load(next((tmp_path / "runs").glob("*/checkpoints/last.pt")), weights_only=False)
    evaluations = [r for r in state["history"] if r["evaluation"] is not None]
    assert [r["epoch"] for r in evaluations] == [1, 3]
    assert all(r["evaluation"]["samples"] == 3 for r in evaluations)
    assert all(r["evaluation"]["loss"] >= 0 for r in evaluations)
    assert all(
        r["evaluation"]["max_absolute_error"] >= r["evaluation"]["loss"] ** 0.5 for r in evaluations
    )
    assert state["updates"] == 3
