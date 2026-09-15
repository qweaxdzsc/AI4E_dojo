"""Vis 专属进程与 HTTP 客户端；宿主不导入可视化后端。"""

import os
import secrets
import socket
import subprocess
import sys
import time
from threading import RLock

import httpx


class VisClient:
    """惰性启动可视化服务，显式传递每次请求的上下文。"""

    def __init__(self, settings):
        """运行缓存独立于 task 配置与训练 run。"""
        self.settings = settings
        self.process = None
        self.url = None
        self.token = secrets.token_urlsafe(32)
        self.lock = RLock()
        self.log = None

    def start(self):
        """在独立进程内加载迁入 Vis，等待技术健康检查。"""
        with self.lock:
            if self.process and self.process.poll() is None:
                return
            with socket.socket() as sock:
                sock.bind(("127.0.0.1", 0))
                port = sock.getsockname()[1]
            root = self.settings.root / "vis-runtime"
            root.mkdir(parents=True, exist_ok=True)
            self.url = f"http://127.0.0.1:{port}"
            self.log = (root / "service.log").open("a")
            env = dict(os.environ, AI4E_VIS_CONTROL_TOKEN=self.token)
            self.process = subprocess.Popen(
                [
                    sys.executable,
                    "-m",
                    "ai4e_viz.cli",
                    "--port",
                    str(port),
                    "--runtime-root",
                    str(root),
                ],
                env=env,
                stdout=self.log,
                stderr=self.log,
            )
            for _ in range(300):
                if self.process.poll() is not None:
                    raise RuntimeError("vis_service_start_failed")
                try:
                    response = httpx.get(self.url + "/api/phys/capabilities", timeout=0.5)
                    if response.status_code == 200:
                        return
                except httpx.HTTPError:
                    pass
                time.sleep(0.1)
            self.close()
            raise RuntimeError("vis_service_start_timeout")

    def request(self, method, path, body=None):
        """固定回环服务，不接受浏览器控制目标 URL。"""
        self.start()
        response = httpx.request(
            method, self.url + path, json=body, headers={"x-vis-control": self.token}, timeout=150
        )
        if not response.is_success:
            message = response.json().get("detail", "vis_request_failed")
            if response.status_code == 404:
                raise KeyError(str(message))
            raise ValueError(str(message))
        return response.json()

    def close(self):
        """服务退出有界回收，Vis 自己关闭所属会话。"""
        if self.process and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(10)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(3)
        if self.log:
            self.log.close()
