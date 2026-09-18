"""一次性清理正式工作区：只留首页任务，迁移平台共享数据，删除旧准备。"""

from __future__ import annotations

import json
import shutil
import sqlite3
from pathlib import Path
from uuid import uuid4

import ai4e_task as task
from ai4e_task.projects.dataset_migration import copy_physical_dataset
from ai4e_task.storage.database import transaction
from ai4e_task.storage.files import read_json, write_json
from ai4e_task.storage.records import all_records, get, put
from ai4e_task.storage.shared_datasets import begin, directory, finish, reserve

ROOT = Path("/Users/zonghui/work/project_simulation/dojo_train/platform")
KEEP_PROJECT_ID = "7142b2dc062e4808a1686795076b8028"
KEEP_TASK_ID = "9c1dac251856411d9091d8d1cc60bc3e"
KEEP_PROJECT = ROOT / "projects" / "f644f908bfde4eb4a5bea65ad97e457a"
ABC_PROJECT = ROOT / "projects" / "4753032f34914c339c311ea02cd4bcb5"
ABC_ID = "34f74688805f4d4e815885da04a081d2"
REAL_CFD_ID = "cfaa5a5281524be2a0200e41f657dd63"
NEW_BINDING = "inputs.trainprep.dataset"


def _copy_shared(name: str, source_manifest: Path, *, overwrite: bool) -> dict:
    keep = task.get_task(KEEP_PROJECT, KEEP_TASK_ID)
    build_id = "migration-" + uuid4().hex
    plan = {
        "name": name,
        "path": f"shared/datasets/{name}/content",
        "manifest": "manifest.json",
        "consumer_binding": NEW_BINDING,
        "overwrite": overwrite,
    }
    with transaction(KEEP_PROJECT) as db:
        reserve(db, KEEP_PROJECT, [plan], build_id)
    context = {
        "project_id": KEEP_PROJECT_ID,
        "task_id": KEEP_TASK_ID,
        "version_id": keep["version_id"],
        "run_id": build_id,
    }
    begin(KEEP_PROJECT, [plan], context)
    copied = copy_physical_dataset(source_manifest, directory(KEEP_PROJECT, name) / "content")
    finish(KEEP_PROJECT, [plan], build_id, succeeded=True)
    record = read_json(directory(KEEP_PROJECT, name) / "asset.json")
    record["migration"] = {
        "source_manifest": str(source_manifest),
        "source_digest": task.manifest_digest(source_manifest),
        "copied_samples": copied["samples"],
    }
    with transaction(KEEP_PROJECT) as db:
        write_json(directory(KEEP_PROJECT, name) / "asset.json", record)
        put(db, "asset", record, replace=True)
    return {"name": name, "status": "copied", "samples": copied["samples"]}


def _update_binding(name: str) -> dict:
    folder = directory(KEEP_PROJECT, name)
    record = read_json(folder / "asset.json")
    record["consumer_binding"] = NEW_BINDING
    with transaction(KEEP_PROJECT) as db:
        write_json(folder / "asset.json", record)
        put(db, "asset", record, replace=True)
    return {"name": name, "status": "binding_updated"}


def _delete_record(db, kind: str, identity: str) -> None:
    db.execute("DELETE FROM records WHERE kind=? AND id=?", (kind, identity))


