"""new/fork：完整文件快照与数据库记录在一个发布流程中提交。"""

import getpass
import shutil
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from ..projects.project import open_project
from ..storage.database import transaction
from ..storage.files import write_json
from ..storage.layout import task_dir
from ..storage.records import all_records, fetch, get, put, remember, replay
from ..storage.snapshots import digest, inventory, snapshot
from ..templates.materialize import materialize, read_entry
from ..versions.records import record_version
from .assets import asset_path, capture_inputs, collect_run_assets, copy_assets


def new_task(
    project, name: str, *, source: str | Path | None = None, idempotency_key: str | None = None
) -> dict:
    """从模板、目录或空目录创建新的根版本。"""
    if source is not None:
        path = Path(source).expanduser()
        if not path.is_dir():
            source = fetch(project, "template", str(source))["source"]
        source = Path(source).resolve()
    return _create(project, name, source=source, key=idempotency_key)


def fork_task(
    project: str | Path,
    task_id: str,
    *,
    name: str | None = None,
    source: str = "worktree",
    run_id: str | None = None,
    baseline_version_id: str | None = None,
    copy_datasets: bool = False,
    copy_preparation: bool = False,
    copy_checkpoints: bool = False,
    idempotency_key: str | None = None,
) -> dict:
    """从当前代码、创建快照或固定运行派生；三种资产复制默认关闭。"""
    parent = fetch(project, "task", task_id)
    folder = task_dir(project, task_id)
    if source == "worktree":
        path = folder / "recipe"
    elif source == "version":
        path = folder / ".dojo/snapshots/creation"
        original = fetch(project, "version", parent["version_id"])
        if digest(inventory(path)) != original["snapshot"]["digest"]:
            raise ValueError("version_snapshot_changed")
    elif source == "run":
        if not run_id:
            raise ValueError("run_id_required")
        run = fetch(project, "run", run_id)
        if run["task_id"] != task_id:
            raise ValueError("run_task_mismatch")
        path = Path(project) / run["code_path"]
        if digest(inventory(path)) != run.get("code_digest"):
            raise ValueError("run_snapshot_changed")
    else:
        raise ValueError("invalid_fork_source")
    kinds = {
        kind
        for kind, selected in [
            ("dataset", copy_datasets),
            ("preparation", copy_preparation),
            ("checkpoint", copy_checkpoints),
        ]
        if selected
    }
    if kinds:
        from .query import list_runs

        list_runs(project, task_id)
    return _create(
        project,
        name or f"{parent['name']}-fork",
        source=path,
        parent=parent,
        baseline=baseline_version_id or parent["version_id"],
        kinds=kinds,
        key=idempotency_key,
        source_kind=source,
        source_run=run_id,
    )


def _create(
    project,
    name,
    *,
    source=None,
    parent=None,
    baseline=None,
    kinds=None,
    key=None,
    source_kind="template",
    source_run=None,
):
    info = open_project(project)
    project = Path(project).resolve()
    fingerprint = digest(
        {
            "op": "fork" if parent else "new",
            "name": name,
            "source": str(source),
            "parent": parent and parent["id"],
            "baseline": baseline,
            "kinds": sorted(kinds or []),
            "source_run": source_run,
        }
    )
    identity, version_id = uuid4().hex, uuid4().hex
    final = task_dir(project, identity)
    stage = project / ".dojo" / f"task-{identity}.tmp"
    published = False
    try:
        with transaction(project) as db:
            previous = replay(db, key, fingerprint)
            if previous is not None:
                return previous
            stage.mkdir()
            for folder in ("assets", "data", "runs", ".dojo/snapshots", ".dojo/executions"):
                (stage / folder).mkdir(parents=True, exist_ok=True)
            if source is not None:
                source = Path(source)
                source_snapshot = snapshot(source, stage / ".dojo/snapshots/source")
            else:
                source_snapshot = {}
            materialize(source, stage / "recipe")
            entry = read_entry(stage / "recipe")
            inputs = capture_inputs(
                stage / "recipe",
                entry,
                project=project,
                inherited=(parent or {}).get("assets", {}),
                shared=all_records(db, "asset"),
            )
            assets = copy_assets(project, inputs, stage, final, kinds or set())
            copied_outputs = {}
            if parent and kinds:
                candidates = [
                    r
                    for r in all_records(db, "run")
                    if r["task_id"] == parent["id"]
                    and r["status"] == "succeeded"
                    and r.get("code_path")
                ]
                if source_run:
                    candidates = [r for r in candidates if r["id"] == source_run]
                if candidates:
                    produced = collect_run_assets(project, candidates[-1], kinds)
                    copied_outputs = copy_assets(project, produced, stage, final, kinds)
            if entry:
                from omegaconf import OmegaConf

                cfg = OmegaConf.load(stage / "recipe" / entry["config"])
                for field, asset in assets.items():
                    OmegaConf.update(cfg, field, str(asset_path(project, asset)))
                OmegaConf.save(cfg, stage / "recipe" / entry["config"])
            creation = snapshot(stage / "recipe", stage / ".dojo/snapshots/creation")
            now = datetime.now(UTC).isoformat()
            value = {
                "id": identity,
                "project_id": info["id"],
                "version_id": version_id,
                "name": name,
                "created_at": now,
                "created_by": getpass.getuser(),
                "entry": entry,
                "assets": assets,
                "copied_outputs": copied_outputs,
                "parent_version_id": parent and parent["version_id"],
                "baseline_version_id": baseline,
            }
            version = {
                "id": version_id,
                "task_id": identity,
                "created_at": now,
                "parent_version_id": value["parent_version_id"],
                "baseline_version_id": baseline,
                "snapshot": creation,
                "source_snapshot": source_snapshot,
                "source": {"kind": source_kind, "path": str(source), "run_id": source_run},
                "assets": assets,
                "copied_outputs": copied_outputs,
            }
            before = fetch_parent = {}
            if parent:
                fetch_parent = get(db, "version", parent["version_id"])
                before = fetch_parent["snapshot"]["files"]
            after = creation["files"]
            version["changes"] = [
                {"path": name, "before": before.get(name), "after": after.get(name)}
                for name in sorted(before.keys() | after.keys())
                if before.get(name) != after.get(name)
            ]
            write_json(stage / "task.json", value)
            write_json(stage / ".dojo/snapshots/version.json", version)
            record_version(db, version)
            put(db, "task", value)
            remember(db, key, fingerprint, "task", identity)
            stage.rename(final)
            published = True
    except BaseException:
        if published:
            shutil.rmtree(final)
        raise
    finally:
        shutil.rmtree(stage, ignore_errors=True)
    return value
