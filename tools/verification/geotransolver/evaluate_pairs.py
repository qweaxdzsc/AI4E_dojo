"""独立参考完整评价，与公开 recipe 固定结果及更新后权重对照。"""

import argparse
import json
from pathlib import Path

import numpy as np
import torch
import yaml

from .reference import cached_cpu_radius, load_reference
from .run_acceptance import WORK


def evaluate(case):
    """全部评价样本、末批不丢弃；物理误差最后在CPU float64复算。"""
    torch.set_num_threads(4)
    cfg = yaml.safe_load((WORK / "implementation" / f"{case}-frozen.yaml").read_text())
    run = max(
        (WORK / case / "paired-runs").glob("*/summary.json"), key=lambda p: p.stat().st_mtime_ns
    )
    summary = json.loads(run.read_text())
    if summary["research_status"] != "completed":
        raise ValueError("Dojo研究未完成")
    source = torch.load(
        WORK / case / "reference/checkpoint.pt", map_location="cpu", weights_only=False
    )
    dojo = torch.load(
        summary["reports"]["train"]["checkpoint"], map_location="cpu", weights_only=False
    )
    diffs = {}
    for name, value in source["model"].items():
        torch.testing.assert_close(value, dojo["model"][name], atol=1e-6, rtol=1e-5, msg=name)
        diffs[name] = float((value - dojo["model"][name]).abs().max())
    np.testing.assert_allclose(source["history"], dojo["history"], atol=1e-6, rtol=1e-5)
    preparation = Path(cfg["inputs"]["infer"]["preparation"])
    prep = json.loads(preparation.read_text())
    split = "test" if case == "darcy" else "validation"
    path = preparation.parent / prep["splits"][split]
    record = json.loads(path.read_text())
    arrays = {
        k: np.load(path.parent / v["path"], mmap_mode="r") for k, v in record["fields"].items()
    }
    reference = load_reference()
    cached_cpu_radius(reference)
    model = reference.GeoTransolver(**cfg["model"]).to("mps")
    model.load_state_dict(source["model"])
    model.eval()
    count = len(arrays["target"])
    size = cfg["infer"]["batch_size"]
    outputs = []
    stats = prep["statistics"]
    normalized = []
    with torch.no_grad():
        for start in range(0, count, size):
            end = min(count, start + size)

            def get(key, start=start, end=end):
                return torch.from_numpy(np.array(arrays[key][start:end], copy=True)).to(
                    "mps", dtype=torch.float32
                )

            names = (
                ["local_embedding", "geometry"]
                if case == "darcy"
                else ["local_embedding", "geometry", "local_positions", "global_embedding"]
            )
            inputs = {k: get(k) for k in names}
            raw = model(**inputs)
            if case == "darcy":
                pred = (
                    raw * raw.new_tensor(stats["sol"]["std"]) + raw.new_tensor(stats["sol"]["mean"])
                )[:, None]
            else:
                b, n, _ = raw.shape
                pred = raw.reshape(b, n, 10, 5).permute(0, 2, 1, 3).clone()
                pred[..., :3] += inputs["local_embedding"][:, None]
                normalized.append(float(torch.nn.functional.mse_loss(pred, get("target"))))
                pred[..., :3] = pred[..., :3] * pred.new_tensor(
                    stats["positions"]["std"]
                ) + pred.new_tensor(stats["positions"]["mean"])
            outputs.append(pred.cpu().numpy())
    prediction = np.concatenate(outputs)
    results = Path(summary["reports"]["infer"]["results"])
    result = json.loads(results.read_text())
    actual = np.load(results.parent / result["fields"]["prediction"]["path"])
    np.testing.assert_allclose(prediction, actual, atol=1e-6, rtol=1e-5)
    truth = np.asarray(arrays["physical_target"], dtype=np.float64)
    delta = prediction.astype(np.float64) - truth
    ratios = np.linalg.norm(delta.reshape(count, -1), axis=1) / np.linalg.norm(
        truth.reshape(count, -1), axis=1
    )
    report = {
        "case": case,
        "updates": source["updates"],
        "samples": count,
        "weight_max_abs_diff": max(diffs.values()),
        "prediction_max_abs_diff": float(np.abs(prediction - actual).max()),
        "loss_max_abs_diff": float(np.abs(np.array(source["history"]) - dojo["history"]).max()),
        "mean_physical_relative_l2": float(ratios.mean()),
        "physical_mse": float(np.mean(delta**2)),
        "reference_normalized_mse": float(np.mean(normalized)) if normalized else None,
        "first_training_loss": source["history"][0],
        "last_training_loss": source["history"][-1],
        "paper_reproduction": False,
        "dojo_summary": str(run),
    }
    output = WORK / case / "comparison.json"
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report))
    return report


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--case", required=True)
    a = p.parse_args()
    evaluate(a.case)
