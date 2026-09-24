"""经典网络验证计时、跨进程串行和十三组合配置测试；不运行训练。"""

import multiprocessing
import os
import time

import pytest

from tools.verification.classic_networks.budget import BudgetExceeded, BudgetLedger, TrainingBusy
from tools.verification.classic_networks.protocol import (
    COMBINATIONS,
    configuration_for,
    select_updates,
)


class Clock:
    def __init__(self):
        self.value = 1000.0

    def __call__(self):
        return self.value


def hold_training(root, ready, release):
    with BudgetLedger(root).training_lock():
        ready.set()
        release.wait(5)


def leave_orphan(root):
    with BudgetLedger(root).measure("darcy:mlp", "crashed"):
        os._exit(17)


def test_failed_retry_and_shared_charge_persist(tmp_path):
    clock = Clock()
    ledger = BudgetLedger(tmp_path, clock=clock, wall_clock=clock)
    ledger.record_charge("darcy:mlp", "shared_preparation", 25, details={"share": "1/12"})
    with (
        pytest.raises(ValueError, match="original"),
        ledger.measure("darcy:mlp", "reference", training=True),
    ):
        clock.value += 12
        assert ledger.remaining("darcy:mlp") == 10800 - 37
        raise ValueError("original failure")
    with ledger.measure("darcy:mlp", "reference_retry", training=True):
        clock.value += 8
    reopened = BudgetLedger(tmp_path)
    assert reopened.remaining("darcy:mlp") == 10800 - 45
    item = reopened.snapshot()["combinations"]["darcy:mlp"]
    assert item["active"] is None
    assert [event["status"] for event in item["events"]] == ["charged", "failed", "complete"]
    assert item["events"][1]["exception"] == "ValueError"
    assert reopened.remaining("shapenet:mlp") == 10800


def test_budget_refuses_reset_limit_and_preserves_excess_charge(tmp_path):
    ledger = BudgetLedger(tmp_path, limit_seconds=10)
    with pytest.raises(BudgetExceeded):
        ledger.record_charge("x", "already_computed", 12)
    assert ledger.snapshot()["combinations"]["x"]["spent_seconds"] == 12
    assert ledger.remaining("x") == 0
    with pytest.raises(BudgetExceeded), ledger.measure("x", "forbidden"):
        pytest.fail("预算耗尽后不得执行")
    with pytest.raises(ValueError, match="上限"):
        BudgetLedger(tmp_path).snapshot()


def test_hard_deadline_interrupts_and_records_timeout(tmp_path):
    ledger = BudgetLedger(tmp_path, limit_seconds=0.05)
    callbacks = []
    with (
        pytest.raises(BudgetExceeded),
        ledger.measure("x", "bounded_wait", on_timeout=lambda: callbacks.append("stopped")),
    ):
        time.sleep(0.5)
    item = ledger.snapshot()["combinations"]["x"]
    assert callbacks == ["stopped"]
    assert item["active"] is None and item["spent_seconds"] >= 0.05
    assert item["events"][-1]["exception"] == "BudgetExceeded"
    assert ledger.remaining("x") == 0


def test_cross_process_training_lock_released_after_owner(tmp_path):
    context = multiprocessing.get_context("spawn")
    ready, release = context.Event(), context.Event()
    process = context.Process(target=hold_training, args=(str(tmp_path), ready, release))
    process.start()
    try:
        assert ready.wait(5)
        with (
            pytest.raises(TrainingBusy),
            BudgetLedger(tmp_path).measure("other", "train", training=True),
        ):
            pytest.fail("不能并行训练")
    finally:
        release.set()
        process.join(5)
        if process.is_alive():
            process.terminate()
            process.join()
    assert process.exitcode == 0
    with BudgetLedger(tmp_path).training_lock():
        pass


def test_ungraceful_exit_is_reconciled_without_losing_charge(tmp_path):
    context = multiprocessing.get_context("spawn")
    process = context.Process(target=leave_orphan, args=(str(tmp_path),))
    process.start()
    process.join(5)
    assert process.exitcode == 17
    ledger = BudgetLedger(tmp_path)
    assert ledger.snapshot()["combinations"]["darcy:mlp"]["active"] is not None
    ledger.record_charge("darcy:mlp", "retry_setup", 2)
    item = ledger.snapshot()["combinations"]["darcy:mlp"]
    assert item["active"] is None
    assert item["spent_seconds"] >= 2
    assert item["events"][0]["status"] == "orphan_conservative_charge"


def test_model_matrix_has_exact_thirteen_and_independent_config_copies():
    assert len(COMBINATIONS) == len(set(COMBINATIONS)) == 13
    for case, family in COMBINATIONS:
        config = configuration_for(case, family, updates=50)
        assert config["dataset"]["case"] == case
        assert config["model"]["family"] == family
        assert config["train"]["updates"] == 50
        assert config["train"]["seconds"] == 9000
        assert config["components"]["model"].endswith("binding.build_network")
        assert (family == "rnn") == (case == "double_cylinder")
    first = configuration_for("darcy", "transformer")
    first["model"]["parameters"]["dim"] = 999
    assert configuration_for("darcy", "transformer")["model"]["parameters"]["dim"] == 64
    assert configuration_for("shapenet_volume", "transformer")["model"]["parameters"][
        "patch_shape"
    ] == [4, 4, 4]
    with pytest.raises(ValueError, match="十三"):
        configuration_for("darcy", "rnn")


def test_selection_uses_explicit_reference_dojo_eval_recovery_coefficients():
    quick = select_updates(1, 2)
    assert quick["updates"] == 100
    assert quick["parts_seconds"] == {
        "reference": 200.0,
        "dojo_train": 100.0,
        "evaluation": 50.0,
        "recovery": 20.0,
        "fixed": 60.0,
    }
    assert quick["estimated_seconds"] == 645
    assert quick["estimated_total_seconds"] == 645
    assert quick["estimate_only"] is True
    assert select_updates(30)["updates"] == 50
    assert select_updates(70)["updates"] == 20
    consumed = select_updates(1, 2, available_seconds=2300, spent_seconds=8500)
    assert consumed["updates"] == 50
    assert consumed["estimated_seconds"] == 367.5
    assert consumed["estimated_total_seconds"] == 8867.5
    assert consumed["ceiling_seconds"] == 500
    with pytest.raises(ValueError, match="禁止开跑"):
        select_updates(1, spent_seconds=9000)
    with pytest.raises(ValueError, match="禁止开跑"):
        select_updates(200)
    with pytest.raises(ValueError, match="禁止开跑"):
        select_updates(1, available_seconds=100)
    with pytest.raises(ValueError):
        select_updates(float("nan"))


@pytest.mark.parametrize("case,family", COMBINATIONS)
def test_protocol_parameters_match_current_network_constructors(case, family):
    from ai4e_contrib.application.classic_networks.binding import build_network

    config = configuration_for(case, family)
    model = build_network(config["model"])
    assert sum(p.numel() for p in model.parameters()) > 0
