"""任务输入资产的登记、核验及按类型复制。"""

from pathlib import Path
from uuid import uuid4

from ..storage.files import copy_content, write_json
from ..storage.layout import inside
from ..storage.snapshots import digest, inventory

KINDS = {"dataset", "preparation", "checkpoint", "model_preset", "other"}


def data_inventory(path: str | Path) -> dict[str, str]:
    """数据允许只读文件链接，内容身份随目标改变；代码快照仍拒绝链接。"""
    from ai4e_core.run.indexes import file_inventory

    path = Path(path)
    if path.is_dir():
        for member in path.rglob("*"):
            if member.is_symlink() and (not member.exists() or member.is_dir()):
                raise ValueError(f"dataset_link_unavailable_or_directory: {member}")
    return file_inventory(path)


def asset_path(project: str | Path, record: dict) -> Path:
    """项目内引用随项目移动，外部引用保持显式绝对路径。"""
    value = record["path"]
    return Path(value) if record.get("external") else inside(project, value)


def validate_asset(project: str | Path, record: dict) -> Path:
    """核对实际内容摘要，缺失或改变时拒绝继续。"""
    if record.get("shared_dataset") and record.get("status") != "available":
        raise ValueError("shared_dataset_unavailable")
    path = asset_path(project, record)
    if digest(data_inventory(path)) != record["digest"]:
        raise ValueError(f"asset_changed: {record['id']}")
    for dependency in record.get("dependencies", []):
        validate_asset(project, dependency)
    if record.get("bundle"):
        root = validate_asset(project, record["bundle"])
        if not path.resolve().is_relative_to(root.resolve()):
            raise ValueError("asset_bundle_members_outside_root")
    return path


def describe_asset(
    path: Path,
    *,
    kind: str,
    source: dict | None = None,
    semantics: dict | None = None,
    stage: str | None = None,
    name: str | None = None,
) -> dict:
    """记录已存在输入，使用流式内容摘要而不加载训练数据。"""
    if kind not in KINDS:
        raise ValueError(f"invalid_asset_kind: {kind}")
    return {
        "id": uuid4().hex,
        "kind": kind,
        "path": str(path.resolve()),
        "external": True,
        "digest": digest(data_inventory(path)),
        "source": source or {},
        "dependencies": [],
        "semantics": semantics or {},
        **({"stage": stage} if stage is not None else {}),
        **({"name": name} if name is not None else {}),
    }


def copy_bundle(project, original: dict, destination: Path, final: Path) -> dict:
    """整体复制发布者声明的相对引用目录；只重定位管理引用，不改科学文件。"""
    source = validate_asset(project, original)
    bundle = original["bundle"]
    root = validate_asset(project, bundle).resolve()
    if not root.is_dir():
        raise ValueError("asset_bundle_directory_required")
    copy_content(root, destination)
    if digest(inventory(destination)) != bundle["digest"]:
        raise ValueError("asset_copy_changed")

    def relocate(record):
        path = asset_path(project, record).resolve()
        if not path.is_relative_to(root):
            raise ValueError("asset_bundle_members_outside_root")
        return {
            **record,
            "external": False,
            "path": str((final / path.relative_to(root)).relative_to(Path(project).resolve())),
            "dependencies": [relocate(dep) for dep in record.get("dependencies", [])],
        }

    value = relocate(original)
    value["bundle"] = relocate(bundle)
    assert source.resolve().is_relative_to(root)
    return value


def indexed_asset(item: dict, *, provenance: dict) -> dict:
    """公共索引转成管理引用，保留依赖闭包与可便携目录声明。"""
    from ai4e_core.run.indexes import validate_asset_content

    validate_asset_content(item)
    record = describe_asset(Path(item["path"]), kind=item["kind"], source=provenance)
    record["dependencies"] = [
        describe_asset(Path(p), kind="other", source=provenance) for p in item["dependencies"]
    ]
    record["semantics"] = item.get("semantics", {})
    record.update(stage=item["stage"], name=item["name"])
    if item.get("bundle"):
        record["bundle"] = describe_asset(
            Path(item["bundle"]["root"]), kind="other", source=provenance
        )
    record["portable"] = bool(record.get("bundle")) or (
        not record["dependencies"] and Path(item["path"]).suffix != ".json"
    )
    return record


