"""列出并解析工作区已处理数据集，不扫描 contrib 源目录。"""

from pathlib import Path

import ai4e_task as task

from ...infrastructure.content_access import roots
from ..visualization import register


def _workspace(service):
    return Path(service.settings.root).resolve()


def harvest(service) -> list[dict]:
    """把已成功的正式原始处理补登记到工作区目录。"""
    root = _workspace(service)
    projects = root / "projects"
    if not projects.is_dir():
        return list_public(service)
    for folder in sorted(projects.iterdir()):
        if not folder.is_dir():
            continue
        try:
            tasks = task.list_tasks(folder)
        except (ValueError, FileNotFoundError, KeyError):
            continue
        for item in tasks:
            try:
                runs = task.list_runs(folder, item["id"])
                config = task.read_configuration(folder, item["id"])["config"]
            except (ValueError, FileNotFoundError, KeyError):
                continue
            for run in runs:
                try:
                    task.publish_processed_from_run(
                        root, folder, item["id"], run, config=config
                    )
                except ValueError:
                    continue
    return list_public(service)


def list_public(service) -> list[dict]:
    """返回跨项目可见的平台数据集，不含本机绝对路径。"""
    result = []
    for item in task.list_processed_datasets(_workspace(service)):
        result.append(
            {
                "name": item["name"],
                "status": item["status"],
                "reason": item.get("reason"),
                "digest": item.get("digest"),
                "created_at": item.get("created_at"),
                "origin_task": (item.get("provenance") or {}).get("task_id"),
                "origin_run": (item.get("provenance") or {}).get("run_id"),
            }
        )
    return result


def as_stage_inputs(service, project: str, identity: str) -> list[dict]:
    """把可用平台数据集转成训练清单候选项。"""
    visible = {name: path.resolve() for name, path in roots(service, project, identity).items()}
    result = []
    for item in task.list_processed_datasets(_workspace(service)):
        path = Path(item["manifest_path"])
        if item["status"] != "available" or not path.is_file():
            result.append(
                {
                    "binding": "train.manifest",
                    "run_id": (item.get("provenance") or {}).get("run_id"),
                    "name": item["name"],
                    "selected": False,
                    "origin": "platform",
                    "processed_name": item["name"],
                    "created_at": item.get("created_at"),
                    "ref": None,
                    "compatibility": {
                        "status": "invalid",
                        "reason": item.get("reason") or "binding_source_unavailable",
                    },
                }
            )
            continue
        match = next(
            ((name, root) for name, root in visible.items() if path.is_relative_to(root)),
            None,
        )
        if not match:
            result.append(
                {
                    "binding": "train.manifest",
                    "run_id": (item.get("provenance") or {}).get("run_id"),
                    "name": item["name"],
                    "selected": False,
                    "origin": "platform",
                    "processed_name": item["name"],
                    "created_at": item.get("created_at"),
                    "ref": None,
                    "compatibility": {"status": "invalid", "reason": "path_outside_root"},
                }
            )
            continue
        root_id, root = match
        result.append(
            {
                "binding": "train.manifest",
                "run_id": (item.get("provenance") or {}).get("run_id"),
                "name": item["name"],
                "selected": False,
                "origin": "platform",
                "processed_name": item["name"],
                "created_at": item.get("created_at"),
                "compatibility": {"status": "unchecked", "reason": "requires_configuration_check"},
                "ref": register(
                    service, project, root_id, str(path.relative_to(root)), identity
                ),
            }
        )
    return result


def check_name(service, name: str, config: dict) -> dict:
    """执行前核验平台数据集名称。"""
    return task.check_processed_name(
        _workspace(service), name, claim=task.processed_claim(config)
    )


def publish_run(service, project: str, identity: str, run: dict) -> dict | None:
    """运行成功后按任务配置登记。"""
    config = task.read_configuration(service.project(project), identity)["config"]
    try:
        return task.publish_processed_from_run(
            _workspace(service), service.project(project), identity, run, config=config
        )
    except ValueError:
        return None
