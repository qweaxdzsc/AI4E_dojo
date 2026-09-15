"""在锁定的外部仓库源码上提取并执行 CD 的 PI-BSNet 分支。

仅隔离其他模型和绘图；不修正原样条、硬边界、损失或更新算法。
使用与 Dojo 相同的物理数据以控制数据差异。不是原脚本全模型运行。
"""

import argparse
import ast
import hashlib
import json
import time
from pathlib import Path

import numpy as np
import torch
from torch import nn


def source_namespace(source):
    """从实际参考文件加载函数/模型和原始 PI 分支，保留源码位置。"""
    lock = (
        Path(__file__).resolve().parents[3]
        / "packages/ai4e-contrib/ability/model/pibsnet/source.json"
    )
    expected = json.loads(lock.read_text())["reference_files"]["src/convection_diffusion.py"]
    if hashlib.sha256(source.read_bytes()).hexdigest() != expected:
        raise ValueError("参考源码摘要与锁定来源不一致")
    tree = ast.parse(source.read_text())
    names = {
        "BsFun",
        "BsFun_derivative",
        "BsFun_second_derivative",
        "BsKnots",
        "BsKnots_derivatives",
        "compute_bspline_derivatives",
        "ControlPointNet",
        "PIBSNet",
    }
    definitions = [
        n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in names
    ]
    if {n.name for n in definitions} != names:
        raise ValueError("参考源码结构已变化")
    branch = next(
        n
        for n in ast.walk(tree)
        if isinstance(n, ast.If) and ast.unparse(n.test) == "name == 'PIBSNet'"
    )
    namespace = {"np": np, "torch": torch, "nn": nn}
    exec(compile(ast.Module(body=definitions, type_ignores=[]), str(source), "exec"), namespace)  # noqa: S102 - 明确执行摘要锁定的参考源码
    body = ast.parse("total_loss = 0.0\npde_loss = 0.0\ndata_loss = 0.0\n").body + branch.body
    return namespace, compile(ast.Module(body=body, type_ignores=[]), str(source), "exec")


def run(source, manifest, output, *, epochs=5000, seed=42):
    """同数据、正式网络与更新预算；输出独立来源和完整测试预测。"""
    if output.exists():
        raise FileExistsError(output)
    output.mkdir(parents=True)
    torch.set_num_threads(1)
    torch.manual_seed(seed)
    meta = json.loads(manifest.read_text())
    if meta["case"] != "convection_diffusion":
        raise ValueError("仅支持 CD 原分支")
    ns, code = source_namespace(source)

    def bases(n):
        tk, knots, b = ns["BsKnots"](25, 3, n)
        d1, d2 = ns["BsKnots_derivatives"](25, 3, n, knots, tk)
        return [torch.tensor(v, dtype=torch.float32) for v in (b, d1, d2)]

    records = [
        (r, torch.load(manifest.parent / r["path"], weights_only=True)) for r in meta["samples"]
    ]
    bt, bt1, bt2 = bases(records[0][1]["u"].shape[0])
    data = []
    for record, sample in records:
        bx, bx1, bx2 = bases(sample["u"].shape[1])
        data.append(
            (
                record,
                {
                    "lam": torch.tensor([[sample["parameters"]["lam"]]], dtype=torch.float32),
                    "a": torch.tensor([[sample["parameters"]["a"]]], dtype=torch.float32),
                    "Bx": bx,
                    "Bx_d1": bx1,
                    "Bx_d2": bx2,
                    "F_mat": sample["u"].float(),
                },
            )
        )
    model = ns["PIBSNet"](25, 25, 3, 64)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    ns.update(
        model=model,
        n_cp_t=25,
        n_cp_x=25,
        device=torch.device("cpu"),
        Bt=bt,
        Bt_d1=bt1,
        Bt_d2=bt2,
        PDE_WEIGHT=1.0,
        DATA_WEIGHT=3.0,
        bsnet_data=[d for r, d in data if r["split"] == "train"],
    )
    start, history = time.monotonic(), []
    for epoch in range(1, epochs + 1):
        optimizer.zero_grad()
        exec(code, ns)  # noqa: S102 - 明确执行摘要锁定的参考源码
        ns["total_loss"].backward()
        optimizer.step()
        history.append(float(ns["total_loss"].detach()))
        if epoch % 500 == 0:
            print(json.dumps({"epoch": epoch, "loss": history[-1]}), flush=True)
    metrics = []
    with torch.no_grad():
        for record, d in data:
            if record["split"] != "test":
                continue
            control = torch.ones(25, 25)
            control[0, :] = 0
            control[:, -1] = 1
            control[1:, :-1] = model(d["lam"], d["a"])[0]
            prediction = bt @ control @ d["Bx"].T
            truth = d["F_mat"]
            torch.save(
                {"prediction": prediction, "target": truth, "sample_id": record["id"]},
                output / f"{record['id']}.pt",
            )
            metrics.append(
                {
                    "id": record["id"],
                    "relative_l2": float((prediction - truth).norm() / truth.norm()),
                }
            )
    report = {
        "status": "complete",
        "execution": "isolated_original_ast_branch_same_physical_dataset",
        "source": str(source),
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "dataset_id": meta["content_id"],
        "epochs": epochs,
        "updates": epochs,
        "seed": seed,
        "device": "cpu",
        "precision": "fp32",
        "pde_points": "complete_dataset_grid",
        "loss_weights": {"pde": 1, "data": 3, "initial": 0, "periodic": 0},
        "samples": metrics,
        "seconds": time.monotonic() - start,
        "history": history,
    }
    torch.save(model.state_dict(), output / "model.pt")
    (output / "reference.json").write_text(json.dumps(report, indent=2))
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--epochs", default=5000, type=int)
    args = parser.parse_args()
    run(args.source, args.manifest, args.output, epochs=args.epochs)
