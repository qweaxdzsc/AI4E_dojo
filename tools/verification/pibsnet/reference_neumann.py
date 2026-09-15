"""从锁定 Neumann 源文件执行原 PI-BSNet 分支，保留原导数和更新。"""

import argparse
import ast
import hashlib
import json
import time
from pathlib import Path

import numpy as np
import torch
from torch import nn


def run(source, manifest, output, *, epochs=5000, physical_derivatives=False):
    """以相同物理数据运行独立参考，不修改原仓库。"""
    lock = (
        Path(__file__).resolve().parents[3]
        / "packages/ai4e-contrib/ability/model/pibsnet/source.json"
    )
    expected = json.loads(lock.read_text())["reference_files"]["src/neumann_bc.py"]
    if hashlib.sha256(source.read_bytes()).hexdigest() != expected:
        raise ValueError("参考源码摘要与锁定来源不一致")
    tree = ast.parse(source.read_text())
    names = {
        "BsFun",
        "BsFun_derivative",
        "BsFun_second_derivative",
        "BsKnots",
        "BsKnots_derivatives",
        "bspline_eval",
        "bspline_derivs",
        "ControlPointNet",
        "BSNetLoss",
    }
    definitions = [
        n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in names
    ]
    if {n.name for n in definitions} != names:
        raise ValueError("参考源码定义发生变化")
    loop = next(
        n
        for n in ast.walk(tree)
        if isinstance(n, ast.For)
        and ast.unparse(n.target) == "sample"
        and ast.unparse(n.iter) == "train_data"
    )
    # 仅选择原 PI-BSNet else，数值语句与更新分组均不重写。
    loop.body = [
        child
        for node in loop.body
        for child in (node.orelse if isinstance(node, ast.If) else [node])
    ]
    ns = {"np": np, "torch": torch, "nn": nn, "device": torch.device("cpu")}
    exec(compile(ast.Module(body=definitions, type_ignores=[]), str(source), "exec"), ns)  # noqa: S102 - 明确执行摘要锁定的参考源码
    code = compile(
        ast.Module(
            body=ast.parse(
                "total_L=0.0\nLpde_acc=0.0\nLdata_acc=0.0\nLic_acc=0.0\nLbc_acc=0.0\n"
            ).body
            + [loop],
            type_ignores=[],
        ),
        str(source),
        "exec",
    )
    if output.exists():
        raise FileExistsError(output)
    output.mkdir(parents=True)
    torch.set_num_threads(1)
    torch.manual_seed(42)
    meta = json.loads(manifest.read_text())
    records = [
        (r, torch.load(manifest.parent / r["path"], weights_only=True)) for r in meta["samples"]
    ]

    def bases(n):
        tk, knots, b = ns["BsKnots"](40, 5, n)
        d1, d2 = ns["BsKnots_derivatives"](40, 5, n, knots, tk)
        if physical_derivatives:
            from scipy.interpolate import BSpline

            physical_knots = np.r_[np.zeros(5), np.linspace(0, 1, 36), np.ones(5)]
            spline = BSpline(physical_knots, np.eye(40), 5)
            coordinates = np.linspace(0, 1, n)
            b, d1, d2 = [spline(coordinates, nu=order) for order in range(3)]
        return [torch.tensor(v, dtype=torch.float32) for v in (b, d1, d2)]

    bt, bt1, bt2 = bases(128)
    bx, bx1, bx2 = bases(128)
    data = [
        (
            r,
            {
                "nu": torch.tensor([[s["parameters"]["nu"]]], dtype=torch.float32),
                "S_true": s["u"].float(),
            },
        )
        for r, s in records
    ]
    model = ns["BSNetLoss"](40, 40, 128)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    ns.update(
        model=model,
        train_data=[d for r, d in data if r["split"] == "train"],
        Bt=bt,
        Bx=bx,
        Bt_d1=bt1,
        Bt_d2=bt2,
        Bx_d1=bx1,
        Bx_d2=bx2,
        idx_x0=0,
        idx_x1=127,
        ic_true=torch.cos(torch.pi * records[0][1]["axes"]["x"].float()),
        PDE_WEIGHT=1.0,
        DATA_WEIGHT=5.0,
        IC_WEIGHT=2.0,
        BC_WEIGHT=2.0,
    )
    start, history = time.monotonic(), []
    for epoch in range(1, epochs + 1):
        optimizer.zero_grad()
        exec(code, ns)  # noqa: S102 - 明确执行摘要锁定的参考源码
        ns["total_L"].backward()
        optimizer.step()
        history.append(float(ns["total_L"].detach()))
        if epoch % 500 == 0:
            print(json.dumps({"epoch": epoch, "loss": history[-1]}), flush=True)
    metrics = []
    with torch.no_grad():
        for record, d in data:
            if record["split"] != "test":
                continue
            prediction = ns["bspline_eval"](model.forward_U(d["nu"])[0], bt, bx)
            truth = d["S_true"]
            torch.save(
                {"sample_id": record["id"], "target": truth, "prediction": prediction},
                output / f"{record['id']}.pt",
            )
            metrics.append(
                {
                    "id": record["id"],
                    "relative_l2": float((prediction - truth).norm() / truth.norm()),
                }
            )
    result = {
        "status": "complete",
        "execution": "diagnostic_original_loop_independent_scipy_physical_basis"
        if physical_derivatives
        else "isolated_original_ast_branch_same_physical_dataset",
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "dataset_id": meta["content_id"],
        "epochs": epochs,
        "updates": epochs,
        "seed": 42,
        "device": "cpu",
        "precision": "fp32",
        "pde_points": "complete_dataset_grid",
        "loss_weights": {"pde": 1, "data": 5, "initial": 2, "periodic": 0, "boundary": 2},
        "seconds": time.monotonic() - start,
        "samples": metrics,
        "history": history,
    }
    torch.save(model.state_dict(), output / "model.pt")
    (output / "reference.json").write_text(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("source", "manifest", "output"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    parser.add_argument("--physical-derivatives", action="store_true")
    args = parser.parse_args()
    run(args.source, args.manifest, args.output, physical_derivatives=args.physical_derivatives)
