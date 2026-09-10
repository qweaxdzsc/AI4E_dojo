"""固定引用的配置、文本和指标比较；不重新计算物理指标。"""

import difflib
import math
from pathlib import Path
from uuid import uuid4

from ..storage.database import transaction
from ..storage.files import read_json
from ..storage.layout import task_dir
from ..storage.records import fetch, put
from ..storage.snapshots import digest, inventory


def _diff(left: Path, right: Path) -> dict:
    a, b = inventory(left), inventory(right)
    changes = []
    for name in sorted(a.keys() | b.keys()):
        if a.get(name) == b.get(name):
            continue
        change = {
            "path": name,
            "status": "added" if name not in a else "removed" if name not in b else "modified",
            "before": a.get(name),
            "after": b.get(name),
        }
        try:
            first = (left / name).read_text().splitlines() if name in a else []
            second = (right / name).read_text().splitlines() if name in b else []
            change["diff"] = "\n".join(
                difflib.unified_diff(
                    first, second, fromfile="before/" + name, tofile="after/" + name, lineterm=""
                )
            )
        except UnicodeDecodeError:
            change["binary"] = True
        changes.append(change)
    return {"files": changes}


def _save(project: str | Path, value: dict, save: bool) -> dict:
    if save:
        value = {"id": uuid4().hex, **value}
        with transaction(project) as db:
            put(db, "comparison", value)
    return value


def compare_versions(project: str | Path, left: str, right: str, *, save: bool = False) -> dict:
    """比较两个正式版本的创建记录，默认不持久化查询。"""
    a, b = fetch(project, "version", left), fetch(project, "version", right)
    for record in (a, b):
        folder = task_dir(project, record["task_id"]) / ".dojo/snapshots/creation"
        if digest(inventory(folder)) != record["snapshot"]["digest"]:
            raise ValueError("version_snapshot_changed")
    result = _diff(
        task_dir(project, a["task_id"]) / ".dojo/snapshots/creation",
        task_dir(project, b["task_id"]) / ".dojo/snapshots/creation",
    )
    result.update(
        kind="versions",
        left=left,
        right=right,
        assets={"before": a["assets"], "after": b["assets"]},
        source={"before": a["source"], "after": b["source"]},
    )
    return _save(project, result, save)


def compare_worktree(project: str | Path, task_id: str) -> dict:
    """查询工作目录相对创建记录的变化，不创建正式版本。"""
    task = fetch(project, "task", task_id)
    folder = task_dir(project, task_id)
    return {
        "kind": "worktree",
        "version_id": task["version_id"],
        **_diff(folder / ".dojo/snapshots/creation", folder / "recipe"),
    }


def _select(value, path: list):
    for part in path:
        value = value[int(part)] if isinstance(value, list) else value[part]
    return value


def _metrics(project: str | Path, run: dict) -> dict:
    # 量声明与代码快照绑定，不能使用后来被编辑的工作目录声明。
    if not run.get("code_path"):
        return {}
    entry_file = Path(project) / run["code_path"] / "task-entry.json"
    if not entry_file.exists():
        return {}
    entry = read_json(entry_file)
    from omegaconf import OmegaConf

    config_path = Path(run["run_dir"]) / "inputs/config.yaml"
    config = (
        OmegaConf.to_container(OmegaConf.load(config_path), resolve=True)
        if config_path.exists()
        else {}
    )
    result = {}
    for item in entry.get("metrics", []):
        semantics = dict(item["quantity"])
        semantics["dataset_digests"] = sorted(
            {
                a["digest"]
                for a in run.get("lineage", {}).get("assets", {}).values()
                if a.get("kind") == "dataset"
            }
        )
        for key, selector in item.get("quantity_config", {}).items():
            try:
                semantics[key] = _select(config, selector)
            except (KeyError, IndexError, TypeError):
                semantics[key] = None
        try:
            value = _select(run.get("summary", {}), item["path"])
        except (KeyError, IndexError, TypeError):
            value = None
        valid = (
            isinstance(value, (float, int)) and not isinstance(value, bool) and math.isfinite(value)
        )
        required = {"field", "domain", "unit", "split", "statistic"}
        status = (
            "available"
            if valid
            and required <= semantics.keys()
            and all(semantics.get(k) is not None for k in item.get("quantity_config", {}))
            and all(semantics[k] is not None for k in required)
            else "missing"
        )
        result[item["name"]] = {
            "value": value if valid else None,
            "quantity": semantics,
            "status": status,
        }
    return result


def compare_runs(project: str | Path, left: str, right: str, *, save: bool = False) -> dict:
    """比较固定运行的已有指标；身份与统计定义不匹配时标不可比。"""
    from ..tasks.query import get_run

    a, b = get_run(project, left), get_run(project, right)
    first, second = _metrics(project, a), _metrics(project, b)
    metrics = {}
    for name in first.keys() | second.keys():
        x, y = first.get(name), second.get(name)
        if any(r["status"] in {"pending", "running", "stopping", "unknown"} for r in (a, b)):
            status, reason = "pending", "运行尚未完整结束"
        elif a["status"] != "succeeded" or b["status"] != "succeeded":
            status, reason = "missing", "运行未完整成功"
        elif x is None or y is None or x["status"] != "available" or y["status"] != "available":
            status, reason = "missing", "量、数值或必要语义缺失"
        elif x["quantity"] != y["quantity"]:
            status, reason = "incompatible", "字段、单位、分片或统计定义不同"
        else:
            status, reason = "available", "固定运行的同语义标量"
        metrics[name] = {"status": status, "reason": reason, "left": x, "right": y}
    result = {
        "kind": "runs",
        "left": left,
        "right": right,
        "metrics": metrics,
        "inputs": {
            "left": a.get("lineage", {}).get("assets", {}),
            "right": b.get("lineage", {}).get("assets", {}),
        },
    }
    if a.get("code_path") and b.get("code_path"):
        result.update(_diff(Path(project) / a["code_path"], Path(project) / b["code_path"]))
    return _save(project, result, save)
