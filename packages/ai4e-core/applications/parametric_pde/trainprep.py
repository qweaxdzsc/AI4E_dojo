"""按公开模型组件准备点集与样条资产，冻结数据和组件来源。"""

from pathlib import Path

from ai4e_core.abilities.data.save.bundle import digest, file_digest, save_bundle, save_json
from ai4e_core.base.events import event

from .contracts import preparation_contract


def trainprep(cfg, *, dataset_component, model_component, session):
    """显式执行准备；新目录逐样本提交，失败不发布完整准备清单。"""
    dataset = dataset_component.Dataset(cfg["dataset"]["manifest"])
    root = Path(cfg["trainprep"]["output"])
    if root.exists() and any(root.iterdir()):
        raise FileExistsError(f"准备输出必须为新目录: {root}")
    result = {"contract": preparation_contract(cfg, dataset, model_component), "samples": []}
    if session.dry_run or not cfg["trainprep"]["execute"]:
        session.report(
            {"status": "checked", "samples": len(dataset.manifest["samples"])}, stage="trainprep"
        )
        return None

    def prepare_one(record):
        prepared = model_component.prepare(dataset.read(record), cfg)
        relative = f"{record['split']}/{record['id']}.pt"
        save_bundle(root / relative, prepared)
        event("物理准备", "样本完成", 样本=record["id"])
        return {
            "id": record["id"],
            "split": record["split"],
            "path": relative,
            "sha256": file_digest(root / relative),
        }

    result["samples"] = session.execute_samples(
        dataset.manifest["samples"], prepare_one, stage="trainprep"
    )
    result["content_id"] = digest(result)
    save_json(root / "preparation.json", result)
    report = {
        "path": str(root / "preparation.json"),
        "content_id": result["content_id"],
        "samples": len(result["samples"]),
    }
    session.artifact("preparation.json", report)
    session.report(report, stage="trainprep")
    return report
