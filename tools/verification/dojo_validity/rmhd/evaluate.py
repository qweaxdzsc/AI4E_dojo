"""主控启动无真值 worker 并独立 FP64 评分；时钟与标签不进入候选进程。"""

import json
import selectors
import subprocess
import time
from pathlib import Path

import h5py
import numpy as np

from ..io import digest, read_json, write_json
from .isolation import clean_environment, policy
from .metrics import aggregate, field_errors
from .protocol import FIELDS, STARTS


class Resident:
    """候选只看到当前输入；父进程收齐输出后停止计时，含固定 IPC 拷贝开销。"""

    def __init__(self, candidate, environment, runtime, output):
        started = time.monotonic()
        self.output = Path(output)
        self.work = self.output / "worker"
        self.work.mkdir(parents=True, exist_ok=False)
        for name in ("home", "cache", "tmp", "agent-state"):
            (self.work / name).mkdir()
        self.inputs = np.lib.format.open_memmap(
            self.work / "input.npy", mode="w+", dtype="float32", shape=(1, 10, 6, 100, 100)
        )
        self.outputs = np.lib.format.open_memmap(
            self.work / "output.npy", mode="w+", dtype="float32", shape=(1, 40, 6, 100, 100)
        )
        self.inputs[:] = 0
        self.outputs[:] = np.nan
        script = Path(__file__).with_name("worker.py").resolve()
        self.body = policy(
            [self.work / "home", self.work / "cache", self.work / "tmp"],
            [candidate, environment, script, self.work / "input.npy", *runtime],
        )
        self.body += f"\n(allow file-read* file-write* (literal {json.dumps(str(self.work / 'output.npy'))}))"
        self.body += f"\n(allow file-read* (literal {json.dumps(str(self.work))}))"
        (self.output / "worker-policy.sbpl").write_text(self.body)
        self.stderr = (self.output / "worker-stderr.log").open("w")
        self.stdout_log = (self.output / "worker-stdout.log").open("w")
        self.process = subprocess.Popen(
            [
                "/usr/bin/sandbox-exec",
                "-p",
                self.body,
                str(Path(environment) / "bin/python"),
                str(script),
                "--candidate",
                str(candidate),
                "--exchange",
                str(self.work),
            ],
            cwd=self.work,
            env=clean_environment(self.work),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=self.stderr,
            text=True,
            bufsize=1,
        )
        self.selector = selectors.DefaultSelector()
        self.selector.register(self.process.stdout, selectors.EVENT_READ)
        self.counter = 0
        self.model_info = None
        try:
            self.wait_for("RMHD_READY", 120)
            info = self.work / "tmp/model-info.json"
            if info.exists():
                self.model_info = read_json(info)
            self.startup_seconds = time.monotonic() - started
        except BaseException:
            self.close()
            raise

    def wait_for(self, expected, timeout):
        """有界等待基础设施响应；保留任意候选 stdout，不用其自报时长。"""
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if not self.selector.select(max(0, deadline - time.monotonic())):
                break
            line = self.process.stdout.readline()
            if not line:
                raise RuntimeError(f"推理进程退出: {self.process.poll()}")
            self.stdout_log.write(line)
            self.stdout_log.flush()
            if line.strip() == expected:
                return
        raise TimeoutError("推理工作进程响应超时")

    def predict(self, history):
        """主机输入至主机输出墙钟；文件映射在计时前建立，不包含磁盘归档。"""
        self.counter += 1
        started = time.perf_counter()
        self.inputs[:] = history
        self.outputs[:] = np.nan
        self.process.stdin.write(json.dumps({"request": self.counter}) + "\n")
        self.process.stdin.flush()
        self.wait_for(f"RMHD_DONE {self.counter}", 60)
        result = np.array(self.outputs, copy=True)
        elapsed = time.perf_counter() - started
        if not np.isfinite(result).all():
            raise ValueError("主控收到非有限或不完整预测")
        return result, elapsed

    def close(self):
        """只结束本次工作进程，不触碰组会话或其他服务。"""
        if self.process.poll() is None:
            self.process.stdin.close()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.terminate()
                self.process.wait(timeout=5)
        self.selector.close()
        self.stderr.close()
        self.stdout_log.close()


def latency_orders(count, seed=None):
    """三批窗口顺序；每窗口五次，随机发生器固定且跨批连续。"""
    if count <= 0:
        raise ValueError("延迟窗口不能为空")
    generator = np.random.Generator(np.random.PCG64(seed)) if seed is not None else None
    for _ in range(3):
        order = np.tile(np.arange(count), 5)
        if generator is not None:
            generator.shuffle(order)
        yield order


