"""历史正式物理数据迁移：复制完整产物并仅修正新副本中的消费路径。"""

from pathlib import Path
from uuid import uuid4

from ..storage.database import transaction
from ..storage.files import copy_content, read_json, write_json
from ..storage.processed_datasets import manifest_digest
from ..storage.shared_datasets import begin, directory, finish, read_dataset, reserve
from ..storage.snapshots import digest, inventory


def copy_physical_dataset(manifest: Path, target: Path) -> dict:
    """复制物理文件、身份与统计依赖；逐字节校验，不解码张量或重算数值。"""
    source = manifest.parent.resolve()
    original = read_json(manifest)
    # 来源目录只包括原始处理产物；运行记录在兄弟目录中，不复制。
    target.mkdir(parents=True, exist_ok=True)
    for child in source.iterdir():
        if child.name.startswith(".") or child.name == "manifest.json":
            continue
        copy_content(child, target / child.name)
        if digest(inventory(child)) != digest(inventory(target / child.name)):
            raise ValueError("shared_dataset_copy_changed")
    for sample in original["samples"]:
        old = Path(sample["path"])
        old = old.resolve() if old.is_absolute() else (source / old).resolve()
        if not old.is_relative_to(source):
            raise ValueError("shared_dataset_member_escape")
        sample["path"] = str(old.relative_to(source))
    copied_dependencies = []
    stats = original.get("statistics")
    if isinstance(stats, dict) and stats.get("path"):
        old = Path(stats["path"])
        old = old.resolve() if old.is_absolute() else (source / old).resolve()
        if old.is_relative_to(source):
            stats["path"] = str(old.relative_to(source))
        else:
            relative = "dependencies/statistics" + old.suffix
            copy_content(old, target / relative)
            if digest(inventory(old)) != digest(inventory(target / relative)):
                raise ValueError("shared_statistics_copy_changed")
            stats["path"] = relative
            copied_dependencies.append(str(old))
    source_manifest = original.get("source_manifest")
    if source_manifest and Path(source_manifest).is_file():
        relative = "dependencies/source-manifest" + Path(source_manifest).suffix
        copy_content(source_manifest, target / relative)
        original["source_manifest"] = relative
    write_json(target / "manifest.json", original)
    return {"samples": len(original["samples"]), "copied_dependencies": copied_dependencies}


def migrate_shared_datasets(
    project: str | Path,
    *,
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
    candidates = {}
    eligible = {}
    for run in list_runs(project):
        if run["status"] != "succeeded" or run.get("operation_mode", "execute") != "execute":
            continue
        if "rawprep" not in run.get("stages", []) or run.get("shared_outputs"):
            continue
        manifest = Path(run["data_dir"]) / "manifest.json"
        config = Path(run["run_dir"]) / "inputs/config.yaml"
        if not manifest.is_file() or not config.is_file():
            continue
        eligible[run["id"]] = (run, manifest)
        from omegaconf import OmegaConf

        cfg = OmegaConf.load(config)
        name = OmegaConf.select(cfg, "dataset.processed_name")
        if name:
            candidates[name] = (run, manifest)
    if sources is not None:
        candidates = {}
        for name, run_id in sources.items():
            directory(project, name)
            if run_id not in eligible:
                raise ValueError(f"shared_migration_source_not_eligible: {run_id}")
            candidates[name] = eligible[run_id]
    result = []
    for name, (run, manifest) in candidates.items():
        target = directory(project, name) / "content"
        source_digest = manifest_digest(manifest)
        item = {
            "name": name,
            "source_manifest": str(manifest),
            "target": str(target),
            "run_id": run["id"],
            "source_digest": source_digest,
            "samples": len(read_json(manifest).get("samples", [])),
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
                "consumer_binding": "inputs.trainprep.dataset",
                "overwrite": overwrite,
            }
            with transaction(project) as db:
                reserve(db, project, [plan], build_id)
            context = {
                "project_id": read_json(project / "project.json")["id"],
                "task_id": run["task_id"],
                "version_id": run["version_id"],
                "run_id": build_id,
            }
            try:
                begin(project, [plan], context)
                item.update(copy_physical_dataset(manifest, target))
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
