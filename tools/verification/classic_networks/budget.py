"""跨进程校验预算账本与单训练互斥；不写入框架运行目录。

默认硬时限依赖 POSIX 主线程 SIGALRM。子进程训练须由调用方提供超时清理
回调，停止整组工作进程；本工具不猜测或终止用户其他进程。
"""

from __future__ import annotations

import fcntl
import hashlib
import json
import math
import os
import signal
import threading
import time
import uuid
from contextlib import contextmanager
from pathlib import Path


class BudgetExceeded(RuntimeError):
    """组合累计计算预算不足或计时范围触及硬截止。"""


class TrainingBusy(RuntimeError):
    """其他进程持有串行训练锁。"""


class BudgetLedger:
    """每组合默认10800秒，计时/重试/人工分摊使用同一持久账本。"""

    def __init__(self, root, *, limit_seconds=10800.0, clock=time.monotonic, wall_clock=time.time):
        if not math.isfinite(limit_seconds) or not 0 < limit_seconds <= 10800:
            raise ValueError("预算上限必须在0到10800秒之间")
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.limit_seconds = float(limit_seconds)
        self.clock, self.wall_clock = clock, wall_clock
        self.path = self.root / "budget.json"

    @contextmanager
    def _file_lock(self, name, *, blocking=True):
        with (self.root / name).open("a+") as handle:
            try:
                fcntl.flock(handle, fcntl.LOCK_EX | (0 if blocking else fcntl.LOCK_NB))
            except BlockingIOError as exc:
                raise TrainingBusy(f"已有工作持有锁: {name}") from exc
            try:
                yield
            finally:
                fcntl.flock(handle, fcntl.LOCK_UN)

    @contextmanager
    def training_lock(self):
        """整个验证根共享单训练锁；冲突立即报错，不排队偷偷并发。"""
        with self._file_lock("training.lock", blocking=False):
            yield

    @contextmanager
    def _combo_lock(self, combo):
        if not isinstance(combo, str) or not combo:
            raise ValueError("combo 必须是非空身份字符串")
        name = "combo-" + hashlib.sha256(combo.encode()).hexdigest() + ".lock"
        with self._file_lock(name, blocking=False):
            yield

    def _read(self):
        if not self.path.exists():
            return {"version": 1, "limit_seconds": self.limit_seconds, "combinations": {}}
        record = json.loads(self.path.read_text())
        if record.get("version") != 1 or record.get("limit_seconds") != self.limit_seconds:
            raise ValueError("预算账本版本或上限不一致；禁止重建账本清空累计耗时")
        return record

    def _write(self, record):
        temporary = self.path.with_name(f"budget-{uuid.uuid4().hex}.tmp")
        try:
            with temporary.open("w") as output:
                json.dump(record, output, ensure_ascii=False, indent=2)
                output.flush()
                os.fsync(output.fileno())
            os.replace(temporary, self.path)
        finally:
            temporary.unlink(missing_ok=True)

    @staticmethod
    def _entry(record, combo):
        return record["combinations"].setdefault(
            combo, {"spent_seconds": 0.0, "events": [], "active": None}
        )

    def snapshot(self):
        """读回可审计账本，不隐式改写运行或旧记录。"""
        with self._file_lock("ledger.lock"):
            return self._read()

    def remaining(self, combo):
        """返回剩余秒数，包含尚未退出的持久化计时范围。"""
        with self._file_lock("ledger.lock"):
            record = self._read()
            entry = record["combinations"].get(combo, {})
            spent = entry.get("spent_seconds", 0.0)
            if entry.get("active"):
                spent += max(0.0, self.wall_clock() - entry["active"]["started_at"])
            return max(0.0, self.limit_seconds - spent)

    def _recover_orphan(self, entry):
        # 已持有组合文件锁，旧active不可能仍由遵守协议的活跃范围持有。
        if entry["active"]:
            active = entry["active"]
            seconds = max(0.0, self.wall_clock() - active["started_at"])
            entry["spent_seconds"] += seconds
            entry["events"].append(
                {**active, "seconds": seconds, "status": "orphan_conservative_charge"}
            )
            entry["active"] = None

    def record_charge(self, combo, phase, seconds, *, details=None):
        """计入共享准备等外部实测分摊；超限仍保留实际账目并报错。"""
        if not math.isfinite(seconds) or seconds < 0:
            raise ValueError("分摊耗时必须是有限非负数")
        with self._combo_lock(combo), self._file_lock("ledger.lock"):
            record = self._read()
            entry = self._entry(record, combo)
            self._recover_orphan(entry)
            entry["spent_seconds"] += float(seconds)
            entry["events"].append(
                {"phase": phase, "seconds": float(seconds), "status": "charged", "details": details}
            )
            self._write(record)
            exceeded = entry["spent_seconds"] >= self.limit_seconds
        if exceeded:
            raise BudgetExceeded(f"{combo} 已耗尽累计预算")

    @contextmanager
    def measure(self, combo, phase, *, training=False, on_timeout=None):
        """计时finally持久写账；异常仍计费，主线程计时器执行硬截止。

        若范围启动子进程，on_timeout须终止其所属进程组并等待退出。未知硬杀
        导致的遗留active在下次持锁时按最后开始至恢复时刻保守计费，不能作零成本。
        """
        if threading.current_thread() is not threading.main_thread():
            raise RuntimeError("硬预算范围必须在主线程执行")
        if signal.getitimer(signal.ITIMER_REAL)[0] > 0:
            raise RuntimeError("已有进程实时时限，不覆盖或嵌套计时器")
        from contextlib import nullcontext

        with self.training_lock() if training else nullcontext(), self._combo_lock(combo):
            with self._file_lock("ledger.lock"):
                record = self._read()
                entry = self._entry(record, combo)
                self._recover_orphan(entry)
                available = self.limit_seconds - entry["spent_seconds"]
                if available <= 0:
                    self._write(record)
                    raise BudgetExceeded(f"{combo} 没有剩余预算")
                active = {
                    "id": uuid.uuid4().hex,
                    "phase": phase,
                    "pid": os.getpid(),
                    "started_at": self.wall_clock(),
                }
                entry["active"] = active
                self._write(record)
            started, status, failure = self.clock(), "complete", None
            previous_handler = signal.getsignal(signal.SIGALRM)

            def timeout(signum, frame):
                if on_timeout is not None:
                    on_timeout()
                raise BudgetExceeded(f"{combo}/{phase} 达到累计硬时限")

            signal.signal(signal.SIGALRM, timeout)
            try:
                signal.setitimer(signal.ITIMER_REAL, available)
                yield self
            except BaseException as exc:
                status, failure = "failed", type(exc).__name__
                raise
            finally:
                signal.setitimer(signal.ITIMER_REAL, 0)
                signal.signal(signal.SIGALRM, previous_handler)
                elapsed = max(0.0, self.clock() - started)
                with self._file_lock("ledger.lock"):
                    record = self._read()
                    entry = self._entry(record, combo)
                    entry["spent_seconds"] += elapsed
                    entry["active"] = None
                    exceeded = entry["spent_seconds"] >= self.limit_seconds
                    if exceeded and failure is None:
                        status, failure = "failed", "BudgetExceeded"
                    entry["events"].append(
                        {**active, "seconds": elapsed, "status": status, "exception": failure}
                    )
                    self._write(record)
                if exceeded and failure == "BudgetExceeded":
                    raise BudgetExceeded(f"{combo} 已达到累计硬时限")
