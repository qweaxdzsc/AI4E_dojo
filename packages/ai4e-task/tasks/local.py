"""本地子进程与身份核对，不凭裸 PID 发送停止信号。"""

import os
import signal
import subprocess
import sys
from pathlib import Path

CHILDREN: dict[str, subprocess.Popen] = {}


def start(request: Path) -> int:
    """脱离调用者会话启动 worker，控制日志不写入 core run 目录。"""
    with (request.parent / "worker.log").open("ab") as log:
        proc = subprocess.Popen(
            [sys.executable, "-m", "ai4e_task.tasks.worker", str(request)],
            stdin=subprocess.DEVNULL,
            stdout=log,
            stderr=log,
            start_new_session=True,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )
    CHILDREN[str(request)] = proc
    return proc.pid


def alive(pid: int | None, request: Path) -> bool:
    """核对进程命令包含精确请求路径，排除 PID 重用及僵尸进程。"""
    child = CHILDREN.get(str(request))
    if child is not None:
        if child.poll() is None:
            return child.pid == pid
        CHILDREN.pop(str(request), None)
        return False
    if not pid:
        return False
    try:
        result = subprocess.run(
            ["ps", "-p", str(pid), "-o", "stat=", "-o", "args="],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return False
    text = result.stdout.strip()
    return bool(
        text
        and not text.startswith("Z")
        and "ai4e_task.tasks.worker" in text
        and str(request) in text
    )


def terminate(pid: int, request: Path):
    """再次核验后请求进程组停止，不自动强杀。"""
    if not alive(pid, request):
        raise RuntimeError("process_identity_unconfirmed")
    child = CHILDREN.get(str(request))
    os.killpg(pid, signal.SIGTERM)
    return child
