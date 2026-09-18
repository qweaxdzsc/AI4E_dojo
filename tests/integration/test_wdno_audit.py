"""收尾审计观察已关闭账本，同时仍计时、限时且阻止并发计算。"""

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_audit_observes_closed_state_and_records_cost(tmp_path):
    ledger = tmp_path / "budget.json"
    ledger.write_text(json.dumps({"seconds": 1, "runs": []}))
    code = 'import json,sys; s=json.load(open(sys.argv[1])); assert not s["runs"]'
    result = subprocess.run(
        [
            "uv",
            "run",
            "--no-project",
            "--python",
            sys.executable,
            "python",
            "-m",
            "tools.verification.wdno.audit",
            "--ledger",
            str(ledger),
            "--",
            "uv",
            "run",
            "--no-project",
            "--python",
            sys.executable,
            "python",
            "-c",
            code,
            str(ledger),
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    state = json.loads(ledger.read_text())
    assert state["seconds"] > 1 and state["runs"][0]["closed_ledger_audit"]
    assert state["runs"][0]["status"] == "success"


def test_audit_times_out_and_accounts_failure(tmp_path):
    ledger = tmp_path / "budget.json"
    ledger.write_text(json.dumps({"seconds": 10739.9, "runs": []}))
    result = subprocess.run(
        [
            "uv",
            "run",
            "--no-project",
            "--python",
            sys.executable,
            "python",
            "-m",
            "tools.verification.wdno.audit",
            "--ledger",
            str(ledger),
            "--",
            "uv",
            "run",
            "--no-project",
            "--python",
            sys.executable,
            "python",
            "-c",
            "import time; time.sleep(30)",
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=10,
        env={**os.environ},
    )
    assert result.returncode != 0
    state = json.loads(ledger.read_text())
    assert 10739.9 < state["seconds"] < 10800 and state["runs"][0]["status"] == "failed"
