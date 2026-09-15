"""检查点候选和不可变输入；只在独立检查进程解析模型元信息。"""

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from uuid import uuid4

from ..storage.files import read_json, write_json
from ..storage.layout import inside, task_dir
from .configuration import read_configuration
from .query import get_run, get_task, list_runs


def inspect_inference(operation: str, **payload) -> object:
    """隔离推理元信息与兼容检查，标准输出只接收 JSON。"""
    result = subprocess.run(
        [sys.executable, "-m", "ai4e_task.tasks.inference_inspection"],
        input=json.dumps({"operation": operation, **payload}),
        capture_output=True,
        text=True,
        timeout=300,
        check=False,
    )
    if result.returncode:
        lines = result.stderr.strip().splitlines()
        raise ValueError((lines[-1] if lines else "inference_inspection_failed")[:1200])
    return json.loads(result.stdout)


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
    if not separator or Path(name).name != name or not name.endswith(".pt"):
        raise ValueError("invalid_checkpoint_identity")
    run = get_run(project, run_id)
    if run["task_id"] != task_id or run.get("operation_mode", "execute") != "execute":
        raise ValueError("checkpoint_task_mismatch")
    if "train" not in run.get("stages", []):
        raise ValueError("checkpoint_requires_training_run")
    path = inside(Path(run["run_dir"]) / "checkpoints", name)
    if not path.is_file() or (Path(run["run_dir"]) / "checkpoints" / name).is_symlink():
        raise ValueError("checkpoint_missing_or_linked")
    return run, path


def _preparation(run: dict, metadata: dict) -> Path | None:
    own = Path(run["run_dir"]) / "artifacts/preparation.json"
    if own.is_file():
        return own
    cfg = metadata.get("effective_config") or {}
    candidate = (cfg.get("train") or {}).get("preparation")
    if not candidate:
        return None
    path = Path(candidate)
    if path.is_file():
        return path.resolve()
    return None


def list_inference_checkpoints(project: str | Path, task_id: str) -> list[dict]:
    """列出包括训练中已提交权重在内的候选，不伪造轮次文件。"""
    get_task(project, task_id)
    cache_root = task_dir(project, task_id) / ".dojo/inference_checkpoints"
    candidates, pending = [], []
    for run in list_runs(project, task_id):
        if (
            "train" not in run.get("stages", [])
            or run.get("operation_mode", "execute") != "execute"
        ):
            continue
        for path in sorted((Path(run["run_dir"]) / "checkpoints").glob("*.pt")):
            if path.is_symlink() or not path.is_file():
                continue
            stat = path.stat()
            stamp = [stat.st_ino, stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns]
            cache = cache_root / (hashlib.sha256(str(path).encode()).hexdigest() + ".json")
            try:
                old = read_json(cache) if cache.is_file() else {}
            except (ValueError, OSError):
                old = {}
            candidate = {
                "id": run["id"] + ":" + path.name,
                "run_id": run["id"],
                "name": path.name,
                "size": stat.st_size,
                "status": run["status"],
                "created_at": run.get("created_at"),
                "path": str(path),
            }
            candidates.append((candidate, run, path, cache, stamp, old))
            if old.get("stamp") != stamp or old.get("catalog_version") != 2:
                pending.append(str(path))
    inspected = (
        {v["path"]: v for v in inspect_inference("metadata", paths=pending)} if pending else {}
    )
    result = []
    for candidate, run, path, cache, stamp, old in candidates:
        if str(path) in inspected:
            record = inspected[str(path)]
            # 检查和内容读取期间被训练原子替换，留给下一次刷新而不混合元信息。
            try:
                revision = file_digest(path)
                stat = path.stat()
            except FileNotFoundError:
                continue
            if stamp != [stat.st_ino, stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns]:
                continue
            old = {"catalog_version": 2, "stamp": stamp, "revision": revision, **record}
            write_json(cache, old)
        metadata = old.get("metadata", {})
        preparation = _preparation(run, metadata)
        reason = old.get("error") or ("检查点缺少关联准备记录" if preparation is None else None)
        try:
            prep = read_json(preparation) if preparation else {}
            if not isinstance(prep, dict) or not prep.get("digest"):
                reason = reason or "准备记录缺少内容摘要"
                prep = {}
        except (ValueError, OSError):
            reason, prep, preparation = "准备记录缺失或格式无效", {}, None
        expected = (metadata.get("contract") or {}).get("preparation")
        if expected and prep.get("digest") != expected:
            reason = "检查点与准备记录摘要不一致"
        candidate.update(
            revision=old["revision"],
            epoch=metadata.get("epoch"),
            updates=metadata.get("updates"),
            evaluation=metadata.get("evaluation"),
            contract=metadata.get("contract", {}),
            preparation={
                "path": str(preparation),
                "digest": prep.get("digest"),
                "revision": file_digest(preparation),
            }
            if preparation
            else None,
            compatibility={"status": "invalid" if reason else "compatible", "reason": reason},
        )
        result.append(candidate)
    return result


def inference_samples(project: str | Path, task_id: str, checkpoint_id: str) -> dict:
    """按检查点关联的冻结准备读取真实分片，兼容检查由业务层负责。"""
    candidates = list_inference_checkpoints(project, task_id)
    selected = next((v for v in candidates if v["id"] == checkpoint_id), None)
    if selected is None:
        raise ValueError("checkpoint_not_found")
    if selected["compatibility"]["status"] != "compatible":
        raise ValueError(selected["compatibility"]["reason"])
    value = inspect_inference(
        "inputs",
        arguments={
            "checkpoint": selected["path"],
            "preparation": selected["preparation"]["path"],
            "config": read_configuration(project, task_id)["config"],
            "config_dir": str(task_dir(project, task_id) / "recipe"),
        },
    )
    return {
        **value, "preparation": selected["preparation"],
        "selection_supported": (task_dir(project, task_id) / "recipe/infer.py").is_file(),
    }


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
        write_json(stage / "asset.json", result)
        stage.rename(folder)
        return result
    finally:
        import shutil

        shutil.rmtree(stage, ignore_errors=True)
