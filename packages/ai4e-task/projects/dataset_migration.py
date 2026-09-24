"""历史正式物理数据迁移：复制完整产物并仅修正新副本中的消费路径。"""

from pathlib import Path
from uuid import uuid4

from ..storage.database import transaction
from ..storage.files import read_json, write_json
from ..storage.processed_datasets import manifest_digest
from ..storage.shared_datasets import begin, directory, finish, read_dataset, reserve


def migrate_shared_datasets(
    project: str | Path,
    *,
    context: dict,
    dry_run: bool = True,
    overwrite: bool = False,
    sources: dict[str, str] | None = None,
) -> list[dict]:
    """预览或复制历史物理产物，返回逐项迁移结果，原文件保持不变。

    sources 可显式指定 {共享名称: 正式运行ID}，用于旧登记名与冻结配置名不同的情形。
    未提供时按配置名称选择最新正式成功运行；空映射不迁移任何内容。
    指定来源非正式成功物理运行时抛 ValueError，同名冲突抛 FileExistsError。
    """
    from ..tasks.records import list_runs

    project = Path(project).resolve()
    from ..storage.asset_transfer import copy_declared_dataset
    from ..tasks.operation_sources import invoke_source, with_operation

    context = {**context, "source": with_operation(context["source"], "inspect")}
    runs = {
        run["id"]: run
        for run in list_runs(project)
        if run["status"] == "succeeded" and run.get("operation_mode", "execute") == "execute"
    }
    choices = invoke_source(
        context["source"],
        context["recipe"],
        {"operation": "migration_candidates", "runs": list(runs.values())},
    )
    eligible, candidates = {}, {}
    for choice in choices:
        run = runs[choice["run_id"]]
        manifest = Path(choice["manifest"]).resolve()
        if not manifest.is_relative_to(Path(run["data_dir"]).resolve()):
            raise ValueError("migration_member_escape")
        eligible[run["id"]] = (run, manifest, choice)
        if choice.get("name"):
            if choice["name"] in candidates and sources is None:
                raise ValueError("migration_sources_required_for_multiple_candidates")
            candidates[choice["name"]] = eligible[run["id"]]
    if sources is not None:
        candidates = {}
        for name, run_id in sources.items():
            directory(project, name)
            if run_id not in eligible:
                raise ValueError(f"shared_migration_source_not_eligible: {run_id}")
            candidates[name] = eligible[run_id]
    result = []
    for name, (run, manifest, choice) in candidates.items():
        target = directory(project, name) / "content"
        source_digest = manifest_digest(manifest)
        item = {
            "name": name,
            "source_manifest": str(manifest),
            "target": str(target),
            "run_id": run["id"],
            "source_digest": source_digest,
            "samples": choice["samples"],
            "status": "planned",
        }
        if (target.parent / "asset.json").is_file():
            existing = read_dataset(project, name)
            if (
                existing["status"] == "available"
                and existing.get("migration", {}).get("source_digest") == source_digest
            ):
                from ..tasks.assets import validate_asset

                validate_asset(project, existing)
                result.append({**item, "status": "already_migrated"})
                continue
            if not overwrite:
                raise FileExistsError(f"shared_dataset_exists: {name}")
        if not dry_run:
            build_id = "migration-" + uuid4().hex
            plan = {
                "name": name,
                "path": str(target.relative_to(project)),
                "manifest": "manifest.json",
                "consumer_binding": choice["consumer_binding"],
                "stage": choice["stage"],
                "application_context": context,
                "overwrite": overwrite,
            }
            with transaction(project) as db:
                reserve(db, project, [plan], build_id)
            run_context = {
                "project_id": read_json(project / "project.json")["id"],
                "task_id": run["task_id"],
                "version_id": run["version_id"],
                "run_id": build_id,
            }
            try:
                begin(project, [plan], run_context)
                item.update(copy_declared_dataset(manifest, target, context=context))
                finish(project, [plan], build_id, succeeded=True)
                from ..storage.records import put

                record = read_json(target.parent / "asset.json")
                record["migration"] = {
                    "source_digest": source_digest,
                    "source_manifest": str(manifest),
                    "run_id": run["id"],
                }
                with transaction(project) as db:
                    write_json(target.parent / "asset.json", record)
                    put(db, "asset", record, replace=True)
                item["status"] = "migrated"
            except BaseException:
                finish(project, [plan], build_id, succeeded=False)
                raise
        result.append(item)
    return result
