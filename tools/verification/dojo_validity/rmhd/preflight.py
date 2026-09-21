"""主控私有真实 baseline 预实验；本模块与派生产物绝不交付实验组。"""

import json
import time
from pathlib import Path

import h5py
import numpy as np
import torch

from ..io import digest, read_json, write_json
from .metrics import aggregate, field_errors
from .model import UNet
from .protocol import FIELDS, SCIENTIFIC, STARTS, gate


def read_fields(path):
    """读取原始六场 [time,field,R,Z]，保持 FP64 和原轴方向。"""
    with h5py.File(path, "r") as stream:
        value = np.stack([stream[field][:] for field in FIELDS], axis=1)
    if value.shape != (211, 6, 100, 100) or not np.isfinite(value).all():
        raise ValueError(f"原始轨迹不合法: {path}")
    return value


def prepare_train(samples, output):
    """只用训练轨迹，以合并中心矩计算总体统计并生成私有 FP32 缓存。"""
    output = Path(output)
    total, mean, m2 = 0, np.zeros(6), np.zeros(6)
    for sample in samples:
        value = read_fields(sample["path"])
        count = value.shape[0] * 100 * 100
        part = value.mean(axis=(0, 2, 3))
        delta = part - mean
        part_m2 = np.sum((value - part[None, :, None, None]) ** 2, axis=(0, 2, 3))
        m2 += part_m2 + delta * delta * total * count / (total + count)
        mean += delta * count / (total + count)
        total += count
    std = np.maximum(np.sqrt(m2 / total), 1e-12)
    write_json(
        output / "statistics.json",
        {
            "fields": FIELDS,
            "count_per_field": total,
            "mean": mean.tolist(),
            "std": std.tolist(),
            "ddof": 0,
        },
    )
    cache = np.lib.format.open_memmap(
        output / "train.npy", mode="w+", dtype="float32", shape=(len(samples), 211, 6, 100, 100)
    )
    for i, sample in enumerate(samples):
        cache[i] = (read_fields(sample["path"]) - mean[None, :, None, None]) / std[
            None, :, None, None
        ]
    cache.flush()
    return cache, mean, std


def rollout(model, state):
    """八次预测回填；不接收真值。"""
    outputs = []
    for _ in range(8):
        prediction = model(state)
        outputs.append(prediction)
        state = torch.cat([state[:, 30:], prediction], dim=1)
    return torch.cat(outputs, dim=1).reshape(-1, 40, 6, 100, 100)


def predictor(model, mean, std):
    """返回包含正反归一化和主机搬运的常驻推理函数。"""
    mean = mean.astype(np.float32)[None, None, :, None, None]
    std = std.astype(np.float32)[None, None, :, None, None]

    @torch.inference_mode()
    def predict(history):
        state = torch.from_numpy(((history - mean) / std).reshape(-1, 60, 100, 100)).to("mps")
        result = rollout(model, state).cpu().numpy() * std + mean
        torch.mps.synchronize()
        return result

    return predict


def validate(predict, samples, output=None):
    """仅开发验证；同时计算保持最后帧的诊断基线。"""
    rows, persistence_rows, histories = [], [], []
    if output is not None:
        Path(output).mkdir(parents=True, exist_ok=True)
    for sample in samples:
        value = read_fields(sample["path"])
        for start in STARTS:
            history = value[start : start + 10].astype(np.float32)[None]
            truth = value[start + 10 : start + 50]
            prediction = predict(history)[0]
            info = {"id": sample["id"], "start": start}
            rows.append(info | field_errors(prediction, truth, history[0, -1]))
            persistence_rows.append(
                info
                | field_errors(
                    np.repeat(value[start + 9 : start + 10], 40, axis=0), truth, value[start + 9]
                )
            )
            histories.append(history)
            if output is not None:
                np.save(
                    Path(output) / f"{sample['id']}-{start}.npy", prediction, allow_pickle=False
                )
    ids = [s["id"] for s in samples]
    return aggregate(rows, ids), aggregate(persistence_rows, ids), histories


def latency(predict, histories):
    """20次预热，三批45窗口各重复五次，取批次P95中位数。"""
    for i in range(20):
        predict(histories[i % len(histories)])
    batches = []
    for _ in range(3):
        values = []
        for _ in range(5):
            for history in histories:
                torch.mps.synchronize()
                started = time.perf_counter()
                prediction = predict(history)
                torch.mps.synchronize()
                values.append(time.perf_counter() - started)
                if prediction.shape != (1, 40, 6, 100, 100) or not np.isfinite(prediction).all():
                    raise ValueError("延迟测试预测无效")
        batches.append({"samples_seconds": values, "p95_seconds": float(np.quantile(values, 0.95))})
    return {
        "p95_seconds": float(np.median([b["p95_seconds"] for b in batches])),
        "batches": batches,
    }


