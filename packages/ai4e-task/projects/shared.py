"""共享资产：按名称保存内容或外部引用，并随目录携带来源。"""

import shutil
from pathlib import Path
from uuid import uuid4

from ..storage.database import transaction
from ..storage.files import copy_content, write_json
from ..storage.layout import inside
from ..storage.records import fetch, listing, put
from ..storage.snapshots import digest, inventory
from ..tasks.assets import copy_bundle, describe_asset, indexed_asset, validate_asset
from .project import open_project


def register_shared(
    project,
    name: str,
    source,
    *,
    kind: str = "other",
    copy: bool = False,
    provenance: dict | None = None,
    dependencies: list[dict] | None = None,
    bundle: dict | None = None,
    semantics: dict | None = None,
    stage: str | None = None,
    asset_name: str | None = None,
) -> dict:
    """按资产名登记或复制共享内容；目标存在时拒绝覆盖。"""
    open_project(project)
    project = Path(project).resolve()
    target = inside(project / "shared", name)
    value = describe_asset(
        Path(source), kind=kind, source=provenance, semantics=semantics, stage=stage
    )
    value["name"] = asset_name if asset_name is not None else name
    value["registration_name"] = name
    value["dependencies"] = dependencies or []
    if bundle is not None:
        value["bundle"] = bundle
        validate_asset(project, value)
    for dep in value["dependencies"]:
        validate_asset(project, dep)
    if copy and value["dependencies"] and not bundle:
        # 不猜测领域清单中的引用位置；复制主文件不能冒充可迁移的完整资产。
        raise ValueError(
            "asset_copy_not_portable: publish a self-contained bundle or use reference"
        )
    stage = project / ".dojo" / f"asset-{uuid4().hex}.tmp"
    published = False
    try:
        with transaction(project) as db:
            if target.exists():
                raise FileExistsError(target)
            stage.mkdir()
            if copy and bundle:
                value = copy_bundle(project, value, stage / "content", target / "content")
            elif copy:
                src = Path(source).resolve()
                dest = stage / "content" / src.name if src.is_file() else stage / "content"
                copy_content(src, dest)
                if digest(inventory(dest)) != value["digest"]:
                    raise ValueError("asset_copy_changed")
                value.update(
                    external=False,
                    path=str((target / dest.relative_to(stage)).relative_to(project)),
                )
            write_json(stage / "asset.json", value)
            target.parent.mkdir(parents=True, exist_ok=True)
            stage.rename(target)
            published = True
            put(db, "asset", value)
    except BaseException:
        if published:
            shutil.rmtree(target)
        raise
    finally:
        shutil.rmtree(stage, ignore_errors=True)
    return value


def list_shared(project: str | Path) -> list[dict]:
    """列出共享资产登记。"""
    return listing(project, "asset")


def get_shared(project: str | Path, asset_id: str, *, validate: bool = True) -> dict:
    """查询资产，默认核验内容与依赖。"""
    value = fetch(project, "asset", asset_id)
    if validate:
        validate_asset(project, value)
    return value


def share_run_asset(
    project, run_id: str, name: str, path, *, kind: str = "other", copy: bool = True
) -> dict:
    """显式共享某次运行的产物，仅接受归属该运行的数据或记录区域。"""
    from ..tasks.query import get_run

    run = get_run(project, run_id)
    source = Path(path).resolve()
    roots = [Path(run["run_dir"]).resolve(), Path(run["data_dir"]).resolve()]
    from .datasets import run_physical_manifest

    physical = run_physical_manifest(project, run)
    if physical is not None:
        roots.append(physical.parent.resolve())
    if not any(source.is_relative_to(r) for r in roots):
        raise ValueError("asset_not_owned_by_run")
    from ai4e_core.run.indexes import validate_asset_content

    from ..storage.files import read_json

    dependencies = []
    bundle = None
    labels = {}
    index = Path(run["run_dir"]) / "artifacts/assets.json"
    if index.is_file():
        matches = [
            item
            for item in read_json(index)["items"].values()
            if Path(item["path"]).resolve() == source
        ]
        for item in matches:
            validate_asset_content(item)
            if item["kind"] != kind:
                raise ValueError("asset_kind_conflict")
            for dependency in item["dependencies"]:
                dependencies.append(describe_asset(Path(dependency), kind="other"))
            candidate = indexed_asset(item, provenance={"run_id": run_id})
            incoming_labels = {
                "semantics": candidate.get("semantics", {}),
                "stage": candidate.get("stage"),
                "asset_name": candidate.get("name"),
            }
            if (
                labels.get("semantics")
                and incoming_labels["semantics"]
                and labels != incoming_labels
            ):
                raise ValueError("asset_labels_conflict")
            if incoming_labels["semantics"] or not labels:
                labels = incoming_labels
            if candidate.get("bundle"):
                bundle = candidate["bundle"]
    return register_shared(
        project,
        name,
        source,
        kind=kind,
        copy=copy,
        dependencies=dependencies,
        bundle=bundle,
        provenance={"run_id": run_id, "task_id": run["task_id"], "version_id": run["version_id"]},
        **labels,
    )
