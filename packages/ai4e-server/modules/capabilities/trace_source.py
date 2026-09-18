"""结构跟踪只读解析最近可用物理来源，不回写任务配置。"""

import json
from pathlib import Path

import ai4e_task as task

from ...infrastructure.content_access import roots


def latest_trace_source(service, project: str, identity: str) -> dict:
    """优先已选或可导入的现行准备，否则最近一次正式清单。"""
    base = service.project(project)
    visible = {name: path.resolve() for name, path in roots(service, project, identity).items()}
    visible.setdefault("project", Path(base).resolve())
    runs = {item["id"]: item for item in task.list_runs(base, identity)}
    artifacts = [
        item
        for item in task.list_stage_artifacts(base, identity, visible)
        if item["binding"] in {"inputs.trainprep.dataset", "inputs.train.preparation"}
    ]

    def recency(item):
        return runs.get(item.get("run_id") or "", {}).get("created_at") or ""

    def resolve(item):
        root = visible.get(item.get("root", "project"), Path(base).resolve())
        return (root / item["path"]).resolve()

    captured = task.read_configuration(base, identity)
    selected = ((captured["config"].get("inputs") or {}).get("train") or {}).get("preparation")
    if isinstance(selected, str) and selected:
        selected_path = Path(selected).resolve()
        if selected_path.is_file() and _importable_preparation(selected_path):
            return {"inputs.train.preparation": str(selected_path)}
    for item in sorted(
        (value for value in artifacts if value["binding"] == "inputs.train.preparation"),
        key=recency,
        reverse=True,
    ):
        path = resolve(item)
        if path.is_file() and _importable_preparation(path):
            return {"inputs.train.preparation": str(path)}
    declared = (captured["config"].get("inputs", {}).get("trainprep") or {}).get("dataset")
    if declared:
        path = Path(declared).resolve()
        if path.is_file() and any(path.is_relative_to(root) for root in visible.values()):
            return {"inputs.trainprep.dataset": str(path)}
    for item in sorted(
        (value for value in artifacts if value["binding"] == "inputs.trainprep.dataset"),
        key=recency,
        reverse=True,
    ):
        path = resolve(item)
        if path.is_file():
            return {"inputs.trainprep.dataset": str(path)}
    raise ValueError("请先完成原始处理后再生成真实模型结构")


def _importable_preparation(path: Path) -> bool:
    """冻结准备只判断现行记录能否导入，不拿声明去挡当前平台参数。"""
    try:
        record = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return False
    return isinstance(record, dict) and record.get("version") == 2
