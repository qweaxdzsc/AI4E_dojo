"""独立执行锁定 Advection notebook 的原训练循环，使用共享物理数据。"""

import argparse
import ast
import hashlib
import json
import time
from pathlib import Path

import numpy as np
import torch
from torch import nn


def load_reference(source):
    """只选择模型、样条及训练所用定义，不执行数据生成或绘图单元。"""
    lock = (
        Path(__file__).resolve().parents[3]
        / "packages/ai4e-contrib/ability/model/pibsnet/source.json"
    )
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    if digest != json.loads(lock.read_text())["reference_files"]["src/advection.ipynb"]:
        raise ValueError("参考源码摘要不匹配")
    code = "\n".join(
        "".join(c["source"])
        for c in json.loads(source.read_text())["cells"]
        if c["cell_type"] == "code"
    )
    tree = ast.parse(code)
    names = {
        "BsFun",
        "BsFun_derivative",
        "BsFun_second_derivative",
        "BsKnots",
        "BsKnots_derivatives",
        "BetaPhaseControlPointNet",
        "compute_bspline_derivatives",
        "assign_first_row_direct",
    }
    definitions = {}
    loop = None
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name in names:
            definitions[node.name] = node
        if isinstance(node, ast.For) and ast.unparse(node.target) == "epoch":
            loop = next(
                n
                for n in node.body
                if isinstance(n, ast.For) and ast.unparse(n.iter) == "training_data"
            )
            break
    if set(definitions) != names or loop is None:
        raise ValueError("参考训练结构变化")
    ns = {"torch": torch, "np": np, "nn": nn}
    exec(  # noqa: S102 - 仅执行摘要锁定的参考定义
        compile(ast.Module(body=list(definitions.values()), type_ignores=[]), str(source), "exec"),
        ns,
    )
    epoch_code = compile(
        ast.Module(body=ast.parse("total_loss=0.0").body + [loop], type_ignores=[]),
        str(source),
        "exec",
    )
    return ns, epoch_code, digest


def run(source, manifest, output, *, epochs=2000):
    """原网络、损失与逐实例 Adam 更新；不把共享数据隔离对照称为原生成器复现。"""
    ns, epoch_code, digest = load_reference(source)
    meta = json.loads(manifest.read_text())
    if meta["case"] != "advection":
        raise ValueError("仅支持 Advection")
    if output.exists():
        raise FileExistsError(output)
    output.mkdir(parents=True)
    torch.set_num_threads(1)
    torch.manual_seed(42)
    records = [
        (r, torch.load(manifest.parent / r["path"], weights_only=True)) for r in meta["samples"]
    ]

    def bases(n):
        tk, knots, b = ns["BsKnots"](150, 5, n)
        d1, _ = ns["BsKnots_derivatives"](150, 5, n, knots, tk)
        return torch.tensor(b, dtype=torch.float32), torch.tensor(d1, dtype=torch.float32)

    bt, dt = bases(records[0][1]["u"].shape[0])
    bx, dx = bases(records[0][1]["u"].shape[1])
    data = [
        (
            r,
            {
                "beta": torch.tensor([[s["parameters"]["beta"]]], dtype=torch.float32),
                "phases": torch.tensor([s["parameters"]["phase"]], dtype=torch.float32),
                "U": s["u"].float(),
            },
        )
        for r, s in records
    ]
    model = ns["BetaPhaseControlPointNet"](150, 150, 64)
    ns.update(
        model=model,
        optimizer=torch.optim.Adam(model.parameters(), lr=0.001),
        mse_loss=nn.MSELoss(),
        Bit_t=bt,
        Bit_x=bx,
        Bit_t_derivative=dt,
        Bit_x_derivative=dx,
        training_data=[d for r, d in data if r["split"] == "train"],
    )
    start, history = time.monotonic(), []
    for epoch in range(1, epochs + 1):
        exec(epoch_code, ns)  # noqa: S102 - 原参考逐实例训练语句
        history.append(ns["total_loss"] / len(ns["training_data"]))
        if epoch % 500 == 0:
            print(json.dumps({"epoch": epoch, "loss": history[-1]}), flush=True)
    metrics = []
    with torch.no_grad():
        for record, sample in data:
            if record["split"] != "test":
                continue
            cp = model(sample["beta"], sample["phases"].view(1, -1))
            ns["assign_first_row_direct"](cp, sample["U"][0].numpy())
            prediction = bt @ cp[0] @ bx.T
            truth = sample["U"]
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
        "execution": "isolated_original_ast_branch_same_physical_dataset",
        "source_sha256": digest,
        "dataset_id": meta["content_id"],
        "epochs": epochs,
        "updates": epochs * len(ns["training_data"]),
        "seed": 42,
        "device": "cpu",
        "precision": "fp32",
        "seconds": time.monotonic() - start,
        "samples": metrics,
        "history": history,
        "pde_points": "complete_dataset_grid",
        "loss_weights": {"pde": 1, "data": 10, "initial": 0, "periodic": 0},
    }
    torch.save(model.state_dict(), output / "model.pt")
    (output / "reference.json").write_text(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("source", "manifest", "output"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    args = parser.parse_args()
    run(args.source, args.manifest, args.output)
