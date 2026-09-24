"""检查点候选和不可变输入；只在独立检查进程解析模型元信息。"""

import hashlib
import os
from pathlib import Path
from uuid import uuid4

from ..storage.files import read_json, write_json
from ..storage.layout import inside, task_dir
from .configuration import read_configuration
from .records import get_run, get_task, list_runs


def inspect_inference(operation: str, *, context: dict, **payload) -> object:
    """使用明确任务/固定来源执行科学检查；缺上下文不推断应用。"""
    from .operation_sources import invoke_source

    return invoke_source(context["source"], context["recipe"], {"operation": operation, **payload})


def file_digest(path: Path) -> str:
    """按完整文件内容生成修订；不把文件名或修改时间当内容身份。"""
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def checkpoint_path(project: str | Path, task_id: str, identity: str) -> tuple[dict, Path]:
    """从任务已有运行解析候选；调用者不能提供任意磁盘路径。"""
    run_id, separator, name = identity.partition(":")
    if not separator or Path(name).is_absolute() or ".." in Path(name).parts:
        raise ValueError("invalid_checkpoint_identity")
    run = get_run(project, run_id)
    if run["task_id"] != task_id or run.get("operation_mode", "execute") != "execute":
        raise ValueError("checkpoint_task_mismatch")
    path = inside(Path(run["run_dir"]) / "checkpoints", name)
    if not path.is_file() or (Path(run["run_dir"]) / "checkpoints" / name).is_symlink():
        raise ValueError("checkpoint_missing_or_linked")
    return run, path


def list_inference_checkpoints(project: str | Path, task_id: str) -> list[dict]:
    """应用提供候选和科学结论，管理层核验路径、内容修订及缓存来源。"""
    from ..storage.snapshots import digest
    from .operation_sources import operation_context

    get_task(project, task_id)
    context = operation_context(project, task_id)
    cache_root = task_dir(project, task_id) / ".dojo/inference_checkpoints"
    result = []
    for run in list_runs(project, task_id):
        if run.get("operation_mode", "execute") != "execute":
            continue
        paths = inspect_inference("checkpoint_candidates", context=context, run=run)
        for name in paths:
            path = Path(name)
            if (
                not path.resolve().is_relative_to(Path(run["run_dir"]).resolve())
                or path.is_symlink()
                or not path.is_file()
            ):
                raise ValueError("checkpoint_missing_or_linked")
            stat = path.stat()
            stamp = [stat.st_ino, stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns]
            cache = cache_root / (digest([str(path), context["source"]["revision"]]) + ".json")
            old = read_json(cache) if cache.is_file() else {}
            if old.get("stamp") != stamp:
                try:
                    record = inspect_inference(
                        "describe_checkpoint", context=context, path=str(path), run=run
                    )
                except ValueError as exc:
                    record = {
                        "compatibility": {"status": "invalid", "reason": str(exc)},
                        "preparation": None,
                    }
                revision = file_digest(path)
                after = path.stat()
                if stamp != [after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns]:
                    continue
                old = {"stamp": stamp, "revision": revision, **record}
                preparation = old.get("preparation")
                if preparation:
                    preparation["revision"] = file_digest(Path(preparation["path"]))
                write_json(cache, old)
            preparation = old.get("preparation")
            if preparation and (
                not Path(preparation["path"]).is_file()
                or file_digest(Path(preparation["path"])) != preparation["revision"]
            ):
                old = {
                    **old,
                    "compatibility": {
                        "status": "invalid",
                        "reason": "preparation_revision_conflict",
                    },
                }
            relative = path.relative_to(Path(run["run_dir"]) / "checkpoints")
            result.append(
                {
                    **old,
                    "id": run["id"] + ":" + str(relative),
                    "run_id": run["id"],
                    "name": path.name,
                    "size": stat.st_size,
                    "status": run["status"],
                    "created_at": run.get("created_at"),
                    "path": str(path),
                }
            )
    return result


def inference_samples(project: str | Path, task_id: str, checkpoint_id: str) -> dict:
    """按检查点关联的冻结准备读取真实分片，兼容检查由业务层负责。"""
    try:
        candidates = list_inference_checkpoints(project, task_id)
        selected = next((v for v in candidates if v["id"] == checkpoint_id), None)
        if selected is None:
            raise ValueError("checkpoint_not_found")
        if selected["compatibility"]["status"] != "compatible":
            raise ValueError(selected["compatibility"]["reason"])
        value = inspect_inference(
            "inputs",
            context=_inference_provider(project, task_id),
            arguments={
                "checkpoint": selected["path"],
                "preparation": selected["preparation"]["path"],
                "config": read_configuration(project, task_id)["config"],
                "config_dir": str(task_dir(project, task_id) / "recipe"),
            },
        )
    except FileNotFoundError as exc:
        raise ValueError(
            "inference_preparation_missing: 检查点关联的准备或样本文件不存在，请确认数据准备仍可用"
        ) from exc
    return {
        **value,
        "preparation": selected["preparation"],
        "selection_supported": value.get("selection_supported", False),
    }


def _inference_provider(project, task_id):
    """使用任务声明的领域连接解释配置，不在Task转换领域参数。"""
    from .operation_sources import operation_context

    return operation_context(project, task_id)


def freeze_checkpoint(project: str | Path, task_id: str, identity: str, revision: str) -> dict:
    """固定选择时的完整字节；原权重更新不改变已经固定的副本。"""
    run, path = checkpoint_path(project, task_id, identity)
    asset_id = uuid4().hex
    folder = task_dir(project, task_id) / "assets" / asset_id
    stage = folder.with_name("." + asset_id + ".tmp")
    stage.mkdir(parents=True)
    try:
        h = hashlib.sha256()
        with path.open("rb") as source, (stage / "checkpoint.pt").open("wb") as target:
            before = os.fstat(source.fileno())
            for block in iter(lambda: source.read(1024 * 1024), b""):
                h.update(block)
                target.write(block)
            target.flush()
            os.fsync(target.fileno())
            after = os.fstat(source.fileno())
        if h.hexdigest() != revision or (before.st_size, before.st_mtime_ns) != (
            after.st_size,
            after.st_mtime_ns,
        ):
            raise ValueError("checkpoint_revision_conflict: 检查点已更新，请刷新选择")
        result = {
            "id": asset_id,
            "kind": "checkpoint",
            "revision": revision,
            "path": str(folder / "checkpoint.pt"),
            "source": {"run_id": run["id"], "checkpoint": identity},
        }
        from .assets import describe_asset

        labels = {}
        index = Path(run["run_dir"]) / "artifacts/assets.json"
        if index.is_file():
            for item in read_json(index).get("items", {}).values():
                if Path(item["path"]).resolve() == path.resolve():
                    labels = {
                        key: item[key] for key in ("semantics", "stage", "name") if key in item
                    }
        result = {
            **describe_asset(stage / "checkpoint.pt", kind="checkpoint", **labels),
            **result,
            **labels,
        }
        write_json(stage / "asset.json", result)
        stage.rename(folder)
        return result
    finally:
        import shutil

        shutil.rmtree(stage, ignore_errors=True)
