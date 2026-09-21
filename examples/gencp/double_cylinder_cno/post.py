"""固定预测的参考处理、逐场评价、绘图与导出。"""

from pathlib import Path

import numpy as np
from configuration import load_configuration, plain

from ai4e_contrib.ability.postproc.gencp.reference import fsi_reference
from ai4e_core import run
from ai4e_core.applications.coupled_physics.post import (
    evaluate_fields,
    export_analysis,
    read_results,
)
from ai4e_core.base.config.conventions import resolve_input


def post(cfg, results=None):
    """只读固定结果；原始预测保留，评价处理形成独立派生数组。"""
    cfg = plain(cfg)
    session = run.TrainingRun()
    if session.dry_run:
        return None
    results = resolve_input(results, cfg["inputs"]["post"]["results"], name="post.results")
    if not results:
        raise ValueError("post 缺少固定预测结果")
    record, pairs = read_results(results)
    raw_metrics = evaluate_fields(pairs)
    derived = {}
    if cfg["dataset"]["name"] != "ntcouple":
        prediction = np.concatenate((pairs["fluid"][0], pairs["structure"][0]), axis=-1)
        target = np.concatenate((pairs["fluid"][1], pairs["structure"][1]), axis=-1)
        masked, truth, smoothed, mask = fsi_reference(prediction, target)
        pairs = {
            "fluid": (masked[..., :3], truth[..., :3]),
            "structure": (masked[..., 3:4], truth[..., 3:4]),
        }
        derived = {"smoothed": smoothed, "evaluation_mask": mask}
    metrics = {"raw": raw_metrics, "reference": evaluate_fields(pairs)}
    output = session.output_dir("post") / "analysis"
    report = export_analysis(
        pairs, metrics, output, metadata=record, plots=cfg["post"]["plots"], derived=derived
    )
    session.record_asset("analysis", report, kind="other", stage="post", dependencies=[results, Path(results).parent])
    for mode, fields in metrics.items():
        for field, values in fields.items():
            for component, value in enumerate(values["component_relative_l2"]):
                session.record_metric(f"{mode}/{field}/{component}/relative_l2", value,
                    stage="post", assets=[results, Path(results).parent], semantics={
                        "field": field, "component": component, "unit": "1", "split": "couple_val",
                        "statistic": "mean_sample_trajectory_relative_l2", "processing": mode,
                        "data_identity": {
                            "physical_frames": record["metadata"].get("physical_frames"),
                            "targets": {name: item["sha256"]["target"]
                                        for name, item in record["fields"].items()},
                        },
                    })
    session.report({"metrics": report}, stage="post")
    return report


if __name__ == "__main__":
    raise SystemExit(
        run.launch({"post": post}, script=__file__, only=["post"], config_loader=load_configuration)
    )
