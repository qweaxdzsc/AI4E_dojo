"""跨进程持久累计计算账本；失败、重试、恢复共用预算及硬截止。"""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import signal
import subprocess
import time
from pathlib import Path

DEFAULT_LEDGER = Path(
    "/Users/zonghui/work/project_simulation/dojo_train/geotransolver/compute-budget.json"
)


class Budget:
    """一次仅允许一个计费子进程，默认180分钟；160分钟后拒绝新训练。"""

    def __init__(
        self, path, *, limit=10800, training_limit=9600, clock=time.monotonic, cooperative=False
    ):
        self.path, self.limit, self.training_limit, self.clock = (
            Path(path),
            limit,
            training_limit,
            clock,
        )
        self.cooperative = cooperative

    def run(self, command, *, label, training=False, env=None):
        """启动进程组并计入全部墙钟耗时；预算耗尽终止整组并留下失败记录。"""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.with_suffix(".lock").open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            state = (
                json.loads(self.path.read_text())
                if self.path.exists()
                else {"seconds": 0.0, "runs": []}
            )
            if state.get("active"):
                raise RuntimeError("上次计费进程异常退出，须核实实际耗时后续接，禁止漏记")
            remaining = self.limit - state["seconds"]
            if remaining <= 0 or (training and state["seconds"] >= self.training_limit):
                raise TimeoutError("累计预算禁止启动")
            started = self.clock()
            state["active"] = {"label": label, "started_unix": time.time()}
            self.path.write_text(json.dumps(state, indent=2))
            process = None
            status = "failed"
            try:
                process = subprocess.Popen(command, env=env, start_new_session=True)
                # 预留独立Task worker的公开停止及检查点交付时间。
                result = process.wait(
                    timeout=None if self.cooperative else max(0.01, remaining - 12)
                )
                status = "passed" if result == 0 else "failed"
                return result
            except subprocess.TimeoutExpired:
                # 先请求受监督脚本收尾，硬截止前仍存活则终止整组。
                if process and process.poll() is None:
                    os.killpg(process.pid, signal.SIGTERM)
                    try:
                        process.wait(
                            timeout=max(0.01, min(10, remaining - (self.clock() - started)))
                        )
                    except subprocess.TimeoutExpired:
                        os.killpg(process.pid, signal.SIGKILL)
                        process.wait()
                status = "deadline"
                raise
            except BaseException:
                if process and process.poll() is None:
                    os.killpg(process.pid, signal.SIGTERM)
                    try:
                        process.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        os.killpg(process.pid, signal.SIGKILL)
                        process.wait()
                raise
            finally:
                elapsed = self.clock() - started
                state["seconds"] += elapsed
                state["runs"].append(
                    {
                        "label": label,
                        "seconds": elapsed,
                        "status": status,
                        "overrun_seconds": max(0, elapsed - remaining),
                    }
                )
                state.pop("active", None)
                self.path.write_text(json.dumps(state, indent=2) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument("--label", required=True)
    parser.add_argument("--training", action="store_true")
    parser.add_argument("--cooperative", action="store_true")
    parser.add_argument("command", nargs=argparse.REMAINDER)
    a = parser.parse_args()
    raise SystemExit(
        Budget(a.ledger, cooperative=a.cooperative).run(
            a.command, label=a.label, training=a.training
        )
    )
