"""已选原案例在Dojo的独立数据、原函数对照及完整阶段验收。"""

import argparse
import ast
import json
import pickle
import sys
from pathlib import Path

import numpy as np
import torch
import yaml
from torch import nn
from trapezoid_dojo import launch

from ai4e_contrib.ability.model.pibsnet import component
from ai4e_contrib.application.datasets.parametric import Dataset
from ai4e_contrib.application.datasets.parametric import component as data_component
from ai4e_core.applications.parametric_pde.model import build_model

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "recipes/parametric_pde"))
from configuration import defaults


def originals(reference, case):
    """只读原基线的数据与权重，禁止使用共享修正数据。"""
    if case == "neumann_diffusion":
        with (reference / case / "checkpoints/dataset_seed42.pkl").open("rb") as f:
            payload = pickle.load(f)
        return payload["train_data"], payload["test_data"]
    return [
        torch.load(reference / case / "data" / name, weights_only=False)
        for name in ["train.pt", "test.pt"]
    ]


def prepare(root, reference, case):
    """数据与初始权重逐值相同后调用真实rawprep/trainprep。"""
    root.mkdir(parents=True, exist_ok=False)
    cfg = defaults(case)
    for parent, key, value in [
        (cfg["dataset"], "manifest", "datasets/manifest.json"),
        (cfg["trainprep"], "output", "prepared"),
        (cfg, "run_root", "runs"),
        (cfg["post"], "output", "predictions"),
    ]:
        parent[key] = str(root / value)
    cfg["train"].update(device="cpu", log_every=100)
    (root / "config.yaml").write_text(yaml.safe_dump(cfg, allow_unicode=True, sort_keys=False))
    data_component(case).generate({"output": str(root / "datasets")})
    dataset = Dataset(cfg["dataset"]["manifest"])
    for split, original in zip(["train", "test"], originals(reference, case), strict=True):
        for record, expected in zip(dataset.records(split), original, strict=True):
            sample = dataset.read(record)
            torch.testing.assert_close(
                sample["u"],
                expected["S_true" if case == "neumann_diffusion" else "U"],
                rtol=0,
                atol=0,
            )
            for key, value in sample["parameters"].items():
                old = expected["phases" if key == "phase" else key].item()
                assert value == old, (record["id"], key, value, old)
    model = build_model(cfg, component)
    initial = torch.load(reference / case / "checkpoints/initial.pt", weights_only=False)["model"]
    assert model.state_dict().keys() == initial.keys()
    for key, value in model.state_dict().items():
        torch.testing.assert_close(value, initial[key], rtol=0, atol=0)
    (root / "preflight.json").write_text(
        json.dumps(
            {"data_exact": True, "initial_exact": True, "reference": str(reference), "case": case}
        )
    )
    launch(root, "rawprep")
    launch(root, "trainprep")


def reference_definitions(reference, case):
    """独立读取锁定源码定义，与迁入模型不共享数值函数。"""
    path = (
        reference
        / "source"
        / ("neumann_bc.py" if case == "neumann_diffusion" else "advection.ipynb")
    )
    source = path.read_text()
    hashes = json.loads((reference / "source/hashes.json").read_text())
    import hashlib

    assert hashlib.sha256(path.read_bytes()).hexdigest() == hashes[path.name]
    if case == "advection":
        notebook = json.loads(source)
        source = "\n".join("".join(notebook["cells"][i]["source"]) for i in [0, 10])
    tree = ast.parse(source)
    definitions = [
        n
        for n in tree.body
        if isinstance(n, (ast.FunctionDef, ast.ClassDef))
        and n.name
        in {
            "BsFun",
            "BsFun_derivative",
            "BsFun_second_derivative",
            "BsKnots",
            "BsKnots_derivatives",
            "ControlPointNet",
            "BSNetLoss",
            "bspline_eval",
            "bspline_derivs",
            "VanillaPINN",
            "PIDeepONet",
            "BetaPhaseControlPointNet",
            "assign_first_row_direct",
            "compute_bspline_derivatives",
        }
    ]
    ns = {"np": np, "torch": torch, "nn": nn, "device": torch.device("cpu")}
    exec(compile(ast.Module(body=definitions, type_ignores=[]), str(path), "exec"), ns)  # noqa: S102 - 摘要锁定的原定义
    return ns