def capture_inputs(
    recipe: Path,
    entry: dict,
    *,
    project,
    inherited: dict | None = None,
    shared: list[dict] | None = None,
    allow_unbound: bool = False,
) -> dict:
    """只登记入口声明且有实际文件的输入；官方分片等非路径值不作为资产。"""
    if not entry:
        return {}
    from omegaconf import OmegaConf

    cfg = OmegaConf.load(recipe / entry["config"])
    result = {}
    for key, kind in entry.get("inputs", {}).items():
        value = OmegaConf.select(cfg, key)
        if not isinstance(value, str):
            continue
        path = Path(value).expanduser()
        if not path.is_absolute():
            path = (recipe / entry["config"]).parent / path
        old = (inherited or {}).get(key)
        # 配置可把同一输入槽改绑到另一共享资产；旧引用不能遮蔽新资产的依赖闭包。
        if old is not None and asset_path(project, old).resolve() != path.resolve():
            old = None
        from ..storage.shared_datasets import resolve_reference

        current = resolve_reference(project, path)
        if current is not None:
            if current.get("status") != "available":
                raise ValueError("shared_dataset_unavailable")
            old = current
        if old is None:
            old = next(
                (a for a in (shared or []) if asset_path(project, a).resolve() == path.resolve()),
                None,
            )
        if old is None and path.resolve().is_relative_to(Path(project).resolve()):
            from ..storage.files import read_json

            receipt = path.parent / "asset.json"
            if receipt.is_file():
                candidate = read_json(receipt)
                if (
                    candidate.get("path")
                    and asset_path(project, candidate).resolve() == path.resolve()
                ):
                    old = candidate
        if old and asset_path(project, old).resolve() == path.resolve():
            validate_asset(project, old)
            result[key] = old
        else:
            # 创建时允许模板保留待绑定路径；执行捕获仍要求实际文件。
            if allow_unbound and not path.exists():
                continue
            from ..storage.files import read_json
            from ..storage.records import listing

            indexed = None
            for run in listing(project, "run"):
                index_path = Path(project) / run.get("run_path", "") / "artifacts/assets.json"
                if not index_path.is_file():
                    continue
                for item in read_json(index_path).get("items", {}).values():
                    if Path(item["path"]).resolve() == path.resolve():
                        candidate = indexed_asset(
                            item, provenance={"run_id": run["id"], "task_id": run["task_id"]}
                        )
                        if indexed is not None:
                            from ai4e_spec.artifacts.task_operations import exact_json_equal

                            # writer 的无用途文件索引与应用补充的用途索引可指向同一文件。
                            # 只采用实际生产者给出的标签；两份非空声明冲突才拒绝。
                            if not candidate.get("semantics") and indexed.get("semantics"):
                                continue
                            keys = ("kind", "stage", "name", "semantics")
                            if (
                                indexed.get("semantics")
                                and candidate.get("semantics")
                                and not exact_json_equal(
                                    {k: indexed.get(k) for k in keys},
                                    {k: candidate.get(k) for k in keys},
                                )
                            ):
                                raise ValueError("asset_labels_conflict")
                        indexed = candidate
            result[key] = indexed or describe_asset(path, kind=kind)
    return result


def copy_assets(
    project: str | Path, assets: dict, stage: Path, final: Path, kinds: set[str]
) -> dict:
    """按类别复制到子任务，来源身份保留；未选资产继续引用。"""
    if not kinds <= KINDS:
        raise ValueError("invalid_copy_kind")
    result = {}
    for key, original in assets.items():
        source = validate_asset(project, original)
        if original["kind"] not in kinds:
            result[key] = original
            continue
        if (
            original.get("dependencies")
            and not original.get("shared_dataset")
            and not original.get("bundle")
        ):
            raise ValueError("asset_copy_not_portable: use reference fork")
        if original.get("portable") is False:
            raise ValueError("asset_copy_not_portable: use reference fork")
        folder = inside(stage / "assets", key)
        folder.mkdir(parents=True)
        if original.get("bundle"):
            value = copy_bundle(
                project, original, folder / "content", final / folder.relative_to(stage) / "content"
            )
            value.update(
                id=uuid4().hex, source={"asset_id": original["id"], **original.get("source", {})}
            )
            write_json(folder / "asset.json", value)
            result[key] = value
            continue
        target = folder / "content" / source.name if source.is_file() else folder / "content"
        shared_copy = original.get("shared_dataset") and original["kind"] == "dataset"
        if shared_copy:
            from ..storage.asset_transfer import copy_declared_dataset

            context = original.get("application_context")
            if context is None:
                raise ValueError("operation_unavailable: dataset_copy_source_missing")
            copy_declared_dataset(source, target.parent, context=context)
        else:
            copy_content(source, target)
        if not shared_copy and digest(inventory(target)) != original["digest"]:
            raise ValueError("asset_copy_changed")
        relative = target.relative_to(stage)
        value = {
            **original,
            "id": uuid4().hex,
            "external": False,
            "path": str((final / relative).relative_to(Path(project).resolve())),
            "source": {"asset_id": original["id"], **original.get("source", {})},
        }
        if shared_copy:
            value.pop("shared_dataset", None)
            value.pop("consumer_binding", None)
            value["digest"] = digest(inventory(target))
            value["dependencies"] = [
                {
                    "id": uuid4().hex,
                    "kind": "dataset",
                    "external": False,
                    "path": str(
                        (final / target.parent.relative_to(stage)).relative_to(
                            Path(project).resolve()
                        )
                    ),
                    "digest": digest(inventory(target.parent)),
                    "dependencies": [],
                }
            ]
        write_json(folder / "asset.json", value)
        result[key] = value
    return result


def collect_run_assets(project: str | Path, run: dict, kinds: set[str]) -> dict:
    """依据捕获入口的产物声明收集父运行输出；复制不自动绑定训练输入。"""
    from ai4e_spec.artifacts.indexes import INDEX_VERSION

    from ..storage.files import read_json

    root = Path(project).resolve()
    directory = root / run["run_path"]
    path = directory / "artifacts/assets.json"
    if not path.is_file():
        return {}
    index = read_json(path)
    if index.get("schema_version") != INDEX_VERSION:
        raise ValueError("unsupported_asset_index")
    result = {}
    provenance = {"run_id": run["id"], "task_id": run["task_id"], "version_id": run["version_id"]}
    for key, item in index["items"].items():
        if item["kind"] not in kinds:
            continue
        record = indexed_asset(item, provenance=provenance)
        safe_key = key.replace("/", "-")
        result[f"run-{run['id']}-{safe_key}"] = record
    return result
