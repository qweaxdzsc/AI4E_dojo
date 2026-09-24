"""项目共享物理数据的受控存储、生产占用和发布收据；不加载数值栈。"""

import shutil
from datetime import UTC, datetime
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

from .database import transaction
from .files import read_json, write_json
from .layout import inside
from .processed_datasets import manifest_digest, validate_processed_name
from .records import get, put
from .snapshots import digest, inventory


def directory(project, name: str) -> Path:
    """取得项目内共享数据目录，名称不可作为任意相对路径。"""
    return inside(project, f"shared/datasets/{validate_processed_name(name)}")


def identity(project, name: str) -> str:
    """项目身份与名称共同确定共享身份，不随覆盖改变。"""
    project_id = read_json(Path(project) / "project.json")["id"]
    return uuid5(NAMESPACE_URL, f"{project_id}/datasets/{name}").hex


def read_dataset(project, name: str) -> dict:
    """轻量读取当前登记；浏览只校验清单，不遍历张量。"""
    folder = directory(project, name)
    value = read_json(folder / "asset.json")
    manifest = inside(project, value["path"])
    status, reason = value.get("status", "unavailable"), value.get("reason")
    if status == "available":
        if not manifest.is_file():
            status, reason = "unavailable", "manifest_missing"
        elif manifest_digest(manifest) != value["manifest_digest"]:
            status, reason = "unavailable", "manifest_changed"
    return {**value, "status": status, "reason": reason, "manifest_path": str(manifest)}


def resolve_reference(project, path: Path) -> dict | None:
    """识别显式选中的共享清单；跨项目引用转成绝对路径，不做跨项目发现。"""
    path = path.resolve()
    for parent in path.parents:
        if (
            parent.name != "content"
            or parent.parent.parent.name != "datasets"
            or parent.parent.parent.parent.name != "shared"
        ):
            continue
        source = parent.parent.parent.parent.parent
        if not (source / "project.json").is_file() or not (parent.parent / "asset.json").is_file():
            continue
        record = read_dataset(source, parent.parent.name)
        if Path(record["manifest_path"]) != path:
            return None
        if source == Path(project).resolve():
            return record

        def external(value, source=source):
            return {
                **value,
                "external": True,
                "path": str(inside(source, value["path"])),
                "dependencies": [external(item) for item in value.get("dependencies", [])],
            }

        return {**external(record), "shared_project": str(source)}
    return None


def reserve(db, project, plans: list[dict], run_id: str) -> None:
    """提交事务内占用同名生产权；未知运行不能凭时间自动接管。"""
    for plan in plans:
        name = plan["name"]
        try:
            old = get(db, "shared_build", name)
        except KeyError:
            old = None
        if old and old.get("status") in {"reserved", "building"}:
            try:
                run = get(db, "run", old["run_id"])
            except KeyError:
                run = {}
            if run.get("status") not in {"failed", "stopped", "succeeded"}:
                raise ValueError(f"shared_dataset_busy: {name}")
        folder = directory(project, name)
        if folder.exists() and any(folder.iterdir()) and not plan["overwrite"]:
            raise FileExistsError(f"shared_dataset_exists: {name}; use --overwrite")
        put(db, "shared_build", {"id": name, "run_id": run_id, "status": "reserved"}, replace=True)


def begin(project, plans: list[dict], run: dict) -> None:
    """覆盖前保留本次回退副本；固定目标路径保证领域清单绝对引用有效。"""
    for plan in plans:
        folder = directory(project, plan["name"])
        with transaction(project) as db:
            slot = get(db, "shared_build", plan["name"])
            if slot["run_id"] != run["run_id"] or slot["status"] != "reserved":
                raise ValueError("shared_dataset_reservation_changed")
            if folder.exists() and any(folder.iterdir()) and not plan["overwrite"]:
                raise FileExistsError(f"shared_dataset_exists: {plan['name']}")
            content = inside(project, plan["path"])
            backup = folder / (".rollback-" + run["run_id"])
            if backup.exists():
                raise ValueError("shared_dataset_unresolved_rollback")
            backup.mkdir(parents=True)
            old_record = folder / "asset.json"
            write_json(
                backup / "journal.json",
                {
                    "run_id": run["run_id"],
                    "had_content": content.exists(),
                    "record": read_json(old_record) if old_record.is_file() else None,
                },
            )
            if content.exists():
                content.rename(backup / "content")
            value = {
                "id": identity(project, plan["name"]),
                "kind": "dataset",
                "name": plan["name"],
                "path": str(Path(plan["path"]) / plan["manifest"]),
                "external": False,
                "shared_dataset": True,
                "status": "building",
                "consumer_binding": plan["consumer_binding"],
                "dependencies": [],
                "source": {k: run[k] for k in ("project_id", "task_id", "version_id", "run_id")},
                "created_at": datetime.now(UTC).isoformat(),
            }
            write_json(folder / "asset.json", value)
            put(db, "asset", value, replace=True)
            put(db, "shared_build", {**slot, "status": "building"}, replace=True)
        content.mkdir(parents=True)


