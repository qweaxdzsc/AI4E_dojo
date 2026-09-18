"""固定结果、边界隔离与外部运行所需交接验收。"""

import numpy as np
import pytest
import torch

from ai4e_contrib.ability.transform.gencp.boundaries import neutron_inpainting
from ai4e_core.applications.coupled_physics.infer import save_results
from ai4e_core.applications.coupled_physics.post import read_results
from tools.verification.gencp.budget import run_budgeted


def test_fixed_arrays_detect_content_change(tmp_path):
    values = {"fluid": torch.ones(2, 3, 4, 5, 2)}
    path = save_results(values, values, tmp_path / "output", metadata={"space": "physical"})
    _record, pairs = read_results(path)
    np.testing.assert_array_equal(pairs["fluid"][0], values["fluid"].numpy())
    np.save(tmp_path / "output/fluid_prediction.npy", np.zeros((2, 3, 4, 5, 2), dtype="float32"))
    with pytest.raises(ValueError, match="内容改变"):
        read_results(path)


def test_boundary_only_changes_declared_column():
    states = {"neutron": torch.zeros(2, 3, 4, 20, 1), "solid": torch.ones(2, 3, 4, 8, 1)}
    noise = torch.zeros(2, 3, 4, 1, 1)
    clean = torch.ones_like(noise)
    updated = neutron_inpainting(states, 0.5, field="neutron", noise=noise, clean=clean)
    assert torch.all(updated["neutron"][..., :1, :] == 0.5)
    assert torch.all(updated["neutron"][..., 1:, :] == 0)
    assert torch.all(states["neutron"] == 0)
    assert updated["solid"] is states["solid"]


def test_budget_counts_failures_and_refuses_more(tmp_path):
    import json
    import sys

    ledger = tmp_path / "budget.json"
    assert run_budgeted(ledger, [sys.executable, "-c", "raise SystemExit(2)"]) == 2
    state = json.loads(ledger.read_text())
    assert state["seconds"] > 0 and state["runs"][0]["status"] == "failed"
    with pytest.raises(TimeoutError):
        run_budgeted(ledger, [sys.executable, "-c", "pass"], soft=0)


def test_budget_timeout_and_missing_command_are_recorded(tmp_path):
    import json
    import sys

    ledger = tmp_path / "timeout.json"
    code = run_budgeted(
        ledger, [sys.executable, "-c", "import time; time.sleep(10)"], soft=0.05, hard=0.2
    )
    assert code != 0
    record = json.loads(ledger.read_text())
    assert record["seconds"] < 2 and record["runs"][0]["soft_stopped"]
    with pytest.raises(FileNotFoundError):
        run_budgeted(tmp_path / "missing.json", ["/not/an/executable"])
    assert json.loads((tmp_path / "missing.json").read_text())["runs"][0]["status"] == "failed"
