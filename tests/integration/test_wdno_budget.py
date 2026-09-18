"""三小时累计成本不因失败或下一次命令重置。"""

import json
import sys

import pytest

from tools.verification.gencp.budget import run_budgeted
from tools.verification.wdno.budget import continue_budget, limits


def test_continuation_requires_existing_ledger(tmp_path):
    ledger = tmp_path / "misspelled.json"
    with pytest.raises(FileNotFoundError):
        continue_budget(ledger, [sys.executable, "-c", "pass"])
    assert not ledger.exists()


def test_continuation_keeps_existing_credit(tmp_path):
    ledger = tmp_path / "budget.json"
    ledger.write_text(json.dumps({"seconds": 100, "runs": []}))
    assert continue_budget(ledger, [sys.executable, "-c", "pass"]) == 0
    state = json.loads(ledger.read_text())
    assert state["seconds"] >= 100 and state["runs"][-1]["status"] == "success"


def test_deadline_includes_termination_grace():
    assert limits(100) == (10740, 10790)
    assert limits(100)[1] + 3 < 10800
    for value in (-1, 10740, float("nan"), float("inf")):
        with pytest.raises(TimeoutError):
            limits(value)


def test_failure_and_retry_share_ledger(tmp_path):
    ledger = tmp_path / "budget.json"
    assert (
        run_budgeted(
            ledger,
            [sys.executable, "-c", "raise SystemExit(2)"],
            credit_seconds=10,
            soft=20,
            hard=21,
        )
        == 2
    )
    first = json.loads(ledger.read_text())["seconds"]
    assert (
        run_budgeted(ledger, [sys.executable, "-c", "pass"], credit_seconds=0, soft=20, hard=21)
        == 0
    )
    state = json.loads(ledger.read_text())
    assert state["seconds"] >= first >= 10
    assert [r["status"] for r in state["runs"]] == ["failed", "success"]


def test_pending_ledger_is_not_restarted(tmp_path):
    ledger = tmp_path / "budget.json"
    ledger.write_text(json.dumps({"seconds": 1, "runs": [{"status": "running"}]}))
    with pytest.raises(RuntimeError, match="未正常收尾"):
        run_budgeted(ledger, [sys.executable, "-c", "pass"])


def test_hard_deadline_terminates_an_interrupt_ignoring_worker(tmp_path):
    ledger = tmp_path / "budget.json"
    command = [
        sys.executable,
        "-c",
        "import signal,time; signal.signal(signal.SIGINT,signal.SIG_IGN); time.sleep(30)",
    ]
    with pytest.raises(TimeoutError):
        run_budgeted(ledger, command, soft=0.3, hard=0.6)
    state = json.loads(ledger.read_text())
    assert state["seconds"] >= 0.6
    assert state["runs"][-1]["soft_stopped"] is True
    assert state["runs"][-1]["status"] == "failed"
