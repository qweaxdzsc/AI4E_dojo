"""独立物理场工作区监督；VTK 对象绝不在工作区之间共享。"""

import multiprocessing as mp
import time
from threading import RLock
from uuid import uuid4

from infrastructure.process.channel import Channel
from infrastructure.process.supervisor import available_port, stop_process


class Sessions:
    """每个工作区一个 Trame 进程，心跳超时可回收。"""

    def __init__(self, maximum=4, ttl=900, idle=45):
        """配置会话上限、断连回收和满员时的短空闲回收。"""
        self.maximum, self.ttl, self.idle = maximum, ttl, idle
        self.items = {}
        self.lock = RLock()

    def create(self, context: dict, spec: dict) -> dict:
        """先启动并核验工作进程，失败不发布成功会话。"""
        from .worker import run

        with self.lock:
            self.reap()
            if len(self.items) >= self.maximum:
                self.reap_idle()
            if len(self.items) >= self.maximum:
                raise ValueError("phys_session_capacity")
            identity = uuid4().hex
            ctx = mp.get_context("spawn")
            parent, child = ctx.Pipe()
            port = available_port()
            secret = uuid4().hex
            process = ctx.Process(
                target=run, args=(child, context["bindings"], spec, port, secret), daemon=True
            )
            process.start()
            child.close()
            if not parent.poll(60):
                stop_process(process)
                parent.close()
                raise ValueError("phys_session_start_timeout")
            try:
                response = parent.recv()
            except (EOFError, OSError) as exc:
                stop_process(process)
                parent.close()
                raise ValueError("phys_worker_start_failed") from exc
            if response.get("error"):
                stop_process(process)
                parent.close()
                raise ValueError(response["error"])
            self.items[identity] = {
                "process": process,
                "channel": Channel(parent),
                "port": port,
                "secret": secret,
                "context": context,
                "last_seen": time.monotonic(),
            }
            return {
                "session_id": identity,
                "status": "ready",
                "snapshot": response["result"],
                "context_id": context["context_id"],
                "secret": secret,
            }

    def get(self, identity: str, context_id: str) -> dict:
        """每次调用绑定上下文，不能通过猜会话 ID 跨任务访问。"""
        with self.lock:
            item = self.items[identity]
            if item["context"]["context_id"] != context_id:
                raise ValueError("phys_session_context_mismatch")
            if not item["process"].is_alive():
                self.close(identity, context_id)
                raise ValueError("phys_session_lost")
            item["last_seen"] = time.monotonic()
            return item

    def command(self, identity: str, context_id: str, body: dict) -> dict:
        """脚本和页面使用同一个工作区命令通道。"""
        if body.get("operation") == "append_sources":
            raise ValueError("trusted_source_binding_required")
        item = self.get(identity, context_id)
        try:
            return item["channel"].call(body)
        except (TimeoutError, EOFError, BrokenPipeError, RuntimeError):
            self.close(identity, context_id)
            raise

    def close(self, identity: str, context_id: str) -> dict:
        """关闭并回收对应工作区，保存配置不受影响。"""
        with self.lock:
            item = self.items.get(identity)
            if item:
                if item["context"]["context_id"] != context_id:
                    raise ValueError("phys_session_context_mismatch")
                self.items.pop(identity)
                stop_process(item["process"])
                item["channel"].connection.close()
        return {"session_id": identity, "status": "closed"}

    def reap(self) -> None:
        """心跳只延长活动会话，断连十五分钟后释放资源。"""
        for identity, item in list(self.items.items()):
            if time.monotonic() - item["last_seen"] > self.ttl or not item["process"].is_alive():
                self.close(identity, item["context"]["context_id"])

    def reap_idle(self) -> None:
        """满员时回收已无心跳的短空闲会话，活动页面的三十秒续约不受影响。"""
        for identity, item in list(self.items.items()):
            if time.monotonic() - item["last_seen"] > self.idle or not item["process"].is_alive():
                self.close(identity, item["context"]["context_id"])

    def shutdown(self) -> None:
        """服务退出清理全部本实例工作进程。"""
        for identity, item in list(self.items.items()):
            self.close(identity, item["context"]["context_id"])
