"""独立参考与 Dojo 实际产物对比；工程一致、学习效果与论文分开。"""

import argparse
import json
from pathlib import Path

import numpy as np
import torch
import yaml

from ai4e_contrib.ability.postproc.gencp.reference import fsi_reference
from ai4e_contrib.ability.transform.gencp.normalization import nt_normalize
from ai4e_core.abilities.eval.trajectory import trajectory_metrics
from ai4e_core.applications.coupled_physics.post import read_results

PAPER = {
    "turek_hron": {
        "cno": [0.0388, 0.1821, 0.2166, 0.0183],
        "sit_fno": [0.0396, 0.1678, 0.1897, 0.0081],
    },
    "double_cylinder": {
        "cno": [0.0279, 0.1150, 0.6208, 0.0055],
        "sit_fno": [0.0522, 0.2397, 0.3987, 0.0061],
    },
    "ntcouple": {"cno": [0.0044, 0.0105, 0.0330], "sit_fno": [0.0085, 0.0364, 0.0270]},
}


def close(a, b):
    """冻结局部 FP32 容差，不因测到误差后放宽。"""
    a, b = torch.as_tensor(a), torch.as_tensor(b)
    dtype = torch.promote_types(a.dtype, b.dtype)
    a, b = a.to(dtype), b.to(dtype)
    return {
        "max_abs": float((a - b).abs().max()),
        "close": bool(torch.allclose(a, b, rtol=1e-4, atol=1e-6)),
    }


def compare(root, dataset, backbone, run):
    """消费明确运行，不猜最新；所有分场分别评价。"""
    root, run = Path(root), Path(run)
    reference = root / "reference"
    output = Path(yaml.safe_load((run / "inputs/config.yaml").read_text())["paths"]["output"])
    fields = ("neutron", "solid", "fluid") if dataset == "ntcouple" else ("fluid", "structure")
    report = {
        "scope": "scaled_not_paper",
        "dataset": dataset,
        "backbone": backbone,
        "run": str(run),
        "fields": {},
        "tolerance": {"rtol": 1e-4, "atol": 1e-6, "metric_ratio": 1.05, "near_zero_absolute": 1e-6},
        "paper": {
            "version": "arxiv:2601.19541v1",
            "values": PAPER[dataset][backbone],
            "eligible": False,
        },
    }
    _single_record, singles = read_results(output / ("single_" + run.name) / "results.json")
    for field in fields:
        original = torch.load(reference / f"{field}.pt", map_location="cpu", weights_only=False)
        actual = torch.load(
            run / f"checkpoints/{field}/latest.pt", map_location="cpu", weights_only=False
        )
        weights = [
            close(original["model"][key], value)
            for key, value in actual["model"].items()
            if value.is_floating_point() or value.is_complex()
        ]
        ema = [
            close(original["ema"][key], value)
            for key, value in actual["ema"].items()
            if value.is_floating_point() or value.is_complex()
        ]
        single = torch.load(
            reference / f"{field}_single.pt", map_location="cpu", weights_only=False
        )
        report["fields"][field] = {
            "updates": actual["updates"],
            "loss": close(original["history"], actual["history"]),
            "weights": {
                "max_abs": max(v["max_abs"] for v in weights),
                "close": all(v["close"] for v in weights),
            },
            "ema": {
                "max_abs": max(v["max_abs"] for v in ema),
                "close": all(v["close"] for v in ema),
            },
            "single_prediction": close(single["prediction"], singles[field][0]),
            "training_loss": {
                "first": actual["history"][0],
                "last": actual["history"][-1],
                "note": "不同训练随机样本的目标损失，不等于固定验证学习效果",
            },
        }
    _record, pairs = read_results(output / ("prediction_" + run.name) / "results.json")
    reference_result = torch.load(reference / "coupled.pt", map_location="cpu", weights_only=False)
    if dataset == "ntcouple":
        expected = {
            field: nt_normalize(value, field, inverse=True).numpy()
            for field, value in zip(fields, reference_result["predictions"])
        }
        reference_report = json.loads((reference / "reference.json").read_text())
        raw_root = reference_report.get("data_root")
        if raw_root is None:
            ledger = json.loads((root / "budget.json").read_text())
            for entry in ledger["runs"]:
                command = entry.get("command", [])
                if (
                    entry.get("status") == "success"
                    and "--data" in command
                    and "--output" in command
                    and Path(command[command.index("--output") + 1]) == reference
                ):
                    raw_root = command[command.index("--data") + 1]
        if raw_root is None:
            raise ValueError("独立参考缺少原始数据来源记录")
        target = {
            field: np.load(Path(raw_root) / "couple_val" / file, mmap_mode="r")[:16]
            .transpose(0, 2, 3, 4, 1)
            .copy()
            for field, file in zip(fields, ("neu.npy", "fuel.npy", "fluid.npy"))
        }
    else:
        p, t = reference_result["physical_prediction"].numpy(), reference_result["target"].numpy()
        expected = {"fluid": p[..., :3], "structure": p[..., 3:4]}
        target = {"fluid": t[..., :3], "structure": t[..., 3:4]}
    for field in fields:
        report["fields"][field]["coupled_prediction"] = close(expected[field], pairs[field][0])
        report["fields"][field]["target"] = close(target[field], pairs[field][1])
    if dataset != "ntcouple":
        p = np.concatenate([expected[f] for f in fields], axis=-1)
        t = np.concatenate([target[f] for f in fields], axis=-1)
        ep, et, *_ = fsi_reference(p, t)
        p = np.concatenate([pairs[f][0] for f in fields], axis=-1)
        ap, at, *_ = fsi_reference(p, t)
        expected = {"fluid": ep[..., :3], "structure": ep[..., 3:4]}
        target = {"fluid": et[..., :3], "structure": et[..., 3:4]}
        pairs = {"fluid": (ap[..., :3], at[..., :3]), "structure": (ap[..., 3:4], at[..., 3:4])}
    for field in fields:
        ref = trajectory_metrics(torch.from_numpy(expected[field]), torch.from_numpy(target[field]))
        ours = trajectory_metrics(*(torch.from_numpy(v) for v in pairs[field]))
        scores = zip(ref["component_relative_l2"], ours["component_relative_l2"])
        report["fields"][field]["metrics"] = {
            "reference": ref,
            "dojo": ours,
            "passed": all(
                a is not None and b is not None and b <= max(a * 1.05, 1e-6) for a, b in scores
            ),
        }
    report["engineering_passed"] = all(
        all(
            value[name]["close"]
            for name in (
                "loss",
                "weights",
                "ema",
                "single_prediction",
                "coupled_prediction",
                "target",
            )
        )
        and value["metrics"]["passed"]
        for value in report["fields"].values()
    )
    if (root / "budget.json").exists():
        report["budget"] = json.loads((root / "budget.json").read_text())
    (root / "comparison.json").write_text(json.dumps(report, indent=2, allow_nan=False))
    print(
        json.dumps(
            {
                "engineering_passed": report["engineering_passed"],
                "fields": {
                    f: {k: v for k, v in info.items() if k != "metrics"}
                    for f, info in report["fields"].items()
                },
            }
        ),
        flush=True,
    )
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("root", "dataset", "backbone", "run"):
        parser.add_argument("--" + name, required=True)
    args = parser.parse_args()
    raise SystemExit(
        0 if compare(args.root, args.dataset, args.backbone, args.run)["engineering_passed"] else 1
    )
