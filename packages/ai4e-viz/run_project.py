#!/usr/bin/env python3
"""Start and manage the complete AI4E_Vis application locally.

The launcher keeps each service in its own detached process group so the app
continues running after the terminal or Codex task that started it closes.
Only processes started by this launcher are stopped by ``stop``.
"""

from __future__ import annotations

import sys
from pathlib import Path
# 单层包内 inspect 与标准库同名，脚本运行时不得把源码包根当顶层模块搜索目录。
sys.path[:] = [entry for entry in sys.path if Path(entry or ".").resolve() != Path(__file__).resolve().parent]

import argparse
import json
import os
import signal
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent
BACKEND = ROOT / "backend"
FRONTEND = ROOT / "frontend"
PYTHON = Path(sys.executable)
RUNTIME = Path(os.environ.get("AI4E_VIS_RUNTIME_DIR", Path.home()/".cache"/"ai4e-vis")) / "runtime"
STATE_FILE = RUNTIME / "services.json"


@dataclass(frozen=True)
class Service:
    name: str
    label: str
    port: int
    cwd: Path
    command: tuple[str, ...]
    health_url: str


SERVICES = (
    Service(
        "api", "解析 / 推荐 API", 8091, BACKEND,
        (str(PYTHON), "-m", "server.dev", "--port", "8091"),
        "http://127.0.0.1:8091/api/health",
    ),
    Service(
        "trame", "Trame + vtk.js", 8090, BACKEND,
        (str(PYTHON), "-m", "modules.visPhysField.trameServer", "--port", "8090"),
        "http://127.0.0.1:8090/",
    ),
    Service(
        "frontend", "React + Vite", 5275, FRONTEND,
        ("npm", "run", "dev", "--", "--host", "127.0.0.1", "--port", "5275"),
        "http://127.0.0.1:5275/",
    ),
)


def _load_state() -> dict[str, dict]:
    try:
        value = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _save_state(state: dict[str, dict]) -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def _pid_alive(pid: int | None) -> bool:
    if not pid:
        return False
    try:
        os.kill(pid, 0)
        return True
    except (ProcessLookupError, PermissionError):
        return False


def _port_open(port: int) -> bool:
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=0.35):
            return True
    except OSError:
        return False


def _http_status(url: str) -> int | None:
    try:
        with urllib.request.urlopen(url, timeout=1.2) as response:
            return response.status
    except urllib.error.HTTPError as error:
        return error.code
    except (OSError, urllib.error.URLError):
        return None


def _http_json(url: str) -> dict:
    """读取本机健康端点JSON；不可达或非对象响应统一返回空字典。"""

    try:
        with urllib.request.urlopen(url, timeout=1.2) as response:
            payload = json.loads(response.read().decode("utf-8"))
        return payload if isinstance(payload, dict) else {}
    except (OSError, urllib.error.URLError, json.JSONDecodeError):
        return {}


def _compatible_running_service(service: Service) -> bool:
    """确认占用端口的API确实是当前模块化入口，而不是遗留 ``api_app.py``。"""

    if service.name != "api":
        return True
    health = _http_json(service.health_url)
    return health.get("entrypoint") == "server.api" and health.get("runtime_layout") == "var-v1"


def _tail(path: Path, lines: int = 18) -> str:
    try:
        return "\n".join(path.read_text(encoding="utf-8", errors="replace").splitlines()[-lines:])
    except FileNotFoundError:
        return "（没有日志输出）"


def _preflight() -> None:
    missing = []
    if not PYTHON.is_file():
        missing.append(f"后端虚拟环境不存在：{PYTHON}")
    node_modules = FRONTEND / "node_modules"
    vite_bin = node_modules / ".bin" / "vite"
    if not node_modules.is_dir():
        missing.append(
            "前端依赖不存在：请按 PORTABLE_STARTUP_GUIDE.zh-CN.md 第 5.1 节"
            "在 frontend 中完成 npm ci"
        )
    elif not vite_bin.is_file():
        missing.append(
            "前端依赖不完整（缺少 node_modules/.bin/vite）：请按启动文档第 10.2–10.3 节"
            "修复 npm 缓存或锁文件后重新安装"
        )
    if missing:
        raise RuntimeError("\n".join(missing))


