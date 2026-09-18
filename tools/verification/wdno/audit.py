"""已关闭计算账本的最终测试审计；限定超时并在结束后记入同一账本。"""

import argparse
import fcntl
import json
import os
import signal
import subprocess
import time
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not command:
        parser.error("缺少测试命令")
    with args.ledger.with_suffix(".lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        state = json.loads(args.ledger.read_text())
        if any(entry["status"] == "running" for entry in state["runs"]):
            raise RuntimeError("数值计算仍在运行，不能进行最终关闭审计")
        # 审计必须观察已收尾的计算账本，不能因审计本身而制造running标记。
        # 持有同一独占锁、进程组硬超时，finally将审计耗时追加；不重置预算。
        timeout = min(180, 10740 - state["seconds"])
        if timeout <= 0:
            raise TimeoutError("原三小时账本不足以开始审计")
        start, started = time.monotonic(), time.time()
        code, process = None, None
        try:
            process = subprocess.Popen(command, start_new_session=True)
            try:
                code = process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGTERM)
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()
                raise TimeoutError("最终测试审计超时") from None
        finally:
            if process is not None and process.poll() is None:
                os.killpg(process.pid, signal.SIGTERM)
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()
            elapsed = time.monotonic() - start
            state["seconds"] += elapsed
            state["runs"].append(
                {
                    "command": command,
                    "started": started,
                    "seconds": elapsed,
                    "status": "success" if code == 0 else "failed",
                    "returncode": code,
                    "closed_ledger_audit": True,
                }
            )
            temporary = args.ledger.with_suffix(".tmp")
            temporary.write_text(json.dumps(state, indent=2))
            temporary.replace(args.ledger)
        return code


if __name__ == "__main__":
    raise SystemExit(main())
