"""独立后处理：检查点核验、全网格预测与逐实例指标。"""

from pathlib import Path

import torch

from ai4e_core.abilities.data.save.bundle import file_digest, save_bundle, save_json

from .contracts import open_preparation, read_prepared
from .model import build_model
from .train import training_contract


def post(cfg, *, dataset_component, model_component, session):
    """独立恢复权重，输出所有 test 预测；失败保留部分交付状态。"""
    dataset = dataset_component.Dataset(cfg["dataset"]["manifest"])
    path, prepared = open_preparation(cfg, dataset, model_component)
    checkpoint = (
        Path(cfg["post"]["checkpoint"])
        if cfg["post"]["checkpoint"]
        else (session.run_dir / "checkpoints" / "last.pt")
    )
    root = Path(cfg["post"]["output"])
    if root.exists() and any(root.iterdir()):
        raise FileExistsError(f"预测输出必须为新目录: {root}")
    if session.dry_run:
        session.report({"status": "checked", "checkpoint": str(checkpoint)}, stage="post")
        return None
    state = torch.load(checkpoint, map_location="cpu", weights_only=False)
    if state["contract"] != training_contract(cfg, prepared, model_component):
        raise ValueError("检查点与物理数据、模型或训练协议不一致")
    model = build_model(cfg, model_component)
    model.load_state_dict(state["model"], strict=True)
    model.eval()
    report = {
        "status": "running",
        "checkpoint": str(checkpoint),
        "epoch": state["epoch"],
        "checkpoint_sha256": file_digest(checkpoint),
        "samples": [],
    }
    try:
        with torch.no_grad():
            for record in prepared["samples"]:
                if record["split"] != "test":
                    continue
                batch = read_prepared(path, record)
                prediction = model_component.predictions(model, batch, cfg)["u"].cpu()
                truth = batch["sample"]["u"].to(prediction)
                error = prediction - truth
                norm = float(truth.norm())
                metrics = {
                    "mae": float(error.abs().mean()),
                    "l2": float(error.norm()),
                    "relative_l2": float(error.norm()) / norm if norm else None,
                    "max_error": float(error.abs().max()),
                }
                # 数据契约首轴为时间；与整体时空相对 L2 分开报告，不能互换。
                time_error = error.double().flatten(1).norm(dim=1)
                time_norm = truth.double().flatten(1).norm(dim=1)
                metrics["mean_time_relative_l2"] = float((time_error / (time_norm + 1e-12)).mean())
                save_bundle(
                    root / f"{record['id']}.pt",
                    {
                        "sample_id": record["id"],
                        "axes": batch["sample"]["axes"],
                        "mapping": batch["sample"]["mapping"],
                        "prediction": prediction,
                        "target": truth,
                        "metrics": metrics,
                    },
                )
                report["samples"].append({"id": record["id"], **metrics})
                session.artifact("post-progress.json", report)
    except Exception as exc:
        report.update(status="partial_failure", error=str(exc))
        session.artifact("post-progress.json", report)
        session.report(report, stage="post")
        raise
    if not report["samples"]:
        report.update(status="failed", error="没有测试实例")
        session.artifact("post-progress.json", report)
        raise ValueError(report["error"])
    report["status"] = "complete"
    relative = [r["relative_l2"] for r in report["samples"] if r["relative_l2"] is not None]
    report["relative_l2_valid_samples"] = len(relative)
    report["mean_relative_l2"] = sum(relative) / len(relative) if relative else None
    report["mean_time_relative_l2"] = sum(
        r["mean_time_relative_l2"] for r in report["samples"]
    ) / len(report["samples"])
    report["time_relative_l2_definition"] = (
        "mean_samples(mean_time(norm_spatial(pred-target)/(norm_spatial(target)+1e-12)))"
    )
    save_json(root / "predictions.json", report)
    session.artifact("post-progress.json", report)
    session.report(report, stage="post")
    return report
