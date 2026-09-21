"""可复制的普通 Python Neumann baseline；不依赖任何训练框架。"""

import argparse
import hashlib
import json
import resource
import time
from pathlib import Path

import numpy as np
import torch


def _json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def _numerics(root):
    import types

    path = root / "source/numerics.py"
    module = types.ModuleType("neumann_reference")
    exec(compile(path.read_text(), str(path), "exec"), module.__dict__)  # noqa: S102 - 摘要锁定的原模型定义
    return module


def model_and_data(root, checkpoint=None):
    """加载本目录材料；返回原始模型、样条矩阵和数据，不导入外部项目。"""
    module = _numerics(root)
    model = module.BSNetLoss(40, 40, 128)
    payload = torch.load(
        checkpoint or root / "initial-checkpoint.pt", weights_only=True, map_location="cpu"
    )
    model.load_state_dict(payload["model"])
    with np.load(root / "dataset.npz", allow_pickle=False) as loaded:
        data = {k: torch.from_numpy(loaded[k].copy()) for k in loaded.files}
    bases = [data[k] for k in ("basis", "basis_d1", "basis_d2")]
    return model, data, bases


def objective(model, parameter, target, bases):
    """保持原参数坐标导数、全网格 MSE 和 1/5/2/2 加权顺序。"""
    b, d1, d2 = bases
    control = model.forward_U(parameter.reshape(1, 1))[0]
    prediction = b @ control @ b.T
    ut = d1 @ control @ b.T
    ux = b @ control @ d1.T
    uxx = b @ control @ d2.T
    losses = {
        "pde": ((ut - parameter.item() * uxx) ** 2).mean(),
        "data": ((prediction - target) ** 2).mean(),
        "initial": ((prediction[0] - target[0]) ** 2).mean(),
        "boundary": (ux[:, 0] ** 2).mean() + (ux[:, -1] ** 2).mean(),
    }
    total = losses["pde"] + 5.0 * losses["data"] + 2.0 * losses["initial"]
    total = total + 2.0 * losses["boundary"]
    return total, losses


def train(root, output, epochs=5000):
    """原整轮顺序累加后一次反传；预算可调整，失败不删除运行目录。"""
    if epochs < 1:
        raise ValueError("epochs 必须为正")
    output.mkdir(parents=True, exist_ok=False)
    torch.set_num_threads(1)
    torch.manual_seed(42)
    model, data, bases = model_and_data(root)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    history = []
    start = time.monotonic()
    for epoch in range(1, epochs + 1):
        optimizer.zero_grad()
        total, terms = 0.0, {}
        for parameter, target in zip(data["train_nu"], data["train_u"], strict=True):
            loss, parts = objective(model, parameter, target, bases)
            total = total + loss
            for key, value in parts.items():
                terms[key] = terms.get(key, 0.0) + float(value.detach())
        total.backward()
        optimizer.step()
        row = {"update": epoch, "total": float(total.detach()), **terms}
        history.append(row)
        if epoch == 1 or epoch % 500 == 0 or epoch == epochs:
            print(json.dumps(row), flush=True)
    checkpoint = output / "checkpoint.pt"
    torch.save(
        {"model": model.state_dict(), "optimizer": optimizer.state_dict(), "updates": epochs},
        checkpoint,
    )
    # loss 指标对应各更新前观测，明确保留而不冒称最后权重的重新评价。
    metrics = {
        "initial_total_loss": history[0]["total"],
        "final_total_loss": history[-1]["total"],
        "best_total_loss": min(r["total"] for r in history),
        "loss_reduction_ratio": (history[0]["total"] - history[-1]["total"]) / history[0]["total"]
        if history[0]["total"]
        else None,
        **{f"final_{k}_loss": history[-1][k] for k in ("pde", "data", "initial", "boundary")},
        "loss_observation": "before_optimizer_update",
        "training_updates": epochs,
        "trainable_parameter_count": sum(p.numel() for p in model.parameters() if p.requires_grad),
        "total_parameter_count": sum(p.numel() for p in model.parameters()),
        "model_depth": sum(isinstance(m, torch.nn.Linear) for m in model.modules()),
        "checkpoint_size_bytes": checkpoint.stat().st_size,
        "resolved_device": "cpu",
        "thread_count": 1,
        "training_seconds": time.monotonic() - start,
        "peak_memory_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        * (1 if __import__("sys").platform == "darwin" else 1024),
    }
    _json(output / "training.json", metrics)
    _json(output / "history.json", history)
    return checkpoint


def predict(root, checkpoint, output):
    """从明确权重生成十个完整场 NPY，不在预测清单中夹带真值。"""
    output.mkdir(parents=True, exist_ok=False)
    torch.set_num_threads(1)
    model, data, bases = model_and_data(root, checkpoint)
    model.eval()
    records = []
    with torch.no_grad():
        for index, parameter in enumerate(data["test_nu"]):
            control = model.forward_U(parameter.reshape(1, 1))[0]
            field = bases[0] @ control @ bases[0].T
            sample_id = f"test-{index:05d}"
            path = output / f"{sample_id}.npy"
            np.save(path, field.numpy(), allow_pickle=False)
            records.append(
                {
                    "id": sample_id,
                    "path": path.name,
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                }
            )
    _json(output / "predictions.json", {"samples": records})
    return output / "predictions.json"


def main():
    """普通脚本入口：train 与 predict 分开执行以准确计时。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["train", "predict"])
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--epochs", type=int, default=5000)
    parser.add_argument("--checkpoint", type=Path)
    args = parser.parse_args()
    if args.action == "train":
        train(args.baseline, args.output, args.epochs)
    else:
        if args.checkpoint is None:
            parser.error("predict 必须指定 --checkpoint")
        predict(args.baseline, args.checkpoint, args.output)


if __name__ == "__main__":
    main()
