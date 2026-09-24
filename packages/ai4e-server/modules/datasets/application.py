"""列出并解析工作区已处理数据集，不扫描 contrib 源目录。"""

from pathlib import Path

import ai4e_task as task

from ...infrastructure.content_access import roots
from ..visualization import register


def _workspace(service):
    return Path(service.settings.root).resolve()


def harvest(service) -> list[dict]:
    """把已成功的正式原始处理补登记到工作区目录。"""
    return list_public(service)


def list_public(service) -> list[dict]:
    """返回跨项目可见的平台数据集，不含本机绝对路径。"""
    result = []
    from .registry import synchronize

    for item in synchronize(service):
        result.append(
            {
                "name": item["name"],
                "status": item["status"],
                "reason": item.get("reason"),
                "digest": item.get("digest"),
                "created_at": item.get("created_at"),
                "origin_task": (item.get("provenance") or {}).get("task_id"),
                "origin_run": (item.get("provenance") or {}).get("run_id"),
                "source_project": item.get("source_project"),
                "source_project_name": item.get("source_project_name"),
                "shared_asset_id": item.get("shared_asset_id"),
            }
        )
    return result


def as_stage_inputs(service, project: str, identity: str) -> list[dict]:
    """把可用平台数据集转成训练清单候选项。"""
    visible = {name: path.resolve() for name, path in roots(service, project, identity).items()}
    entry = task.recipe_entry(service.project(project), identity)
    requirements = (entry.get("task_description", {}).get("description") or {}).get("inputs", {})
    result = []
    from .registry import synchronize

    for item in synchronize(service):
        path = Path(item["manifest_path"]).resolve()
        location = next(
            ((name, root) for name, root in visible.items() if path.is_relative_to(root)), None
        )
        available = item["status"] == "available" and path.is_file() and location is not None
        for binding, requirement in requirements.items():
            if requirement["kind"] != "dataset":
                continue
            matched = task.match_asset({"kind": "dataset", **item}, requirement, status="succeeded")
            if matched["conflicts"]:
                continue
            reason = (
                (item.get("reason") or "binding_source_unavailable")
                if not available
                else matched["reason"]
            )
            ref = (
                register(
                    service,
                    project,
                    location[0],
                    str(path.relative_to(location[1])),
                    identity,
                    integrity="stat",
                )
                if available
                else None
            )
            result.append(
                {
                    "binding": binding,
                    "run_id": (item.get("provenance") or {}).get("run_id"),
                    "name": item["name"],
                    "selected": False,
                    "origin": "platform",
                    "source_project": item.get("source_project"),
                    "source_project_name": item.get("source_project_name"),
                    "shared_asset_id": item.get("shared_asset_id"),
                    "processed_name": item["name"],
                    "created_at": item.get("created_at"),
                    "ref": ref,
                    "matching": matched,
                    "compatibility": {
                        "status": "unchecked" if available and matched["matches"] else "invalid",
                        "reason": reason or "requires_configuration_check",
                    },
                }
            )
    return result


def claim_config(config: dict, rawprep: dict | None = None) -> dict:
    """检查与登记共用同一份配置；展开后的 rawprep 覆盖磁盘段。"""
    merged = dict(config or {})
    if rawprep is not None:
        merged["rawprep"] = rawprep
    return merged


def describe_name(service, name: str, config: dict, *, project: str | None = None) -> dict:
    """页面回传名称是否可执行，不抛冲突。"""
    if project is not None:
        return task.describe_shared_name(service.project(project), name)
    return task.describe_processed_name(
        _workspace(service),
        name,
        claim=task.processed_claim(
            config, context=task.configuration_context(config, _workspace(service))
        ),
        context=task.configuration_context(config, _workspace(service)),
    )


def check_name(
    service, name: str, config: dict, *, overwrite: bool = False, project: str | None = None
) -> dict:
    """执行前核验平台数据集名称；覆盖须由提交显式确认。"""
    if project is not None:
        task.validate_processed_name(name)
        result = task.describe_shared_name(service.project(project), name)
        if result["status"] == "conflict" and not overwrite:
            raise FileExistsError("shared_dataset_exists: " + name)
        return result
    return task.check_processed_name(
        _workspace(service),
        name,
        claim=task.processed_claim(
            config, context=task.configuration_context(config, _workspace(service))
        ),
        context=task.configuration_context(config, _workspace(service)),
        overwrite=overwrite,
    )


def publish_run(service, project: str, identity: str, run: dict) -> dict | None:
    """运行成功后按与预检相同的展开配置登记。"""
    from .registry import synchronize

    synchronize(service)
    return None
