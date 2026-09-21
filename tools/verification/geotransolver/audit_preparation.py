# ruff: noqa: S102
# 独立参考执行经版本核对的本地源码定义，不执行网络下载内容。
"""由独立原数据及上游读取/统计定义核对准备，禁止用迁移函数作为真值。"""

from __future__ import annotations

import argparse
import ast
import json
import re
import types
from pathlib import Path

import numpy as np
import pyvista as pv
import torch
from scipy.io import loadmat

from .reference import DEFAULT_SOURCE, locked_source


def definitions(path, names, namespace):
    tree = ast.parse(locked_source(path))
    nodes = [
        n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in names
    ]
    exec(
        "from __future__ import annotations\n"
        + ast.unparse(ast.Module(body=nodes, type_ignores=[])),
        namespace,
    )


def audit_darcy(raw, prepared):
    from ai4e_core.applications.parametric_pde.trainprep import read_field_inputs

    ns = {"torch": torch}
    definitions(
        DEFAULT_SOURCE / "examples/cfd/darcy_transolver/darcy_datapipe_fix.py",
        ["UnitTransformer"],
        ns,
    )
    stats = {}
    counts = {}
    for split, suffix, count in [("train", "smooth1", 1000), ("test", "smooth2", 200)]:
        data = loadmat(next(Path(raw).rglob(f"*{suffix}.mat")))
        x = torch.from_numpy(data["coeff"][:count, ::5, ::5].reshape(count, -1)).float()
        y = torch.from_numpy(data["sol"][:count, ::5, ::5].reshape(count, -1)).float()
        if split == "train":
            stats = {"x": ns["UnitTransformer"](x), "y": ns["UnitTransformer"](y)}
        xx, yy = np.meshgrid(np.linspace(0, 1, 85), np.linspace(0, 1, 85))
        coords = torch.tensor(np.c_[xx.ravel(), yy.ravel()], dtype=torch.float32)
        _, arrays = read_field_inputs(prepared, split)
        np.testing.assert_array_equal(
            arrays["local_embedding"][..., :2], coords[None].expand(count, -1, -1).numpy()
        )
        np.testing.assert_array_equal(
            arrays["local_embedding"][..., 2], stats["x"].encode(x).numpy()
        )
        np.testing.assert_array_equal(arrays["target"][..., 0], stats["y"].encode(y).numpy())
        np.testing.assert_array_equal(arrays["physical_target"][:, 0, :, 0], y.numpy())
        counts[split] = count
    return {
        "counts": counts,
        "inputs_max_abs_diff": 0.0,
        "targets_max_abs_diff": 0.0,
        "statistics": "original UnitTransformer",
    }


def audit_bumper(raw, prepared):
    from ai4e_core.applications.parametric_pde.trainprep import read_field_inputs

    root = Path(raw) / "CURATED_DATA_VTP"
    source = DEFAULT_SOURCE / "examples/structural_mechanics/crash/vtp_reader.py"
    text = source.read_text().replace(
        're.match(r"displacement_t0\\.[0-9]{3}$", name)',
        're.match(r"displacement_t[0-9]+\\.[0-9]+$", name)',
    )
    tree = ast.parse(text)
    nodes = [
        n
        for n in tree.body
        if isinstance(n, ast.FunctionDef)
        and n.name in ["load_vtp_file", "extract_mesh_connectivity_from_polydata"]
    ]
    ns = {"np": np, "pv": pv, "re": re, "torch": torch}
    exec(ast.unparse(ast.Module(body=nodes, type_ignores=[])), ns)
    definitions(
        DEFAULT_SOURCE / "examples/structural_mechanics/crash/datapipe.py", ["CrashBaseDataset"], ns
    )
    ns["EPS"] = 1e-8
    position = {}
    dynamics = {}
    identities = {}
    for split, folder in [("train", "TRAINING_DATA"), ("validation", "VALIDATION_DATA")]:
        _, arrays = read_field_inputs(prepared, split)
        record, _ = read_field_inputs(prepared, split)
        identities[split] = record["metadata"]["ids"]
        position[split] = []
        dynamics[split] = []
        for identity in identities[split]:
            pos, _, fields = ns["load_vtp_file"](root / folder / (identity + ".vtp"))
            position[split].append(torch.tensor(pos[:11], dtype=torch.float32))
            features = []
            for prefix in ("effective_plastic_strain_t", "stress_vm_t"):
                names = sorted(
                    [n for n in fields if n.startswith(prefix)],
                    key=lambda n: float(n[len(prefix) :]),
                )
                assert [float(n[len(prefix) :]) for n in names[:11]] == list(range(0, 101, 10))
                features.append(np.stack([fields[n] for n in names[:11]], axis=0)[..., None])
            dynamics[split].append(np.concatenate(features, axis=-1).astype("float32"))
    holder = types.SimpleNamespace(
        dt=10, num_samples=len(position["train"]), mesh_pos_seq=position["train"]
    )
    stats = ns["CrashBaseDataset"]._compute_autoreg_node_stats(holder)
    for split, _positions in position.items():
        _, arrays = read_field_inputs(prepared, split)
        pos = torch.stack(_positions)
        norm = (pos - stats["pos_mean"]) / (stats["pos_std"] + 1e-8)
        dynamic = np.stack(dynamics[split])
        np.testing.assert_array_equal(arrays["local_embedding"], norm[:, 0].numpy())
        np.testing.assert_array_equal(
            arrays["target"], np.concatenate((norm[:, 1:].numpy(), dynamic[:, 1:]), axis=-1)
        )
        np.testing.assert_array_equal(
            arrays["physical_target"], np.concatenate((pos[:, 1:].numpy(), dynamic[:, 1:]), axis=-1)
        )
    return {
        "counts": {k: len(v) for k, v in position.items()},
        "inputs_max_abs_diff": 0.0,
        "targets_max_abs_diff": 0.0,
        "statistics": "original CrashBaseDataset._compute_autoreg_node_stats; corrected timestamp reader",
    }


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--case", required=True)
    p.add_argument("--raw", required=True)
    p.add_argument("--prepared", required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    torch.set_num_threads(4)
    result = (audit_darcy if a.case == "darcy" else audit_bumper)(a.raw, a.prepared)
    a.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))
