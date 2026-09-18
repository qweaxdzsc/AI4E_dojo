"""组合实验累计限时；重试也计入同一持久化账本。"""

import argparse
import fcntl
import json
import os
import signal
import subprocess
import time
from pathlib import Path


def run_budgeted(ledger, command, *, credit_seconds=0.0, soft=10500.0, hard=10800.0):
    """独占组合账本，175 分钟拒绝新计算，180 分钟终止进程组。"""
    ledger = Path(ledger)
    ledger.parent.mkdir(parents=True, exist_ok=True)
    with ledger.with_suffix(".lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        state = (
            json.loads(ledger.read_text())
            if ledger.exists()
            else {"seconds": credit_seconds, "runs": []}
        )
        if any(entry.get("status") == "running" for entry in state["runs"]):
            raise RuntimeError("上次监督进程未正常收尾，须核实并补记累计时间后继续")
        if state["seconds"] >= soft:
            raise TimeoutError("累计预算不允许新计算")
        start = time.time()
        monotonic_start = time.monotonic()
        entry = {"command": command, "started": start, "status": "running"}
        state["runs"].append(entry)

        def save():
            temporary = ledger.with_suffix(".tmp")
            temporary.write_text(json.dumps(state, indent=2))
            temporary.replace(ledger)

        save()
        process = None
        code = None
        soft_stopped = False
        try:
            process = subprocess.Popen(command, start_new_session=True)
            while process.poll() is None:
                elapsed = time.monotonic() - monotonic_start
                if state["seconds"] + elapsed >= soft and not soft_stopped:
                    os.killpg(process.pid, signal.SIGINT)
                    soft_stopped = True
                if state["seconds"] + elapsed >= hard:
                    os.killpg(process.pid, signal.SIGTERM)
                    try:
                        process.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        os.killpg(process.pid, signal.SIGKILL)
                    raise TimeoutError("累计 180 分钟终止")
                try:
                    process.wait(
                        timeout=min(
                            0.5,
                            max(
                                0.001, (hard if soft_stopped else soft) - state["seconds"] - elapsed
                            ),
                        )
                    )
                except subprocess.TimeoutExpired:
                    pass
            code = process.returncode
            return code
        finally:
            if process is not None and process.poll() is None:
                os.killpg(process.pid, signal.SIGTERM)
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()
            elapsed = time.monotonic() - monotonic_start
            state["seconds"] += elapsed
            entry.update(
                seconds=elapsed,
                returncode=code,
                status="success" if code == 0 and not soft_stopped else "failed",
                soft_stopped=soft_stopped,
            )
            save()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", required=True)
    parser.add_argument("--credit-seconds", type=float, default=0.0)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not command:
        parser.error("缺少计算命令")
    raise SystemExit(run_budgeted(args.ledger, command, credit_seconds=args.credit_seconds))
