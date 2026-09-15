"""同环境执行锁定原函数，区分 Dojo 迁移差异与跨依赖环境差异。"""

import argparse
import ast
import time
from pathlib import Path

import numpy as np
import torch
from torch import nn

from ai4e_contrib.application.datasets.parametric import Dataset
from ai4e_core.abilities.data.save.bundle import file_digest, save_json


def run(root, source):
    """相同完整预算、数据与初始化执行原函数；不修改任何Dojo算法设置。"""
    output = root / "same_environment_reference"
    output.mkdir(exist_ok=False)
    text = source.read_text()
    wanted = {
        "BsFun",
        "build_bspline_basis",
        "build_bspline_derivatives",
        "BSplineNet_a",
        "compute_loss_pde_data_icbc",
    }
    nodes = [
        n
        for n in ast.parse(text).body
        if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in wanted
    ]
    if len(nodes) != len(wanted):
        raise ValueError("原函数定义不完整")
    namespace = {"np": np, "torch": torch, "nn": nn}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(source), "exec"), namespace)  # noqa: S102 - 仅选定原数值函数
    dataset = Dataset(root / "datasets/manifest.json")
    train = [dataset.read(r) for r in dataset.records("train")]
    data = [
        (torch.tensor([[s["parameters"]["a"]]], dtype=torch.float32), s["u"].float()) for s in train
    ]
    bases = []
    for cp, n in [(100, 1001), (20, 21), (20, 21)]:
        b, k, t = namespace["build_bspline_basis"](cp, 3, n)
        d, dd = namespace["build_bspline_derivatives"](cp, 3, n, k, t)
        bases.append((b, d, dd))
    bt, bx, by = bases
    torch.manual_seed(42)
    net = namespace["BSplineNet_a"](100, 20, 20, 64)
    optimizer = torch.optim.Adam(net.parameters(), lr=0.001)
    fn = namespace["compute_loss_pde_data_icbc"]
    started = time.monotonic()
    history = []
    for epoch in range(3000):
        losses = []
        for a, target in data:
            loss, *_ = fn(
                net,
                a,
                target,
                bt[0],
                bx[0],
                by[0],
                bt[1],
                bx[2],
                by[2],
                lambda_data=1.0,
                lambda_phys=0.001,
            )
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            losses.append(float(loss.detach()))
        history.append(sum(losses) / len(losses))
        if (epoch + 1) % 500 == 0:
            print(epoch + 1, history[-1], flush=True)
    dojo_path = list((root / "runs").glob("*/checkpoints/last.pt"))
    if len(dojo_path) != 1:
        raise ValueError("Dojo最终检查点不唯一")
    dojo = torch.load(dojo_path[0], weights_only=False)
    weights = {k: float((v - dojo["model"][k]).abs().max()) for k, v in net.state_dict().items()}
    predictions = []
    metrics = []
    with torch.no_grad():
        for i, record in enumerate(dataset.records("test")):
            sample = dataset.read(record)
            a = torch.tensor([[sample["parameters"]["a"]]], dtype=torch.float32)
            _, _, _, pred, _ = fn(
                net,
                a,
                sample["u"].float(),
                bt[0],
                bx[0],
                by[0],
                bt[1],
                bx[2],
                by[2],
                lambda_data=1.0,
                lambda_phys=0.001,
            )
            pred = pred[0]
            truth = sample["u"].float()
            actual = torch.load(root / "predictions" / f"{record['id']}.pt", weights_only=False)[
                "prediction"
            ]
            predictions.append(float((pred - actual).abs().max()))
            d = (pred - truth).double().flatten(1)
            r = truth.double().flatten(1)
            metrics.append(float((d.norm(dim=1) / (r.norm(dim=1) + 1e-12)).mean()))
            np.savez_compressed(
                output / f"{record['id']}.npz", prediction=pred.numpy(), target=truth.numpy()
            )
    result = {
        "epochs": 3000,
        "updates": 30000,
        "seconds": time.monotonic() - started,
        "numpy": np.__version__,
        "torch": torch.__version__,
        "source": str(source),
        "source_sha256": file_digest(source),
        "mean_time_relative_l2": float(np.mean(metrics)),
        "parameter_max_differences_from_dojo": weights,
        "prediction_max_differences_from_dojo": predictions,
        "history_max_difference_from_dojo": max(
            abs(x - r["loss"]) for x, r in zip(history, dojo["history"], strict=True)
        ),
    }
    torch.save({"model": net.state_dict(), "history": history}, output / "last.pt")
    save_json(output / "result.json", result)
    print(result, flush=True)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, required=True)
    p.add_argument("--source", type=Path, required=True)
    a = p.parse_args()
    torch.set_num_threads(1)
    run(a.root, a.source)
