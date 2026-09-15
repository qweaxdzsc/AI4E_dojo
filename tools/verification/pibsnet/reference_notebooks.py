"""Burgers/梯形的锁定 notebook 独立参考；文献参数覆盖明确记录。"""

import argparse
import ast
import hashlib
import json
import time
from pathlib import Path

import numpy as np
import torch
from torch import nn


def run(case, source, manifest, output, *, epochs=None):
    """共享物理数据隔离模型差异，保留原导数、原条件施加及原方程符号。"""
    if case not in {"burgers", "diffusion_trapezoid"}:
        raise ValueError(case)
    lock = (
        Path(__file__).resolve().parents[3]
        / "packages/ai4e-contrib/ability/model/pibsnet/source.json"
    )
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    if digest != json.loads(lock.read_text())["reference_files"][f"src/{case}.ipynb"]:
        raise ValueError("参考来源摘要不匹配")
    text = "\n".join(
        "".join(c["source"])
        for c in json.loads(source.read_text())["cells"]
        if c["cell_type"] == "code"
    )
    text = text.replace(
        "!pip install shapely", "# Notebook dependency installation is not executed"
    )
    tree = ast.parse(text)
    names = (
        {
            "BsFun",
            "BsFun_derivative",
            "BsFun_second_derivative",
            "BsKnots",
            "BsKnots_derivatives",
            "compute_bspline_derivatives",
            "ControlPointNet",
        }
        if case == "burgers"
        else {
            "BsFun",
            "build_bspline_basis",
            "build_bspline_derivatives",
            "BSplineNet_a",
            "compute_loss_pde_data_icbc",
        }
    )
    definitions = [
        n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in names
    ]
    if len(definitions) != len(names):
        raise ValueError("参考定义结构变化")
    ns = {"torch": torch, "nn": nn, "np": np}
    exec(compile(ast.Module(body=definitions, type_ignores=[]), str(source), "exec"), ns)  # noqa: S102 - 执行摘要锁定的原定义
    meta = json.loads(manifest.read_text())
    if meta["case"] != case:
        raise ValueError("案例身份不匹配")
    if output.exists():
        raise FileExistsError(output)
    output.mkdir(parents=True)
    torch.set_num_threads(1)
    torch.manual_seed(42)
    records = [
        (r, torch.load(manifest.parent / r["path"], weights_only=True)) for r in meta["samples"]
    ]
    epochs = epochs if epochs is not None else (5000 if case == "burgers" else 3000)
    nt, nx = records[0][1]["u"].shape[0], records[0][1]["u"].shape[-1]
    degree = 4 if case == "burgers" else 3

    def bases(cp, count):
        if case == "burgers":
            tk, knots, b = ns["BsKnots"](cp, degree, count)
            d1, d2 = ns["BsKnots_derivatives"](cp, degree, count, knots, tk)
            return tuple(torch.tensor(x, dtype=torch.float32) for x in (b, d1, d2))
        b, knots, tk = ns["build_bspline_basis"](cp, degree, count)
        d1, d2 = ns["build_bspline_derivatives"](cp, degree, count, knots, tk)
        return b, d1, d2

    bt, dt, dtt = bases(100, nt)
    bx, dx, dxx = bases(100 if case == "burgers" else 20, nx)
    data = []
    if case == "burgers":
        ns.update(n_cp_t=100, n_cp_x=100, nu=0.01)
        model = ns["ControlPointNet"](100, 100, 64)
        for r, s in records:
            data.append(
                (
                    r,
                    {
                        "mu": torch.tensor([[s["parameters"]["mu"]]], dtype=torch.float32),
                        "m": torch.tensor([[s["parameters"]["m"]]], dtype=torch.float32),
                        "U": s["u"].float().T,
                        "Bit_x": bx,
                        "Bit_x_derivative": dx,
                        "Bit_x_second_derivative": dxx,
                    },
                )
            )
        loop = next(
            n
            for n in ast.walk(tree)
            if isinstance(n, ast.For) and ast.unparse(n.iter) == "training_data_set"
        )
        epoch_code = compile(
            ast.Module(body=ast.parse("total_loss=0.0").body + [loop], type_ignores=[]),
            str(source),
            "exec",
        )
        ns.update(
            model=model,
            optimizer=torch.optim.Adam(model.parameters(), lr=0.001),
            Bit_t=bt,
            Bit_t_derivative=dt,
            Bit_t_second_derivative=dtt,
            training_data_set=[d for r, d in data if r["split"] == "train"],
        )
    else:
        by, _dy, dyy = bases(20, records[0][1]["u"].shape[1])
        model = ns["BSplineNet_a"](100, 20, 20, 64)
        optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
        data = [
            (r, (torch.tensor([[s["parameters"]["a"]]], dtype=torch.float32), s["u"].float()))
            for r, s in records
        ]

        def loss_fn(sample):
            return ns["compute_loss_pde_data_icbc"](
                model, *sample, bt, bx, by, dt, dxx, dyy, lambda_data=1.0, lambda_phys=0.001
            )

    train = [d for r, d in data if r["split"] == "train"]
    start, history = time.monotonic(), []
    for epoch in range(1, epochs + 1):
        if case == "burgers":
            exec(epoch_code, ns)  # noqa: S102 - 原逐实例训练语句，不修正原对流符号
            total = ns["total_loss"]
        else:
            total = 0.0
            for sample in train:
                loss = loss_fn(sample)[0]
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                total += float(loss.detach())
        history.append(total / len(train))
        if epoch % 500 == 0:
            print(json.dumps({"epoch": epoch, "loss": history[-1]}), flush=True)
    metrics = []
    with torch.no_grad():
        for record, sample in data:
            if record["split"] != "test":
                continue
            if case == "burgers":
                prediction = bt @ model(sample["mu"], sample["m"]) @ bx.T
                truth = sample["U"].T
            else:
                prediction = loss_fn(sample)[3][0]
                truth = sample[1]
            torch.save(
                {"sample_id": record["id"], "prediction": prediction, "target": truth},
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
        "case": case,
        "execution": "original_notebook_functions_same_physical_dataset_paper_parameters",
        "source_sha256": digest,
        "dataset_id": meta["content_id"],
        "epochs": epochs,
        "updates": epochs * len(train),
        "seed": 42,
        "device": "cpu",
        "precision": "fp32",
        "seconds": time.monotonic() - start,
        "history": history,
        "samples": metrics,
        "pde_points": "complete_dataset_grid",
        "loss_weights": {
            "pde": 1 if case == "burgers" else 0.001,
            "data": 15 if case == "burgers" else 1,
            "initial": 0,
            "periodic": 0,
        },
        "differences": "共享修正物理数据；原导数/条件/符号保留。梯形使用文献50实例、100x20x20、PDE权重.001，非notebook默认值。",
    }
    torch.save(model.state_dict(), output / "model.pt")
    (output / "reference.json").write_text(json.dumps(result, ensure_ascii=False, indent=2))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=["burgers", "diffusion_trapezoid"], required=True)
    for name in ("source", "manifest", "output"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    args = parser.parse_args()
    run(args.case, args.source, args.manifest, args.output)
