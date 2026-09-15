"""从真实训练历史核验评价预算并拟合经验关系，不宣称理论上界。"""

import argparse
import json
from pathlib import Path

import numpy as np
import torch


def summarize(checkpoint, output):
    """严格核对2000轮和41次完整评价，筛选训练损失再拟合log-log关系。"""
    state = torch.load(checkpoint, map_location="cpu", weights_only=False)
    history = state["history"]
    evaluated = [r for r in history if r["evaluation"] is not None]
    expected = [*range(1, 2000, 50), 2000]
    if state["epoch"] != 2000 or [r["epoch"] for r in evaluated] != expected:
        raise ValueError("正式泛化预算或评价轮次不完整")
    if any(r["evaluation"]["samples"] != 30 for r in evaluated):
        raise ValueError("泛化评价必须覆盖全部30测试实例")
    selected = [
        r
        for r in evaluated
        if np.isfinite(r["loss"])
        and np.isfinite(r["evaluation"]["max_absolute_error"])
        and 0 < r["loss"] <= 1
        and r["evaluation"]["max_absolute_error"] > 0
    ]
    if len(selected) < 2:
        raise ValueError("损失筛选后不足两个点，不能拟合")
    x = np.log([r["loss"] for r in selected])
    y = np.log([r["evaluation"]["max_absolute_error"] for r in selected])
    if np.ptp(x) == 0:
        raise ValueError("训练损失无变化，不能拟合")
    slope, intercept = np.polyfit(x, y, 1)
    result = {
        "status": "complete",
        "checkpoint": str(checkpoint),
        "evaluations": evaluated,
        "fit_points": len(selected),
        "slope": float(slope),
        "intercept": float(intercept),
        "protocol": "sample-mean weighted training loss, loss<=1, global maximum absolute error over all 30 samples and all points; corrected Dojo equations; empirical correlation only",
    }
    if output.exists():
        raise FileExistsError(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    summarize(args.checkpoint, args.output)