def main() -> dict:
    report: dict = {"copied": [], "updated": [], "deleted_tasks": [], "deleted_preps": []}
    for item in task.list_shared_datasets(ABC_PROJECT):
        if item.get("status") != "available":
            continue
        existing = directory(KEEP_PROJECT, item["name"])
        overwrite = existing.exists() and any(existing.iterdir())
        report["copied"].append(
            _copy_shared(item["name"], Path(item["manifest_path"]), overwrite=overwrite)
        )
    car4 = directory(KEEP_PROJECT, "shapenet_car4") / "asset.json"
    if car4.is_file():
        record = read_json(car4)
        if record.get("status") == "available" and record.get("consumer_binding") != NEW_BINDING:
            report["updated"].append(_update_binding("shapenet_car4"))

    keep = task.get_task(KEEP_PROJECT, KEEP_TASK_ID)
    current = task.read_configuration(KEEP_PROJECT, KEEP_TASK_ID)
    config = current["config"]
    inputs = config.setdefault("inputs", {})
    for stage, key in (("train", "preparation"), ("infer", "preparation"), ("trainprep", "dataset")):
        section = inputs.setdefault(stage, {})
        if isinstance(section, dict):
            section.pop(key, None)
    train = config.get("train")
    if isinstance(train, dict):
        train.pop("preparation", None)
        train.pop("manifest", None)
    task.replace_configuration(KEEP_PROJECT, KEEP_TASK_ID, config, revision=current["revision"])

    keep_runs = KEEP_PROJECT / "tasks" / KEEP_TASK_ID / "runs"
    prep_ids = []
    if keep_runs.is_dir():
        for folder in keep_runs.iterdir():
            if (folder / "artifacts" / "preparation.json").is_file():
                prep_ids.append(folder.name)
                shutil.rmtree(folder)
    with transaction(KEEP_PROJECT) as db:
        for run in all_records(db, "run"):
            if run.get("task_id") != KEEP_TASK_ID:
                continue
            run_id = run["id"]
            if run_id in prep_ids or Path(run.get("run_dir") or "").name in prep_ids:
                _delete_record(db, "run", run_id)
                if run_id not in prep_ids:
                    prep_ids.append(run_id)
    report["deleted_preps"] = prep_ids

    extra_tasks = []
    extra_versions = []
    extra_runs = []
    with transaction(KEEP_PROJECT) as db:
        for item in all_records(db, "task"):
            if item["id"] != KEEP_TASK_ID:
                extra_tasks.append(item)
                _delete_record(db, "task", item["id"])
        for item in all_records(db, "version"):
            if item.get("task_id") and item["task_id"] != KEEP_TASK_ID:
                extra_versions.append(item["id"])
                _delete_record(db, "version", item["id"])
        for item in all_records(db, "run"):
            if item.get("task_id") and item["task_id"] != KEEP_TASK_ID:
                extra_runs.append(item["id"])
                _delete_record(db, "run", item["id"])
    for item in extra_tasks:
        folder = KEEP_PROJECT / "tasks" / item["id"]
        if folder.is_dir():
            shutil.rmtree(folder)
        report["deleted_tasks"].append(item["id"])
    report["deleted_versions"] = extra_versions
    report["deleted_extra_runs"] = extra_runs

    if ABC_PROJECT.is_dir():
        shutil.rmtree(ABC_PROJECT)
        report["deleted_abc_project"] = True
    server = sqlite3.connect(ROOT / "server.sqlite")
    try:
        server.execute(
            "DELETE FROM documents WHERE kind=? AND id IN (?,?)",
            ("project", ABC_ID, REAL_CFD_ID),
        )
        server.commit()
    finally:
        server.close()
    report["unregistered_projects"] = [ABC_ID, REAL_CFD_ID]

    datasets = ROOT / "datasets"
    if datasets.is_dir():
        removed = []
        for child in datasets.iterdir():
            if child.name.startswith("."):
                continue
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()
            removed.append(child.name)
        report["cleared_workspace_registry"] = removed

    report["kept"] = {
        "project_id": KEEP_PROJECT_ID,
        "task_id": KEEP_TASK_ID,
        "task_name": keep["name"],
        "remaining_tasks": [item["id"] for item in task.list_tasks(KEEP_PROJECT)],
    }
    report["shared_after"] = [
        {
            "name": item.get("name"),
            "status": item.get("status"),
            "binding": item.get("consumer_binding"),
        }
        for item in task.list_shared_datasets(KEEP_PROJECT)
    ]
    return report


if __name__ == "__main__":
    print(json.dumps(main(), ensure_ascii=False, indent=2))
