"""原解析场、相同拟合预算下的物理样条与有限差分导数消融。"""

import argparse
import ast
import hashlib
import json
import time
from pathlib import Path

import numpy as np
import torch

from ai4e_contrib.ability.model.pibsnet.spline import basis


def run(source, output):
    """保存六个场及五种导数的全数组和内点误差；计时包括准备与拟合。"""
    lock = (
        Path(__file__).resolve().parents[3]
        / "packages/ai4e-contrib/ability/model/pibsnet/source.json"
    )
    expected = json.loads(lock.read_text())["reference_files"]["src/derivatives_ablation.ipynb"]
    if hashlib.sha256(source.read_bytes()).hexdigest() != expected:
        raise ValueError("参考源码摘要与锁定来源不一致")
    if output.exists():
        raise FileExistsError(output)
    text = "\n".join(
        "".join(c["source"])
        for c in json.loads(source.read_text())["cells"]
        if c["cell_type"] == "code"
    )
    names = [
        "F_true",
        "dF_dt",
        "dF_dx",
        "d2F_dtt",
        "d2F_dxx",
        "d2F_dtx",
        "finite_difference_derivatives",
    ]
    definitions = [
        n for n in ast.parse(text).body if isinstance(n, ast.FunctionDef) and n.name in names
    ]
    if {n.name for n in definitions} != set(names):
        raise ValueError("消融参考定义变化")
    ns = {"np": np}
    exec(compile(ast.Module(body=definitions, type_ignores=[]), str(source), "exec"), ns)  # noqa: S102 - 明确执行摘要锁定的参考源码
    t, x = np.linspace(0, 1, 121), np.linspace(-1, 1, 121)
    tt, xx = np.meshgrid(t, x, indexing="ij")
    truth = [ns[n](tt, xx) for n in names[:6]]
    start = time.perf_counter()
    bt = [v.numpy() for v in basis(torch.from_numpy(t), bounds=(0, 1), control_points=20, degree=4)]
    bx = [
        v.numpy() for v in basis(torch.from_numpy(x), bounds=(-1, 1), control_points=20, degree=4)
    ]
    built = time.perf_counter()
    # C-order flatten 的独立设计矩阵；不继承原 notebook 的 vec 顺序假设。
    design = np.einsum("ti,xj->txij", bt[0], bx[0]).reshape(121**2, 20**2)
    coefficients = np.linalg.solve(
        design.T @ design + 1e-10 * np.eye(400), design.T @ truth[0].ravel()
    ).reshape(20, 20)
    fitted = time.perf_counter()
    orders = [(0, 0), (1, 0), (0, 1), (2, 0), (0, 2), (1, 1)]
    spline = [bt[a] @ coefficients @ bx[b].T for a, b in orders]
    differentiated = time.perf_counter()
    fd = [truth[0], *ns["finite_difference_derivatives"](truth[0], t, x)]
    end = time.perf_counter()
    mask = np.ones((121, 121), dtype=bool)
    mask[[0, -1], :] = False
    mask[:, [0, -1]] = False
    metrics = {}
    for name, exact, bs, diff in zip(names[:6], truth, spline, fd, strict=True):
        metrics[name] = {}
        for method, predicted in [("spline", bs), ("finite_difference", diff)]:
            error = (predicted - exact)[mask]
            metrics[name][method] = {
                "relative_l2": float(np.linalg.norm(error) / np.linalg.norm(exact[mask])),
                "mae": float(np.abs(error).mean()),
                "max_error": float(np.abs(error).max()),
                "rmse": float(np.sqrt(np.mean(error**2))),
            }
    output.mkdir(parents=True)
    np.savez_compressed(
        output / "fields.npz",
        t=t,
        x=x,
        truth=truth,
        spline=spline,
        finite_difference=fd,
        mask=mask,
        coefficients=coefficients,
    )
    result = {
        "status": "complete",
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "grid": [121, 121],
        "control_points": [20, 20],
        "degree": 4,
        "ridge": 1e-10,
        "evaluation": "exclude_one_cell_boundary",
        "metrics": metrics,
        "seconds": {
            "basis": built - start,
            "fit": fitted - built,
            "spline_derivatives": differentiated - fitted,
            "finite_difference": end - differentiated,
        },
    }
    (output / "derivatives.json").write_text(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    run(args.source, args.output)
