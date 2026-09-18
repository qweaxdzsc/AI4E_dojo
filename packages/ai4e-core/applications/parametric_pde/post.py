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
        rows.append({"id": item["id"], "mae": float(error.abs().mean()),
                     "l2": float(error.norm()), "relative_l2": float(error.norm()) / norm if norm else None,
                     "max_error": float(error.abs().max()),
                     "mean_time_relative_l2": float((time_error / (time_norm + 1e-12)).mean())})
    valid = [r["relative_l2"] for r in rows if r["relative_l2"] is not None]
    report = {"status": "complete", "samples": rows, "results": str(source),
              "relative_l2_valid_samples": len(valid),
              "mean_relative_l2": sum(valid) / len(valid) if valid else None,
              "mean_time_relative_l2": sum(r["mean_time_relative_l2"] for r in rows) / len(rows)}
    output = session.output_dir("post") / "metrics.json"
    save_json(output, report)
    session.record_asset("metrics", output, kind="other", stage="post", dependencies=[source])
    for name in ("mean_relative_l2", "mean_time_relative_l2"):
        if report[name] is not None:
            session.record_metric(name, report[name], stage="post", assets=[source.parent],
                semantics={"field": "u", "unit": "1", "split": "test", "statistic": name,
                           "data_identity": manifest["dataset_identity"]})
    session.report(report, stage="post")
    return report