def publish(project, plan: dict, run_id: str) -> dict:
    """计算完成后发布共享资产；大文件摘要不持有数据库事务。"""
    folder = directory(project, plan["name"])
    record = read_json(folder / "asset.json")
    if record["source"]["run_id"] != run_id:
        raise ValueError("shared_dataset_owner_changed")
    manifest = inside(project, record["path"])
    from ..storage.records import fetch
    from ..tasks.operation_sources import invoke_source, operation_context

    context = plan.get("application_context")
    if context is None:
        run = fetch(project, "run", run_id)
        context = operation_context(project, run["task_id"], name="inspect", run=run)
    description = invoke_source(
        context["source"],
        context["recipe"],
        {"operation": "validate_dataset", "manifest": str(manifest)},
    )
    for member in description["members"]:
        candidate = Path(member)
        if (
            not candidate.resolve().is_relative_to(manifest.parent.resolve())
            or candidate.is_symlink()
        ):
            raise ValueError("shared_dataset_member_escape")
        if not candidate.exists():
            raise FileNotFoundError(candidate)
    files = inventory(manifest.parent)
    content_digest = digest(
        {
            "manifest": description["identity"],
            "files": {key: value for key, value in files.items() if key != manifest.name},
        }
    )
    record["semantics"] = description["semantics"]
    record["stage"] = plan["stage"]
    record["application_context"] = context
    dependency = {
        "id": record["id"] + "-content",
        "kind": "dataset",
        "external": False,
        "path": plan["path"],
        "digest": digest(files),
        "dependencies": [],
        "source": record["source"],
    }
    record.update(
        status="available",
        digest=digest(inventory(manifest)),
        manifest_digest=manifest_digest(manifest),
        content_digest=content_digest,
        dependencies=[dependency],
        updated_at=datetime.now(UTC).isoformat(),
    )
    with transaction(project) as db:
        slot = get(db, "shared_build", plan["name"])
        if slot["run_id"] != run_id:
            raise ValueError("shared_dataset_owner_changed")
        write_json(folder / "asset.json", record)
        put(db, "asset", record, replace=True)
        put(db, "shared_build", {**slot, "status": "published"}, replace=True)
        try:
            run = get(db, "run", run_id)
        except KeyError:
            run = None
        if run is not None:
            receipts = run.setdefault("shared_publications", {})
            receipts[plan.get("group", "physical_dataset")] = {
                "asset_id": record["id"],
                "name": record["name"],
                "manifest_digest": record["manifest_digest"],
                "content_digest": content_digest,
                "path": record["path"],
            }
            put(db, "run", run, replace=True)
    backup = folder / (".rollback-" + run_id)
    if backup.exists():
        shutil.rmtree(backup)
    return record


def finish(project, plans: list[dict], run_id: str, *, succeeded: bool) -> None:
    """完成或核对生产收据；重复调用不会恢复已被其他运行覆盖的旧数据。"""
    for plan in plans:
        with transaction(project) as db:
            slot = get(db, "shared_build", plan["name"])
        if slot["run_id"] != run_id or slot["status"] in {"published", "failed"}:
            continue
        if succeeded and slot["status"] == "building":
            publish(project, plan, run_id)
            continue
        with transaction(project) as db:
            slot = get(db, "shared_build", plan["name"])
            if slot["run_id"] != run_id:
                continue
            if slot["status"] == "building":
                folder = directory(project, plan["name"])
                path = folder / "asset.json"
                backup = folder / (".rollback-" + run_id)
                journal = read_json(backup / "journal.json") if backup.exists() else None
                value = read_json(path)
                if journal and journal["record"] is not None:
                    content = inside(project, plan["path"])
                    if content.exists():
                        shutil.rmtree(content)
                    if journal["had_content"]:
                        (backup / "content").rename(content)
                    value = journal["record"]
                else:
                    value.update(status="unavailable", reason="build_failed")
                write_json(path, value)
                put(db, "asset", value, replace=True)
                if backup.exists():
                    shutil.rmtree(backup)
            put(db, "shared_build", {**slot, "status": "failed"}, replace=True)
