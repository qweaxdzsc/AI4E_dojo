"""参数化 PDE 固定结果评价；不加载检查点、不构建模型。"""

import json
from pathlib import Path

from ai4e_core.abilities.data.save.bundle import file_digest, load_bundle, save_json


def post(cfg, *, session, **components):
    """从已保存预测重算与原版一致的逐实例误差。"""
    source = Path(cfg["post"]["results"])
    manifest = json.loads(source.read_text())
    if manifest.get("status") != "complete" or not manifest.get("samples"):
        raise ValueError("固定预测清单未完成")
    if session.dry_run:
        session.report({"status": "checked", "results": str(source)}, stage="post")
        return None
    rows = []
    for item in manifest["samples"]:
        path = (source.parent / f"{item['id']}.pt").resolve()
        if not path.is_relative_to(source.parent.resolve()):
            raise ValueError("固定预测路径越界")
        if item.get("sha256") != file_digest(path):
            raise ValueError("固定预测内容已变化或缺少摘要")
        sample = load_bundle(path)
        if sample["sample_id"] != item["id"]:
            raise ValueError("固定预测样本身份不一致")
        error = sample["prediction"] - sample["target"]
        norm = float(sample["target"].norm())
        time_error = error.double().flatten(1).norm(dim=1)
        time_norm = sample["target"].double().flatten(1).norm(dim=1)
        rows.append(
            {
                "id": item["id"],
                "mae": float(error.abs().mean()),
                "l2": float(error.norm()),
                "relative_l2": float(error.norm()) / norm if norm else None,
                "max_error": float(error.abs().max()),
                "mean_time_relative_l2": float((time_error / (time_norm + 1e-12)).mean()),
            }
        )
    valid = [r["relative_l2"] for r in rows if r["relative_l2"] is not None]
    report = {
        "status": "complete",
        "samples": rows,
        "results": str(source),
        "relative_l2_valid_samples": len(valid),
        "mean_relative_l2": sum(valid) / len(valid) if valid else None,
        "mean_time_relative_l2": sum(r["mean_time_relative_l2"] for r in rows) / len(rows),
    }
    output = session.output_dir("post") / "metrics.json"
    save_json(output, report)
    session.record_asset("metrics", output, kind="other", stage="post", dependencies=[source])
    for name in ("mean_relative_l2", "mean_time_relative_l2"):
        if report[name] is not None:
            session.record_metric(
                name,
                report[name],
                stage="post",
                assets=[source.parent],
                semantics={
                    "field": "u",
                    "unit": "1",
                    "split": "test",
                    "statistic": name,
                    "data_identity": manifest["dataset_identity"],
                },
            )
    session.report(report, stage="post")
    return report


def report_fields(results, output, *, time_unit, consume=None):
    """仅读固定结果，校验网格及派生输出，输出数值表、误差曲线与场图。"""
    from pathlib import Path

    from ai4e_core.abilities.data.save.array_manifest import digest, read_arrays
    from ai4e_core.abilities.data.save.arrays import save_json
    from ai4e_core.abilities.eval.trajectory import named_frame_metrics
    from ai4e_core.abilities.postproc.visualization.trajectory import (
        plot_named_field,
        plot_named_frames,
    )
    from ai4e_core.abilities.report.tabular import export_frame_metrics

    record, arrays = read_arrays(results, kind="named-field-result-v1")
    meta = record["metadata"]
    root = Path(output)
    root.mkdir(parents=True, exist_ok=True)
    for entry in meta["meshes"]:
        path = (Path(results).parent / entry["path"]).resolve()
        if (
            not path.is_relative_to(Path(results).parent.resolve())
            or digest(path) != entry["sha256"]
        ):
            raise ValueError("固定网格改变或越界")
    metrics = named_frame_metrics(
        arrays["prediction"],
        arrays["target"],
        ids=meta["ids"],
        times=meta["times"],
        fields=meta["fields"],
        units=meta["units"],
    )
    if consume:
        metrics["derived"] = consume(arrays, meta["derived"])
    save_json(root / "metrics.json", metrics)
    export_frame_metrics(root / "metrics.csv", metrics)
    plot_named_frames(root / "errors.png", metrics, time_unit=time_unit)
    plot_named_field(
        root / "field.png",
        arrays["prediction"][0, -1, :, -1],
        arrays["target"][0, -1, :, -1],
        arrays["coordinates"][0],
        field=meta["fields"][-1],
        unit=meta["units"][-1],
    )
    return {
        "mse": metrics["mse"],
        "mean_relative_l2": metrics["mean_relative_l2"],
        "samples": len(meta["ids"]),
        "metrics": str(root / "metrics.json"),
        "field_metrics": [
            {
                "name": "physical_mse_" + name,
                "value": sum(row["mse"] for row in metrics["rows"] if row["field"] == name)
                / sum(row["field"] == name for row in metrics["rows"]),
                "semantics": {
                    "field": name,
                    "unit": unit + "^2",
                    "split": meta.get("split", "evaluation"),
                    "statistic": "sample_time_equal_mean_mse",
                    "data_identity": digest(results),
                    "space": "physical",
                },
            }
            for name, unit in zip(meta["fields"], meta["units"], strict=True)
        ],
    }
