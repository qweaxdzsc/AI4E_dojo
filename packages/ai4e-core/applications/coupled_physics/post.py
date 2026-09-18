"""固定耦合预测分析，不导入或重建任何网络。"""

import csv
from pathlib import Path

import numpy as np
import torch

from ai4e_core.abilities.data.save.arrays import save_json, save_npy
from ai4e_core.abilities.eval.trajectory import trajectory_metrics
from ai4e_core.abilities.postproc.visualization.trajectory import plot_error_curve, plot_frame

from .contracts import file_digest, read_record


def read_results(path):
    """读固定预测和真值；拒绝非数值 pickle 与形状漂移。"""
    path = Path(path)
    record = read_record(path, "coupled_results_v1")
    pairs = {}
    for name, field in record["fields"].items():
        for role in ("prediction", "target"):
            source = (path.parent / field[role]).resolve()
            if not source.is_relative_to(path.parent.resolve()):
                raise ValueError("结果路径越界")
            if field.get("sha256") and file_digest(source) != field["sha256"][role]:
                raise ValueError("固定数组内容改变")
        prediction = np.load(path.parent / field["prediction"], allow_pickle=False)
        target = np.load(path.parent / field["target"], allow_pickle=False)
        if list(prediction.shape) != field["shape"] or prediction.shape != target.shape:
            raise ValueError("固定结果形状损坏")
        pairs[name] = (prediction, target)
    return record, pairs


def evaluate_fields(pairs):
    """逐场时空物理量评价，输出可独立 JSON 保存的数值。"""
    return {
        name: trajectory_metrics(torch.from_numpy(pred), torch.from_numpy(target))
        for name, (pred, target) in pairs.items()
    }


def export_analysis(pairs, metrics, output, *, metadata, plots=True, derived=None):
    """保存派生数组、轻量指标和静态图；所有输入来自固定结果。"""
    output = Path(output)
    if output.exists():
        raise FileExistsError(output)
    output.mkdir(parents=True)
    for name, (prediction, target) in pairs.items():
        if plots:
            for component in range(prediction.shape[-1]):
                plot_frame(
                    prediction, target, output / f"{name}_{component}.png", component=component
                )
            metric = trajectory_metrics(torch.from_numpy(prediction), torch.from_numpy(target))
            plot_error_curve(metric["frame_component_relative_l2"], output / f"{name}_frames.png")
    for name, value in (derived or {}).items():
        save_npy(output / f"{name}.npy", value)
    with (output / "components.csv").open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["field", "component", "relative_l2"])
        for name, (prediction, target) in pairs.items():
            values = trajectory_metrics(torch.from_numpy(prediction), torch.from_numpy(target))
            for component, value in enumerate(values["component_relative_l2"]):
                writer.writerow([name, component, value])
    report = {"scope": "scaled_not_paper_reproduction", "metadata": metadata, "metrics": metrics}
    save_json(output / "metrics.json", report)
    return str((output / "metrics.json").resolve())