def _rollback_started(started: list[tuple[Service, subprocess.Popen, Path]], state: dict[str, dict]) -> None:
    """Avoid leaving a new half-started stack after a startup failure."""
    for service, process, _ in reversed(started):
        if process.poll() is None:
            try:
                os.killpg(process.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
        state.pop(service.name, None)
    _save_state(state)


def start(timeout: float = 30.0) -> int:
    _preflight()
    RUNTIME.mkdir(parents=True, exist_ok=True)
    state = _load_state()
    started: list[tuple[Service, subprocess.Popen, Path]] = []

    for service in SERVICES:
        previous = state.get(service.name, {})
        if _port_open(service.port):
            if not _compatible_running_service(service):
                print(
                    f"[error] {service.label} 端口 {service.port} 被旧版或不兼容进程占用；"
                    "请先停止该进程，避免连接 backend/state 等废弃运行库。",
                    file=sys.stderr,
                )
                _rollback_started(started, state)
                return 1
            ownership = "本启动器管理" if _pid_alive(previous.get("pid")) else "已有外部进程"
            print(f"[ready] {service.label:<18} 127.0.0.1:{service.port}（{ownership}）")
            continue

        log_path = RUNTIME / f"{service.name}.log"
        log_handle = log_path.open("a", encoding="utf-8")
        log_handle.write(f"\n\n=== start {time.strftime('%Y-%m-%d %H:%M:%S')} ===\n")
        log_handle.flush()
        process = subprocess.Popen(
            service.command,
            cwd=service.cwd,
            stdout=log_handle,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        log_handle.close()
        state[service.name] = {
            "pid": process.pid,
            "port": service.port,
            "log": str(log_path),
            "started_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        }
        _save_state(state)
        started.append((service, process, log_path))
        print(f"[start] {service.label:<18} pid={process.pid}")

    deadline = time.monotonic() + timeout
    pending = {service.name: (service, process, log_path) for service, process, log_path in started}
    while pending and time.monotonic() < deadline:
        for name, (service, process, log_path) in list(pending.items()):
            if _port_open(service.port):
                print(f"[ready] {service.label:<18} {service.health_url}")
                pending.pop(name)
            elif process.poll() is not None:
                print(f"[error] {service.label} 启动失败（code={process.returncode}）", file=sys.stderr)
                print(_tail(log_path), file=sys.stderr)
                pending.pop(name)
                _rollback_started(started, state)
                return 1
        time.sleep(0.25)

    if pending:
        for service, _, log_path in pending.values():
            print(f"[error] {service.label} 在 {timeout:g}s 内未监听 {service.port}", file=sys.stderr)
            print(_tail(log_path), file=sys.stderr)
        _rollback_started(started, state)
        return 1

    print("\n项目已启动：")
    print("  http://127.0.0.1:5275/")
    print("  http://127.0.0.1:5275/#/assets/A-1114")
    print(f"日志目录：{RUNTIME}")
    return 0


def status() -> int:
    state = _load_state()
    all_ready = True
    for service in SERVICES:
        record = state.get(service.name, {})
        port_ready = _port_open(service.port)
        http_status = _http_status(service.health_url) if port_ready else None
        owner = f"pid={record.get('pid')}" if _pid_alive(record.get("pid")) else "external/unmanaged"
        if port_ready:
            print(f"[ready] {service.label:<18} port={service.port} http={http_status or '-'} {owner}")
        else:
            print(f"[down]  {service.label:<18} port={service.port}")
            all_ready = False
    return 0 if all_ready else 1


def stop() -> int:
    state = _load_state()
    for service in reversed(SERVICES):
        record = state.get(service.name, {})
        pid = record.get("pid")
        if not _pid_alive(pid):
            state.pop(service.name, None)
            continue
        try:
            os.killpg(pid, signal.SIGTERM)
            print(f"[stop]  {service.label:<18} pid={pid}")
        except ProcessLookupError:
            pass
        state.pop(service.name, None)
    _save_state(state)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="AI4E_Vis 本地项目启动管理器")
    parser.add_argument("command", nargs="?", choices=("start", "status", "stop", "restart"), default="start")
    parser.add_argument("--timeout", type=float, default=30.0, help="等待每个服务启动的最长秒数")
    args = parser.parse_args()
    if args.command == "status":
        return status()
    if args.command == "stop":
        return stop()
    if args.command == "restart":
        stop()
        time.sleep(0.8)
    return start(args.timeout)


if __name__ == "__main__":
    raise SystemExit(main())
