"""共享资产：按名称保存内容或外部引用，并随目录携带来源。"""

import shutil
from pathlib import Path
from uuid import uuid4

from ..storage.database import transaction
from ..storage.files import copy_content, write_json
from ..storage.layout import inside
from ..storage.records import fetch, listing, put
from ..storage.snapshots import digest, inventory
from ..tasks.assets import describe_asset, validate_asset
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
) -> dict:
    """按资产名登记或复制共享内容；目标存在时拒绝覆盖。"""
    open_project(project)
    project = Path(project).resolve()
    target = inside(project / "shared", name)
    value = describe_asset(Path(source), kind=kind, source=provenance)
    value["name"] = name
    value["dependencies"] = dependencies or []
    for dep in value["dependencies"]:
        validate_asset(project, dep)
    stage = project / ".dojo" / f"asset-{uuid4().hex}.tmp"
    published = False
    try:
        with transaction(project) as db:
            if target.exists():
                raise FileExistsError(target)
            stage.mkdir()
            if copy:
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
    if not any(source.is_relative_to(r) for r in roots):
        raise ValueError("asset_not_owned_by_run")
    return register_shared(
        project,
        name,
        source,
        kind=kind,
        copy=copy,
        provenance={"run_id": run_id, "task_id": run["task_id"], "version_id": run["version_id"]},
    )
