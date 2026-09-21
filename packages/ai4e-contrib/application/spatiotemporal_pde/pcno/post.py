"""圆柱固定预测的指标绑定，未来几何仅用于共同评价域。"""

import numpy as np
import torch

from ai4e_core.abilities.constraint.continuity import staggered_divergence, weighted_mean_square
from ai4e_core.abilities.constraint.field_supervision import interior_mask
from ai4e_core.abilities.eval.field_windows import field_metrics


def metrics(arrays):
    """物理空间逐时间字段指标及真实/预测几何散度，含用户速度模长消费。"""
    truth = np.asarray(arrays["truth"])
    mask = interior_mask(torch.from_numpy((truth[..., 3] > 0.02).copy()))
    valid = mask[..., :-1, :-1] & mask[..., 1:, :-1] & mask[..., :-1, 1:]
    result = {}
    for key in ("initial", "persistence", "supervised", "physics"):
        predicted = np.asarray(arrays[key])
        fluid = field_metrics(predicted[..., :3], truth[..., :3], mask.numpy())
        structure = field_metrics(predicted[..., 3:], truth[..., 3:], np.ones_like(truth[..., 3]))
        div = staggered_divergence(torch.from_numpy(predicted[..., :2].copy()).double())
        predicted_mask = interior_mask(torch.from_numpy((predicted[..., 3] > 0.02).copy()))
        pv = (
            predicted_mask[..., :-1, :-1]
            & predicted_mask[..., 1:, :-1]
            & predicted_mask[..., :-1, 1:]
        )
        result[key] = {
            "fluid": fluid,
            "structure": structure,
            "divergence_rms": float(weighted_mean_square(div, valid).sqrt()),
            "divergence_by_time": [
                float(weighted_mean_square(d, v).sqrt()) for d, v in zip(div, valid)
            ],
            "predicted_geometry_divergence_rms": float(weighted_mean_square(div, pv).sqrt())
            if pv.any()
            else None,
            "predicted_geometry_valid_count": int(pv.sum()),
            "reference_geometry_valid_count": int(valid.sum()),
        }
    if "speed" in arrays:
        result["derived_speed"] = {
            "mean": float(np.mean(arrays["speed"])),
            "shape": list(arrays["speed"].shape),
        }
    return result


def summarize(report: str, output: str) -> str:
    """先按轨迹聚合，再等权汇总轨迹指标；清楚区分真实与预测几何诊断。"""
    import json
    from pathlib import Path

    from ai4e_core.abilities.data.save.arrays import save_json
    from ai4e_core.abilities.eval.field_windows import combine_field_metrics

    windows = json.loads(Path(report).read_text())["results"]
    identities = sorted({x["metadata"]["id"] for x in windows})
    trajectories = {}
    for identity in identities:
        rows = [x["metrics"] for x in windows if x["metadata"]["id"] == identity]
        combined = {}
        for variant in ("initial", "persistence", "supervised", "physics"):
            count = np.array([r[variant]["reference_geometry_valid_count"] for r in rows])
            combined[variant] = {
                "fluid": combine_field_metrics([r[variant]["fluid"] for r in rows]),
                "structure": combine_field_metrics([r[variant]["structure"] for r in rows]),
                "divergence_rms": float(
                    np.sqrt(
                        sum(r[variant]["divergence_rms"] ** 2 * c for r, c in zip(rows, count))
                        / count.sum()
                    )
                ),
            }
        trajectories[identity] = combined
    aggregate = {}

    def equal_mean(values):
        return [
            None
            if any(row[j] is None for row in values)
            else float(np.mean([row[j] for row in values]))
            for j in range(len(values[0]))
        ]

    for variant in ("initial", "persistence", "supervised", "physics"):
        aggregate[variant] = {
            field: {
                metric: equal_mean([trajectories[i][variant][field][metric] for i in identities])
                for metric in ("mae", "rmse", "relative_l2")
            }
            for field in ("fluid", "structure")
        }
        aggregate[variant]["divergence_rms"] = float(
            np.mean([trajectories[i][variant]["divergence_rms"] for i in identities])
        )
    save_json(
        output,
        {
            "scope": "held-out validation; equal trajectory aggregation; no independent test",
            "windows": len(windows),
            "trajectories": trajectories,
            "aggregate": aggregate,
            "window_metrics": str(report),
        },
    )
    return str(Path(output).resolve())
