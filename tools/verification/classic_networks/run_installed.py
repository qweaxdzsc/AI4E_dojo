"""在统一预算锁内串行执行六个已安装案例，失败保留并清理子进程组。"""

import argparse
import json
import os
import shutil
import signal
import subprocess
import time
from pathlib import Path

from tools.verification.classic_networks.budget import BudgetLedger

CASES = (
    ("classic_networks.darcy", "darcy", "mlp-darcy"),
    ("classic_networks.shapenet_volume", "shapenet_volume", "mlp-shapenet_volume"),
    ("classic_networks.double_cylinder", "double_cylinder", "rnn-double_cylinder"),
    ("recipe_extensions.network_composition.resunet", "darcy", "unet-darcy"),
    ("recipe_extensions.network_composition.unet_transformer", "darcy", "transformer-darcy"),
    ("recipe_extensions.network_composition.cnn_rnn", "double_cylinder", "rnn-double_cylinder"),
)


def stop(process):
    """给验证器清理Task子进程的机会，超时再终止本次独立进程组。"""
    if process.poll() is None:
        os.killpg(process.pid, signal.SIGTERM)
        try:
            process.wait(timeout=12)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait(timeout=5)


def main():
    """实际消费wheel而非source overlay；与源训练共享持久预算账本。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    ledger = BudgetLedger(root / "budget")
    preparation = json.loads((root / "evidence/preparation.json").read_text())
    summary_path = root / "evidence/installed.json"
    summary = json.loads(summary_path.read_text()) if summary_path.exists() else {}
    runtime = root / "installed-validation"
    runtime.mkdir(exist_ok=True)
    shutil.copy2(Path(__file__).with_name("installed_replay.py"), runtime / "installed_replay.py")
    environment = {
        **os.environ,
        "PYTHONPATH": "",
        "PYTHONDONTWRITEBYTECODE": "1",
        "UV_CACHE_DIR": str(root / "cache"),
        "TMPDIR": str(root / "tmp"),
    }
    for identity, case, budget in CASES:
        if summary.get(identity, {}).get("status") == "passed":
            continue
        destination = runtime / (identity + "-" + str(time.time_ns()))
        log = destination.with_suffix(".log")
        process = None
        try:
            with ledger.measure(budget, "installed-" + identity, training=True):
                command = [
                    "uv",
                    "run",
                    "--no-project",
                    "--no-sync",
                    "--python",
                    str(root / "installed/bin/python"),
                    str(runtime / "installed_replay.py"),
                    "--root",
                    str(destination),
                    "--environment",
                    str(root / "installed"),
                    "--case-id",
                    identity,
                    "--preparation",
                    preparation[case]["prepared"],
                    "--seconds",
                    str(ledger.remaining(budget) - 30),
                    "--budget-identity",
                    budget,
                    "--device",
                    "cpu",
                    "--with-task",
                ]
                with log.open("w") as stream:
                    process = subprocess.Popen(
                        command,
                        cwd=runtime,
                        env=environment,
                        stdout=stream,
                        stderr=subprocess.STDOUT,
                        start_new_session=True,
                    )
                    try:
                        code = process.wait(timeout=ledger.remaining(budget) - 10)
                    finally:
                        stop(process)
                if code:
                    raise RuntimeError(f"安装案例失败: {log}")
                report = json.loads((destination / "report.json").read_text())
                if report["status"] != "passed":
                    raise AssertionError("安装案例未完整通过")
                summary[identity] = {
                    "status": "passed",
                    "report": str(destination / "report.json"),
                    "budget_identity": budget,
                    "elapsed_seconds": report["elapsed_seconds"],
                }
        except BaseException as exc:
            if process is not None:
                stop(process)
            summary[identity] = {"status": "failed", "error": repr(exc), "log": str(log)}
            summary_path.write_text(json.dumps(summary, indent=2))
            raise
        summary_path.write_text(json.dumps(summary, indent=2))
        print("INSTALLED COMPLETE", identity, flush=True)


if __name__ == "__main__":
    main()
