"""持久预算的失败、重试、恢复与禁止启动行为。"""

import json
import subprocess

import pytest

from tools.verification.geotransolver.budget import Budget


def test_failed_retry_and_training_cutoff(tmp_path, monkeypatch):
    clock = iter([0, 7, 10, 14])

    class Child:
        def __init__(self, *a, **kw):
            pass

        def wait(self, timeout):
            return 1

    monkeypatch.setattr(subprocess, "Popen", Child)
    path = tmp_path / "ledger.json"
    budget = Budget(path, limit=20, training_limit=10, clock=lambda: next(clock))
    assert budget.run(["failed"], label="first") == 1
    assert budget.run(["retry"], label="retry") == 1
    assert json.loads(path.read_text())["seconds"] == 11
    with pytest.raises(TimeoutError):
        budget.run(["training"], label="new", training=True)
    state = json.loads(path.read_text())
    state["seconds"] = 20
    path.write_text(json.dumps(state))
    with pytest.raises(TimeoutError):
        budget.run(["evaluation"], label="eval")


def test_unresolved_active_process_blocks(tmp_path):
    path = tmp_path / "ledger.json"
    path.write_text(json.dumps({"seconds": 3, "active": {"label": "orphan"}, "runs": []}))
    with pytest.raises(RuntimeError, match="核实"):
        Budget(path).run(["never"], label="x")


def test_cooperative_overrun_finishes_and_blocks_next_run(tmp_path, monkeypatch):
    times = iter([0, 15])

    class Child:
        def __init__(self, *args, **kwargs):
            pass

        def wait(self, timeout):
            assert timeout is None
            return 0

    monkeypatch.setattr(subprocess, "Popen", Child)
    path = tmp_path / "ledger.json"
    budget = Budget(path, limit=10, cooperative=True, clock=lambda: next(times))
    assert budget.run(["active"], label="complete") == 0
    assert json.loads(path.read_text())["runs"][0]["overrun_seconds"] == 5
    with pytest.raises(TimeoutError):
        budget.run(["next"], label="blocked")


def test_hard_deadline_and_cancellation_are_charged(tmp_path, monkeypatch):
    import os
    import signal

    clocks = iter([0, 9, 11])
    calls = []

    class Child:
        pid = 123
        attempts = 0

        def __init__(self, *a, **kw):
            pass

        def poll(self):
            return None

        def wait(self, timeout=None):
            self.attempts += 1
            if self.attempts < 3:
                raise subprocess.TimeoutExpired("fake", timeout)
            return -9

    monkeypatch.setattr(subprocess, "Popen", Child)
    monkeypatch.setattr(os, "killpg", lambda pid, sig: calls.append(sig))
    path = tmp_path / "budget.json"
    with pytest.raises(subprocess.TimeoutExpired):
        Budget(path, limit=12, clock=lambda: next(clocks)).run(["fake"], label="deadline")
    assert calls == [signal.SIGTERM, signal.SIGKILL]
    state = json.loads(path.read_text())
    assert state["seconds"] == 11
    assert state["runs"][0]["status"] == "deadline"
    assert "active" not in state

    clocks = iter([0, 2])

    class Cancelled(Child):
        def wait(self, timeout=None):
            self.attempts += 1
            if self.attempts == 1:
                raise KeyboardInterrupt
            return -15

    monkeypatch.setattr(subprocess, "Popen", Cancelled)
    with pytest.raises(KeyboardInterrupt):
        Budget(tmp_path / "cancel.json", clock=lambda: next(clocks)).run(["fake"], label="cancel")
    assert json.loads((tmp_path / "cancel.json").read_text())["seconds"] == 2