def evaluate_candidate(candidate, environment, runtime, samples, output, *, latency_seed=None):
    """评分进程不 import 候选；单例逐一发历史、未来真值仅留本进程。"""
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    resident = None
    execution_started = time.monotonic()
    try:
        resident = Resident(candidate, environment, runtime, output)
        rows, persistence_rows, histories = [], [], []
        predictions = output / "predictions"
        predictions.mkdir(exist_ok=True)
        files = []
        archive_seconds = 0.0
        for sample in samples:
            with h5py.File(sample["path"], "r") as stream:
                for start in STARTS:
                    history = np.stack(
                        [stream[f][start : start + 10] for f in FIELDS], axis=1
                    ).astype(np.float32)[None]
                    truth = np.stack([stream[f][start + 10 : start + 50] for f in FIELDS], axis=1)
                    prediction, _ = resident.predict(history)
                    rows.append(
                        {"id": sample["id"], "start": start}
                        | field_errors(prediction[0], truth, history[0, -1])
                    )
                    persistence_rows.append(
                        {"id": sample["id"], "start": start}
                        | field_errors(np.broadcast_to(history[0, -1], truth.shape), truth)
                    )
                    target = predictions / f"{sample['id']}-{start}.npy"
                    archive_started = time.perf_counter()
                    np.save(target, prediction[0], allow_pickle=False)
                    files.append(
                        {
                            "id": sample["id"],
                            "start": start,
                            "file": target.name,
                            "sha256": digest(target),
                        }
                    )
                    archive_seconds += time.perf_counter() - archive_started
                    histories.append(history)
        scores = aggregate(rows, [s["id"] for s in samples])
        persistence = aggregate(persistence_rows, [s["id"] for s in samples])
        for i in range(20):
            resident.predict(histories[i % len(histories)])
        batches = []
        for order in latency_orders(len(histories), latency_seed):
            times = [resident.predict(histories[i])[1] for i in order]
            batches.append(
                {
                    "samples_seconds": times,
                    "p95_seconds": float(np.quantile(times, 0.95)),
                    "window_order": order.tolist(),
                }
            )
        p95 = float(np.median([b["p95_seconds"] for b in batches]))
        write_json(
            output / "latency.json",
            {
                "p95_seconds": p95,
                "batches": batches,
                "includes_controller_ipc_copy": True,
                "latency_seed": latency_seed,
            },
        )
        write_json(output / "predictions.json", {"files": files, "fields": FIELDS})
        return {
            "status": "evaluated",
            "eligible": p95 <= 0.050,
            "latency_p95_seconds": p95,
            "accuracy": scores,
            "loaded_models": getattr(resident, "model_info", None),
            "cold_worker_and_model_startup_seconds": getattr(resident, "startup_seconds", None),
            "prediction_archive_and_hash_seconds": archive_seconds,
            "persistence": persistence,
            "per_field_improvement_over_persistence": {
                field: 1 - scores["per_field_relative_l2"][field] / value if value > 0 else None
                for field, value in persistence["per_field_relative_l2"].items()
            },
            "latency_limit_seconds": 0.050,
        }
    except (ValueError, RuntimeError, TimeoutError, OSError) as error:
        return {
            "status": "invalid",
            "eligible": False,
            "accuracy": None,
            "error": f"{type(error).__name__}: {error}",
        }
    finally:
        if resident is not None:
            resident.close()
        write_json(
            output / "execution.json",
            {
                "start": execution_started,
                "end": time.monotonic(),
                "source": "controller clock including inference and FP64 scoring",
            },
        )


def evaluator_for(comparison):
    """只有主控持有测试名单；调用者仍必须经双方最终冻结的状态门禁。"""
    root = Path(comparison)
    if read_json(root / "state.json")["phase"] not in {"both_finals_locked", "hidden_evaluating"}:
        raise ValueError("双方最终冻结前禁止构造隐藏评价器")
    for group in ("plain", "dojo"):
        read_json(root / "final-selections" / f"{group}.json")
    samples = read_json(root / "private-split.json")["splits"]["test"]
    config = read_json(root / "comparison-protocol.json")
    started = time.monotonic()
    for sample in samples:
        if digest(sample["path"]) != sample["sha256"]:
            raise ValueError("主控隐藏来源摘要变化，须恢复冻结来源后原样重试")
    write_json(
        root / "evidence/hidden-input-integrity.json",
        {
            "samples": [{"id": s["id"], "sha256": s["sha256"]} for s in samples],
            "verified": True,
            "seconds": time.monotonic() - started,
            "scope": "controller verification after both final selections; no feedback to groups",
        },
    )

    def evaluate(group, number, candidate, output):
        return evaluate_candidate(
            candidate,
            root / "frozen-environments" / group,
            config["runtime_readonly_roots"],
            samples,
            output,
        )

    return evaluate