def run_preflight(comparison):
    """完整500epoch训练，失败或超时不缩预算、不启动正式组。"""
    comparison = Path(comparison).resolve()
    root = comparison / "preflight"
    root.mkdir(exist_ok=False)
    cfg = read_json(comparison / "scientific.json")
    if cfg != json.loads(json.dumps(SCIENTIFIC)):
        raise ValueError("科学配置改变；必须新建协议并重新冻结")
    if not torch.backends.mps.is_available():
        raise RuntimeError("MPS 不可用，禁止 CPU 回退")
    split = read_json(comparison / "private-split.json")["splits"]
    torch.set_num_threads(6)
    torch.manual_seed(42)
    model = UNet()
    torch.save(model.state_dict(), root / "initial-checkpoint.pt")
    write_json(
        root / "provenance.json",
        {
            "torch": torch.__version__,
            "numpy": np.__version__,
            "device": "mps",
            "model_sha256": digest(Path(__file__).with_name("model.py")),
            "preflight_sha256": digest(__file__),
            "split_sha256": digest(comparison / "private-split.json"),
            "initial_checkpoint_sha256": digest(root / "initial-checkpoint.pt"),
            "parameter_count": sum(p.numel() for p in model.parameters()),
        },
    )
    start = time.monotonic()
    cache, mean, std = prepare_train(split["train"], root)
    preparation_seconds = time.monotonic() - start
    print(json.dumps({"phase": "prepared", "seconds": preparation_seconds}), flush=True)
    model.to("mps")
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    generator = np.random.Generator(np.random.PCG64(42))
    validation_seconds = 0.0
    train_started = time.monotonic()
    curve = []
    with (root / "events.jsonl").open("w") as events:
        for epoch in range(1, 501):
            model.train()
            starts = generator.integers(0, 162, size=70)
            order = generator.permutation(70)
            losses = []
            for offset in range(0, 70, 16):
                ids = order[offset : offset + 16]
                batch = np.stack([cache[i, starts[i] : starts[i] + 50] for i in ids])
                x = torch.from_numpy(batch[:, :10].copy()).reshape(-1, 60, 100, 100).to("mps")
                y = torch.from_numpy(batch[:, 10:].copy()).to("mps")
                optimizer.zero_grad(set_to_none=True)
                loss = (rollout(model, x) - y).square().mean()
                if not torch.isfinite(loss):
                    raise ValueError(f"训练非有限: epoch {epoch}")
                loss.backward()
                optimizer.step()
                losses.append(float(loss.detach().cpu()))
            event = {
                "epoch": epoch,
                "loss": float(np.mean(losses)),
                "elapsed": time.monotonic() - train_started,
            }
            if epoch % 10 == 0:
                validation_start = time.monotonic()
                model.eval()
                score, persistence, histories = validate(
                    predictor(model, mean, std), split["validation"]
                )
                event["validation"] = {k: v for k, v in score.items() if k != "rows"}
                validation_seconds += time.monotonic() - validation_start
                print(json.dumps(event), flush=True)
            curve.append(event)
            events.write(json.dumps(event) + "\n")
            events.flush()
            if epoch % 100 == 0:
                torch.save(
                    {
                        "model": model.state_dict(),
                        "optimizer": optimizer.state_dict(),
                        "epoch": epoch,
                        "rng": generator.bit_generator.state,
                    },
                    root / f"epoch-{epoch}.pt",
                )
    torch.mps.synchronize()
    training_wall = time.monotonic() - train_started
    model.eval()
    score, persistence, histories = validate(
        predictor(model, mean, std), split["validation"], root / "validation-predictions"
    )
    times = latency(predictor(model, mean, std), histories)
    write_json(root / "latency.json", times)
    result = {
        "scope": "private_preflight_train_validation_only",
        "epochs": 500,
        "device": "mps",
        "training_seconds": training_wall,
        "training_compute_and_loading_seconds": training_wall - validation_seconds,
        "scheduled_validation_seconds": validation_seconds,
        "data_preparation_seconds": preparation_seconds,
        "latency_p95_seconds": times["p95_seconds"],
        "validation": score,
        "persistence": persistence,
        "training_updates": 2500,
        "peak_mps_allocated_bytes_at_finish": torch.mps.driver_allocated_memory(),
    }
    result["gate"] = gate(result)
    write_json(root / "result.json", result)
    write_json(root / "curve.json", curve)
    write_json(
        comparison / "state.json",
        {
            "phase": "science_passed" if result["gate"]["passed"] else "science_gate_failed",
            "formal_sessions_started": False,
            "gate": result["gate"],
        },
    )
    print(
        json.dumps({k: v for k, v in result.items() if k not in ("validation", "persistence")}),
        flush=True,
    )
    return result
