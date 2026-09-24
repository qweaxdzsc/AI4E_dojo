"""外流推理的管理适配：候选科学身份、执行参数和已交付进度。"""

import json
from pathlib import Path


def checkpoint_candidates(run: dict) -> list[str]:
    """外流权重格式及目录由应用解释，返回成员供管理层核验。"""
    if "train" not in run.get("stages", []):
        return []
    return [
        str(p)
        for p in sorted((Path(run["run_dir"]) / "checkpoints").glob("*.pt"))
        if p.is_file() and not p.is_symlink()
    ]


def describe_checkpoint(path: str, run: dict) -> dict:
    """读取检查点和关联准备；只交付显示元数据与带作用域的等值身份。"""
    from ai4e_core.applications.aero_cfd.infer import inspect_checkpoint

    metadata = inspect_checkpoint(path)
    own = Path(run["run_dir"]) / "artifacts/preparation.json"
    reference = (
        metadata.get("effective_config", {}).get("inputs", {}).get("train", {}).get("preparation")
    )
    preparation = own if own.is_file() else Path(reference) if reference else None
    reason, prep = None, {}
    try:
        prep = json.loads(preparation.read_text()) if preparation else {}
        if not isinstance(prep, dict) or not prep.get("digest"):
            reason, prep = "准备记录缺少内容摘要", {}
    except (ValueError, OSError):
        reason, preparation = "准备记录缺失或格式无效", None
    contract = metadata.get("contract") or {}
    if contract.get("preparation") and prep.get("digest") != contract["preparation"]:
        reason = "检查点与准备记录摘要不一致"
    return {
        "epoch": metadata.get("epoch"),
        "updates": metadata.get("updates"),
        "evaluation": metadata.get("evaluation"),
        "contract": contract,
        "preparation": {"path": str(preparation), "digest": prep.get("digest")}
        if preparation
        else None,
        "compatibility": {"status": "invalid" if reason else "compatible", "reason": reason},
        "execution_identity": {
            "scope": "aero.inference.v1",
            "value": {
                "preparation": prep.get("digest"),
                "component": contract.get("component"),
                "model": contract.get("model"),
            },
        },
    }


def plan_execution(request: dict) -> list[dict]:
    """按所选权重与切片装配已有运行器参数，不返回命令或调度逻辑。"""
    selection = request["request"]
    groups = request.get("groups") or [
        {"split": selection.get("split", "test"), "samples": selection.get("samples", [])}
    ]
    work = request.get("retry_children") or [
        {"checkpoint_id": cp["id"], **group} for cp in request["checkpoints"] for group in groups
    ]
    result = []
    for index, unit in enumerate(work):
        cp = next(c for c in request["checkpoints"] if c["id"] == unit["checkpoint_id"])
        params = {
            **selection["options"],
            "samples": unit["samples"],
            "split": unit["split"],
            **{key: selection[key] for key in ("fields", "metrics") if key in selection},
        }
        bindings = {
            "inputs.infer.preparation": cp["preparation"]["path"],
            "inputs.infer.checkpoint": cp.get("fixed", {}).get("path", cp["path"]),
        }
        overrides = ["pipeline.stages=[infer]"]
        overrides.extend("infer." + key + "=" + json.dumps(value) for key, value in params.items())
        overrides.extend(key + "=" + json.dumps(value) for key, value in bindings.items())
        overrides.append("infer.device=" + json.dumps(selection["device"]))
        result.append(
            {
                **unit,
                "id": str(index),
                "stages": ["infer"],
                "overrides": overrides,
                "input_keys": list(bindings),
            }
        )
    return result


def read_progress(run: dict) -> dict:
    """解释外流 writer 账本；无交付证据时保留未知完成数。"""
    root = Path(run["run_dir"]) / "artifacts"
    for name in ("inference-progress.json", "infer-progress.json", "post-progress.json"):
        path = root / name
        if not path.is_file():
            continue
        progress = json.loads(path.read_text())
        if "completed" not in progress:
            operations = progress.get("operations", {})
            record = next(
                (
                    operations[key]
                    for key in ("save", "evaluation", "predictions", "prediction")
                    if key in operations and operations[key].get("status") != "skipped"
                ),
                {},
            )
            progress["completed"] = record.get("completed")
        return progress
    return {"completed": None}