def original_step(ns, model, sample, bases, case):
    """独立原函数装配原标量损失，保留每项运算顺序。"""
    t, x = bases
    p = sample["parameters"]
    truth = sample["u"].float()
    if case == "neumann_diffusion":
        nu = torch.tensor([[p["nu"]]])
        control = model.forward_U(nu)[0]
        u = ns["bspline_eval"](control, t[0], x[0])
        ut, ux, uxx = ns["bspline_derivs"](control, t[0], x[0], t[1], x[1], t[2], x[2])
        initial = torch.tensor(np.cos(np.pi * sample["axes"]["x"].numpy()), dtype=torch.float32)
        losses = [
            torch.mean((ut - nu.item() * uxx) ** 2),
            torch.mean((u - truth) ** 2),
            torch.mean((u[0] - initial) ** 2),
            torch.mean(ux[:, 0] ** 2) + torch.mean(ux[:, -1] ** 2),
        ]
        loss = 1.0 * losses[0] + 5.0 * losses[1] + 2.0 * losses[2] + 2.0 * losses[3]
    else:
        beta = torch.tensor([[p["beta"]]])
        control = model(beta, torch.tensor([[p["phase"]]]))
        ns["assign_first_row_direct"](control, truth[0].numpy())
        control = control[0]
        u = t[0] @ control @ x[0].T
        ut, ux = ns["compute_bspline_derivatives"](control, t[0], x[0], t[1], x[1])
        residual = ut + beta * ux
        loss = nn.functional.mse_loss(
            residual, torch.zeros_like(residual)
        ) + 10 * nn.functional.mse_loss(u, truth)
    return loss, u


def reference_run(root, reference):
    """同Dojo环境的独立原函数完整预算训练；同时检查全部矩阵与一步梯度。"""
    cfg = yaml.safe_load((root / "config.yaml").read_text())
    case = cfg["case"]
    output = root / "same_environment_reference"
    output.mkdir(exist_ok=False)
    ns = reference_definitions(reference, case)
    dataset = Dataset(cfg["dataset"]["manifest"])
    samples = [dataset.read(r) for r in dataset.records("train")]
    sample = samples[0]
    nt, nx = cfg["model"]["control_points"]
    d = cfg["model"]["degree"]
    bases = []
    for n, axis in [(nt, "t"), (nx, "x")]:
        tk, knots, b = ns["BsKnots"](n, d, len(sample["axes"][axis]))
        first, second = ns["BsKnots_derivatives"](n, d, len(sample["axes"][axis]), knots, tk)
        bases.append([torch.tensor(v, dtype=torch.float32) for v in [b, first, second]])
    torch.manual_seed(42)
    if case == "neumann_diffusion":
        ns["VanillaPINN"](hidden=128)
        ns["PIDeepONet"](branch_hidden=128, trunk_hidden=128)
        model = ns["BSNetLoss"](nt, nx, cfg["model"]["hidden_dim"])
    else:
        model = ns["BetaPhaseControlPointNet"](nx, nt, cfg["model"]["hidden_dim"])
    dojo = build_model(cfg, component)
    for key, value in model.state_dict().items():
        torch.testing.assert_close(value, dojo.state_dict()[key], rtol=0, atol=0)
    prepared = component.prepare(sample, cfg)
    for a, b in zip(bases, prepared["grid_bases"], strict=True):
        for x, y in zip(a, b, strict=True):
            torch.testing.assert_close(x, y, rtol=0, atol=0)
    loss, u = original_step(ns, model, sample, bases, case)
    actual = component.step(dojo, prepared, cfg)["loss"]
    torch.testing.assert_close(loss, actual, rtol=0, atol=0)
    loss.backward()
    actual.backward()
    for a, b in zip(model.parameters(), dojo.parameters(), strict=True):
        torch.testing.assert_close(a.grad, b.grad, rtol=0, atol=0)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    history = []
    for epoch in range(cfg["train"]["max_epochs"]):
        total = 0.0
        if case == "neumann_diffusion":
            optimizer.zero_grad()
        for sample in samples:
            if case == "advection":
                optimizer.zero_grad()
            loss, _ = original_step(ns, model, sample, bases, case)
            if case == "neumann_diffusion":
                total = total + loss
            else:
                loss.backward()
                optimizer.step()
                total += loss.item()
        if case == "neumann_diffusion":
            total.backward()
            optimizer.step()
        value = float(total.detach()) if isinstance(total, torch.Tensor) else total / len(samples)
        history.append(value)
        if (epoch + 1) % 100 == 0:
            print(case, epoch + 1, value, flush=True)
    torch.save({"model": model.state_dict(), "history": history}, output / "last.pt")
    with torch.no_grad():
        for record in dataset.records("test"):
            sample = dataset.read(record)
            _, u = original_step(ns, model, sample, bases, case)
            torch.save({"prediction": u, "target": sample["u"]}, output / (record["id"] + ".pt"))
    (output / "complete.json").write_text(
        json.dumps({"epochs": len(history), "case": case, "single_step_exact": True})
    )


