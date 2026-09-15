"""结构跟踪只读解析最近可用物理来源，不回写任务配置。"""

import json
from copy import deepcopy
from pathlib import Path

import ai4e_task as task

from ...infrastructure.content_access import roots


def latest_trace_source(service, project: str, identity: str) -> dict:
    """优先最近一次与当前模型相容的准备，否则最近一次正式清单。"""
    base = service.project(project)
    visible = {name: path.resolve() for name, path in roots(service, project, identity).items()}
    visible.setdefault("project", Path(base).resolve())
    runs = {item["id"]: item for item in task.list_runs(base, identity)}
    artifacts = [
        item
        for item in task.list_stage_artifacts(base, identity, visible)
        if item["binding"] in {"train.manifest", "train.preparation"}
    ]

    def recency(item):
        return runs.get(item.get("run_id") or "", {}).get("created_at") or ""

    def resolve(item):
        root = visible.get(item.get("root", "project"), Path(base).resolve())
        return (root / item["path"]).resolve()

    captured = task.read_configuration(base, identity)
    for item in sorted(
        (value for value in artifacts if value["binding"] == "train.preparation"),
        key=recency,
        reverse=True,
    ):
        path = resolve(item)
        if path.is_file() and _preparation_compatible(path, captured["config"]):
            return {"train.preparation": str(path)}
    for item in sorted(
        (value for value in artifacts if value["binding"] == "train.manifest"),
        key=recency,
        reverse=True,
    ):
        path = resolve(item)
        if path.is_file():
            return {"train.manifest": str(path)}
    raise ValueError("请先完成原始处理后再生成真实模型结构")


def _preparation_compatible(path: Path, config: dict) -> bool:
    """对照冻结声明，不相容的旧准备不能用于当前模型结构。"""
    try:
        record = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return False
    declarations = record.get("declarations") or {}
    current = {
        key: deepcopy(config.get(key))
        for key in ("model", "trainprep", "sampling", "normalization")
    }
    current["component"] = (config.get("components") or {}).get("model")
    if declarations.get("component") and declarations.get("component") != current["component"]:
        return False
    if declarations.get("model") and declarations["model"] != current["model"]:
        return False
    return True
