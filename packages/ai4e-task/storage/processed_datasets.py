"""工作区已处理数据集登记：按名称保存清单路径与摘要，不复制张量。"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import UTC, datetime
from pathlib import Path

from .files import read_json, write_json

NAME_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9_]{0,63}$")
CLAIM_EXCLUDED_RAWPREP = frozenset({"workers"})


def processed_root(workspace: str | Path) -> Path:
    """工作区已处理数据集目录。"""
    return Path(workspace).resolve() / "datasets"


def validate_processed_name(name: str) -> str:
    """校验平台数据集名称；空值与非法字符都拒绝。"""
    if not isinstance(name, str) or not name.strip():
        raise ValueError("processed_dataset_name_required")
    value = name.strip()
    if not NAME_PATTERN.fullmatch(value):
        raise ValueError("processed_dataset_name_invalid")
    return value


def manifest_digest(path: str | Path) -> str:
    """清单文件内容摘要；路径丢失时由调用方先判断存在。"""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _record_path(workspace: str | Path, name: str) -> Path:
    return processed_root(workspace) / validate_processed_name(name) / "dataset.json"


def describe_processed_dataset(workspace: str | Path, name: str) -> dict:
    """读取一条登记并核验清单是否仍可用。"""
    path = _record_path(workspace, name)
    if not path.is_file():
        raise KeyError(name)
    record = read_json(path)
    status, reason = _availability(record)
    return {**record, "status": status, "reason": reason}


def _listed_at(record: dict, path: Path) -> str:
    """登记时间；旧记录缺字段时用登记文件修改时间，避免按目录名冒充先后。"""
    value = record.get("created_at")
    if isinstance(value, str) and value.strip():
        return value
    try:
        return datetime.fromtimestamp(path.stat().st_mtime, UTC).isoformat()
    except OSError:
        return ""


def list_processed_datasets(workspace: str | Path) -> list[dict]:
    """列出工作区全部已处理数据集，含可用性；按登记时间倒序。"""
    root = processed_root(workspace)
    if not root.is_dir():
        return []
    result = []
    for child in root.iterdir():
        path = child / "dataset.json"
        if not path.is_file():
            continue
        try:
            item = describe_processed_dataset(workspace, child.name)
        except (KeyError, TypeError, ValueError, OSError):
            continue
        result.append((item, _listed_at(item, path)))
    result.sort(key=lambda pair: pair[0]["name"])
    result.sort(key=lambda pair: pair[1], reverse=True)
    return [item for item, _ in result]


def check_processed_name(workspace: str | Path, name: str, *, claim: dict | None = None) -> dict:
    """执行前核对名称：空名、非法名或同名不同声明都拒绝。"""
    value = validate_processed_name(name)
    path = processed_root(workspace) / value / "dataset.json"
    if not path.is_file():
        return {"name": value, "status": "available"}
    record = describe_processed_dataset(workspace, value)
    existing = record.get("claim") or {}
    if claim and existing and existing != claim:
        raise ValueError("processed_dataset_name_conflict")
    return record


def register_processed_dataset(
    workspace: str | Path,
    name: str,
    *,
    manifest_path: str | Path,
    digest: str,
    provenance: dict | None = None,
    claim: dict | None = None,
) -> dict:
    """登记或复用同名同摘要资源；同名不同摘要拒绝覆盖。"""
    value = validate_processed_name(name)
    manifest = Path(manifest_path).resolve()
    if not manifest.is_file() or manifest.name != "manifest.json":
        raise ValueError("processed_dataset_manifest_required")
    if digest != manifest_digest(manifest):
        raise ValueError("processed_dataset_digest_mismatch")
    path = _record_path(workspace, value)
    if path.is_file():
        current = read_json(path)
        if current.get("digest") == digest:
            return describe_processed_dataset(workspace, value)
        existing_claim = current.get("claim") or {}
        incoming = claim or {}
        if incoming and existing_claim and incoming == existing_claim:
            current.update(
                {
                    "manifest_path": str(manifest),
                    "digest": digest,
                    "provenance": provenance or current.get("provenance") or {},
                }
            )
            write_json(path, current)
            return describe_processed_dataset(workspace, value)
        raise ValueError("processed_dataset_name_conflict")
    record = {
        "name": value,
        "manifest_path": str(manifest),
        "digest": digest,
        "claim": claim or {},
        "provenance": provenance or {},
        "created_at": datetime.now(UTC).isoformat(),
    }
    write_json(path, record)
    return describe_processed_dataset(workspace, value)


def publish_processed_from_run(
    workspace: str | Path,
    project: str | Path,
    task_id: str,
    run: dict,
    *,
    config: dict | None = None,
) -> dict | None:
    """成功正式原始处理按配置名称登记；试跑或不完整产物跳过。"""
    if run.get("status") != "succeeded" or run.get("operation_mode", "execute") != "execute":
        return None
    stages = run.get("stages") or []
    if "rawprep" not in stages:
        return None
    cfg = config or {}
    name = (cfg.get("dataset") or {}).get("processed_name")
    if not name:
        return None
    manifest = Path(run["data_dir"]) / "manifest.json"
    if not manifest.is_file():
        return None
    claim = processed_claim(cfg)
    return register_processed_dataset(
        workspace,
        name,
        manifest_path=manifest,
        digest=manifest_digest(manifest),
        claim=claim,
        provenance={
            "project": str(Path(project).resolve()),
            "task_id": task_id,
            "run_id": run.get("id"),
        },
    )


def processed_claim(config: dict) -> dict:
    """用源数据与处理产物语义识别同名是否同一意图；并行线程不进入声明。"""
    dataset = config.get("dataset") or {}
    rawprep = {
        key: value
        for key, value in (config.get("rawprep") or {}).items()
        if key not in CLAIM_EXCLUDED_RAWPREP
    }
    payload = {
        "source_dataset": (config.get("components") or {}).get("dataset"),
        "root": dataset.get("root"),
        "train_h5": dataset.get("train_h5"),
        "test_h5": dataset.get("test_h5"),
        "connectivity_h5": dataset.get("connectivity_h5"),
        "rawprep": rawprep,
    }
    return {
        "fingerprint": hashlib.sha256(
            json.dumps(payload, sort_keys=True, default=str).encode()
        ).hexdigest()
    }


def _availability(record: dict) -> tuple[str, str | None]:
    path = Path(record.get("manifest_path") or "")
    if not path.is_file():
        return "unavailable", "binding_file_missing"
    try:
        if manifest_digest(path) != record.get("digest"):
            return "unavailable", "digest_changed"
    except OSError:
        return "unavailable", "binding_source_unavailable"
    return "available", None