def report(root):
    """真实训练、恢复容器和全预测与同环境原函数逐值比较。"""
    cfg = yaml.safe_load((root / "config.yaml").read_text())
    case = cfg["case"]
    path = next((root / "runs").glob("*/checkpoints/last.pt"))
    state = torch.load(path, weights_only=False)
    reference = torch.load(root / "same_environment_reference/last.pt", weights_only=False)
    epochs = cfg["train"]["max_epochs"]
    updates = epochs if case == "neumann_diffusion" else epochs * 100
    assert (state["epoch"], state["updates"]) == (epochs, updates)
    assert [r["loss"] for r in state["history"]] == reference["history"]
    for k, v in state["model"].items():
        torch.testing.assert_close(v, reference["model"][k], rtol=0, atol=0)
    summary = json.loads((root / "predictions/predictions.json").read_text())
    assert summary["status"] == "complete"
    values = []
    for row in summary["samples"]:
        actual = torch.load(root / "predictions" / (row["id"] + ".pt"), weights_only=False)
        other = torch.load(
            root / "same_environment_reference" / (row["id"] + ".pt"), weights_only=False
        )
        torch.testing.assert_close(actual["prediction"], other["prediction"], rtol=0, atol=0)
        values.append(
            float(
                (actual["prediction"].double() - actual["target"].double()).norm()
                / actual["target"].double().norm()
            )
        )
    result = {
        "status": "complete",
        "case": case,
        "epochs": epochs,
        "updates": updates,
        "mean_relative_l2": float(np.mean(values)),
        "weights_history_predictions_exact": True,
        "python": sys.version,
        "numpy": np.__version__,
        "torch": torch.__version__,
        "per_sample_relative_l2": values,
        "std_relative_l2": float(np.std(values)),
        "checkpoint": str(path),
    }
    (root / "verification.json").write_text(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["prepare", "reference", "train", "report"])
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--reference", type=Path)
    parser.add_argument("--case")
    args = parser.parse_args()
    torch.set_num_threads(1)
    if args.action == "prepare":
        prepare(args.root, args.reference, args.case)
    elif args.action == "reference":
        reference_run(args.root, args.reference)
    elif args.action == "train":
        launch(args.root, "train")
        launch(args.root, "post")
    else:
        print(report(args.root))
