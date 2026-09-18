"""控制案例复用的累计预算监督器验收，覆盖重试与进程组终止。"""

import json
import sys

import pytest

from tools.verification.gencp.budget import run_budgeted


def test_success_failure_retry_accounted(tmp_path):
    ledger = tmp_path / "budget.json"
    assert (
        run_budgeted(ledger, [sys.executable, "-c", "pass"], credit_seconds=1.0, soft=10, hard=11)
        == 0
    )
    assert (
        run_budgeted(ledger, [sys.executable, "-c", "raise SystemExit(2)"], soft=10, hard=11) == 2
    )
    state = json.loads(ledger.read_text())
    assert len(state["runs"]) == 2 and state["seconds"] > 1
    assert [x["status"] for x in state["runs"]] == ["success", "failed"]
    with pytest.raises(TimeoutError):
        run_budgeted(ledger, [sys.executable, "-c", "pass"], soft=0.5, hard=1)
    assert json.loads(ledger.read_text()) == state


def test_soft_and_hard_stop(tmp_path):
    ledger = tmp_path / "hard.json"
    script = "import signal,time; signal.signal(signal.SIGINT, signal.SIG_IGN); time.sleep(30)"
    with pytest.raises(TimeoutError, match="180"):
        run_budgeted(ledger, [sys.executable, "-c", script], soft=0.2, hard=0.5)
    state = json.loads(ledger.read_text())
    assert 0.5 <= state["seconds"] < 3
    assert state["runs"][0]["status"] == "failed" and state["runs"][0]["soft_stopped"]


def test_unclosed_ledger_refuses_restart(tmp_path):
    ledger = tmp_path / "running.json"
    ledger.write_text(json.dumps({"seconds": 1, "runs": [{"status": "running"}]}))
    with pytest.raises(RuntimeError, match="未正常收尾"):
        run_budgeted(ledger, [sys.executable, "-c", "pass"])


def test_continuation_reserves_evaluation_and_keeps_history(tmp_path):
    from tools.verification.safediffcon.budget import phase_limits

    ledger = tmp_path / "budget.json"
    state = {"seconds": 3575.0, "runs": [{"status": "success", "seconds": 3575.0}]}
    ledger.write_text(json.dumps(state))
    soft, hard = phase_limits(ledger, seconds=9000, reserve=2100)
    assert (soft, hard) == (8695, 8700)
    assert json.loads(ledger.read_text()) == state
    with pytest.raises(ValueError, match="已有"):
        phase_limits(tmp_path / "fresh.json", seconds=100, reserve=0)
    with pytest.raises(TimeoutError):
        phase_limits(ledger, seconds=100, reserve=8000)


@pytest.mark.parametrize("seconds,reserve", [(float("nan"), 0), (10, -1), (0, 0)])
def test_invalid_continuation_budget_fails_before_compute(tmp_path, seconds, reserve):
    from tools.verification.safediffcon.budget import phase_limits

    ledger = tmp_path / "budget.json"
    ledger.write_text(json.dumps({"seconds": 1, "runs": []}))
    with pytest.raises(ValueError):
        phase_limits(ledger, seconds=seconds, reserve=reserve)


def test_training_forecast_counts_both_sides_and_resumed_steps():
    from tools.verification.safediffcon.budget import training_forecast

    result = training_forecast(
        start=4100, total=7000, seconds_per_update=0.44, post_seconds=600, training_limit=4200
    )
    assert result["additional_per_side"] == 2900
    assert result["guarded_seconds"] == 3940
    with pytest.raises(TimeoutError):
        training_forecast(
            start=4100, total=20000, seconds_per_update=0.44, post_seconds=600, training_limit=4200
        )
    with pytest.raises(ValueError):
        training_forecast(
            start=4100, total=4000, seconds_per_update=0.44, post_seconds=600, training_limit=4200
        )


def test_continuation_rejects_changed_config_before_launch(tmp_path, monkeypatch):
    """冻结后改配置必须在启动任何计算之前失败。"""
    from tools.verification.safediffcon import continue_case

    work = tmp_path / "continuation"
    work.mkdir()
    (work / "burgers-training-freeze.json").write_text(
        json.dumps({"total": 5000, "reference_config_sha256": "frozen"})
    )
    (work / "burgers-reference-5000.yaml").write_text("changed: true")

    def forbidden(*args, **kwargs):
        pytest.fail("配置不符时不得启动子进程")

    monkeypatch.setattr(continue_case.subprocess, "run", forbidden)
    monkeypatch.setenv("PYTHONPATH", "before-test")
    with pytest.raises(ValueError, match="冻结配置改变"):
        continue_case.execute(tmp_path, "burgers", 5000)


@pytest.mark.parametrize("status,samples,diagnostic", [("failed", 50, False), ("passed", 4, True)])
def test_delivery_rejects_partial_or_diagnostic_results(tmp_path, status, samples, diagnostic):
    """少量诊断和失败结果不能混入正式50样本交付。"""
    from tools.verification.safediffcon.report import build_report

    for name in ["continuation", "short", "budget"]:
        (tmp_path / name).mkdir()
    (tmp_path / "continuation/burgers-final-acceptance.json").write_text(
        json.dumps({"status": status, "samples": samples, "diagnostic_only": diagnostic})
    )
    (tmp_path / "short/burgers-acceptance.json").write_text("{}")
    (tmp_path / "budget/burgers.json").write_text('{"seconds": 1, "runs": []}')
    with pytest.raises(ValueError, match="完整50样本"):
        build_report(tmp_path)
