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
_IDENTITY_LABELS = (
    ("vtkhdf", "VTKHDF"),
    ("formats", "输出格式"),
    ("sources", "来源域"),
    ("fields", "提取字段"),
    ("geometry", "几何派生"),
    ("save_fields", "保存字段"),
    ("filters", "清洗"),
    ("statistics", "统计"),
    ("extraction", "字段提取"),
    ("root", "数据根"),
    ("train_h5", "训练文件"),
    ("test_h5", "测试文件"),
    ("connectivity_h5", "拓扑文件"),
    ("source_dataset", "数据集组件"),
)


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


def describe_processed_name(
    workspace: str | Path,
    name: str,
    *,
    claim: dict | None = None,
    config: dict | None = None,
) -> dict:
    """给页面回传名称状态；不抛冲突，未确认覆盖的正式提交仍走 check_processed_name。"""
    if not isinstance(name, str) or not name.strip():
        return {"status": "empty", "message": "正式执行前需要填写平台数据集名称。"}
    try:
        record = check_processed_name(workspace, name, claim=claim, config=config)
    except ValueError as exc:
        _, _, location = str(exc).partition(": ")
        return {
            "status": "conflict",
            "message": location or "该平台数据集名称已存在。确认后将覆盖原登记。",
        }
    if record.get("digest"):
        return {"status": "reuse", "message": "名称已存在，声明相同。执行时将询问是否覆盖原登记。"}
    return {"status": "available", "message": ""}


def check_processed_name(
    workspace: str | Path,
    name: str,
    *,
    claim: dict | None = None,
    config: dict | None = None,
    overwrite: bool = False,
) -> dict:
    """执行前核对名称；未确认覆盖时同名不同声明拒绝。"""
    value = validate_processed_name(name)
    path = processed_root(workspace) / value / "dataset.json"
    if not path.is_file():
        return {"name": value, "status": "available"}
    record = describe_processed_dataset(workspace, value)
    incoming = claim or (processed_claim(config) if config else {})
    if overwrite or _claims_compatible(record, incoming, config):
        return record
    if incoming and (record.get("claim") or {}):
        raise ValueError("processed_dataset_name_conflict: " + _conflict_detail(record, incoming))
    return record


def register_processed_dataset(
    workspace: str | Path,
    name: str,
    *,
    manifest_path: str | Path,
    digest: str,
    provenance: dict | None = None,
    claim: dict | None = None,
    overwrite: bool = False,
) -> dict:
    """登记或复用同名同摘要资源；未确认覆盖时同名不同声明拒绝。"""
    value = validate_processed_name(name)
    manifest = Path(manifest_path).resolve()
    if not manifest.is_file() or manifest.name != "manifest.json":
        raise ValueError("processed_dataset_manifest_required")
    if digest != manifest_digest(manifest):
        raise ValueError("processed_dataset_digest_mismatch")
    path = _record_path(workspace, value)
    if path.is_file():
        current = read_json(path)
        incoming = claim or {}
        if overwrite:
            current.update(
                {
                    "manifest_path": str(manifest),
                    "digest": digest,
                    "claim": incoming,
                    "provenance": provenance or {},
                    "created_at": datetime.now(UTC).isoformat(),
                }
            )
            write_json(path, current)
            return describe_processed_dataset(workspace, value)
        if current.get("digest") == digest:
            return describe_processed_dataset(workspace, value)
        if _same_claim(current.get("claim") or {}, incoming):
            current.update(
                {
                    "manifest_path": str(manifest),
                    "digest": digest,
                    "claim": incoming or current.get("claim") or {},
                    "provenance": provenance or current.get("provenance") or {},
                }
            )
            write_json(path, current)
            return describe_processed_dataset(workspace, value)
        raise ValueError(
            "processed_dataset_name_conflict: "
            + _conflict_detail({**current, "claim": current.get("claim") or {}}, incoming)
        )
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
    overwrite: bool = False,
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
    from ..projects.datasets import run_physical_manifest

    manifest = run_physical_manifest(project, run)
    if manifest is None or not manifest.is_file():
        return None
    claim = processed_claim(cfg)
    return register_processed_dataset(
        workspace,
        name,
        manifest_path=manifest,
        digest=manifest_digest(manifest),
        claim=claim,
        overwrite=overwrite,
        provenance={
            "project": str(Path(project).resolve()),
            "task_id": task_id,
            "run_id": run.get("id"),
        },
    )


def processed_claim(config: dict) -> dict:
    """用源数据与处理产物语义识别同名是否同一意图；并行线程与列表顺序不进入声明。"""
    identity = _canonical_identity(config)
    return {"fingerprint": _fingerprint({"identity": identity}), "identity": identity}


def _canonical_identity(config: dict) -> dict:
    """只保留改变产物身份的字段；几何与格式按集合比较。"""
    dataset = config.get("dataset") or {}
    raw = config.get("rawprep") or {}
    return {
        "source_dataset": (config.get("components") or {}).get("dataset"),
        "root": dataset.get("root"),
        "train_h5": dataset.get("train_h5"),
        "test_h5": dataset.get("test_h5"),
        "connectivity_h5": dataset.get("connectivity_h5"),
        "sources": sorted(raw.get("sources") or []),
        "fields": _fields_identity(raw.get("fields") or {}),
        "geometry": _geometry_identity(raw.get("geometry")),
        "save_fields": sorted(raw.get("save_fields") or []),
        "filters": {
            domain: sorted(names)
            for domain, names in sorted((raw.get("filters") or {}).items())
            if isinstance(names, list)
        },
        "statistics": _statistics_identity(raw.get("statistics") or {}),
        "formats": _formats_identity(raw),
        "vtkhdf": bool(raw.get("vtkhdf")),
        "extraction": raw.get("extraction") or None,
    }


def _fields_identity(fields) -> dict:
    """只比较提取了哪些场和分量；展开默认值时多出的来源元数据不另占名称。"""
    if not isinstance(fields, dict):
        return {}
    result = {}
    for domain, items in fields.items():
        if not isinstance(items, dict):
            continue
        result[domain] = {
            name: ({"components": spec.get("components")} if isinstance(spec, dict) else spec)
            for name, spec in items.items()
        }
    return result


def _geometry_identity(value) -> dict:
    if isinstance(value, dict):
        parameters = {
            name: options
            for name, options in value.items()
            if isinstance(options, dict)
            and any(item is not None and item != {} for item in options.values())
        }
        return {"names": sorted(value), "parameters": parameters}
    if isinstance(value, list):
        return {"names": sorted(item for item in value if isinstance(item, str)), "parameters": {}}
    return {"names": [], "parameters": {}}


def _statistics_identity(value: dict) -> dict:
    return {
        "mode": value.get("mode"),
        "fields": sorted(value.get("fields") or []),
        "position_fields": sorted(value.get("position_fields") or []),
    }


def _formats_identity(raw: dict) -> list[str]:
    if raw.get("formats") is not None:
        values = list(raw.get("formats") or [])
    elif "format" in raw:
        values = [raw.get("format")]
    else:
        values = ["pt"]
    return sorted({item for item in values if isinstance(item, str)})


def _fingerprint(payload: dict) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()


def _legacy_fingerprints(config: dict) -> set[str]:
    """兼容旧登记：整段 rawprep 哈希，以及把 workers 算进指纹的历史写法。"""
    dataset = config.get("dataset") or {}
    raw = dict(config.get("rawprep") or {})
    base = {
        "source_dataset": (config.get("components") or {}).get("dataset"),
        "root": dataset.get("root"),
        "train_h5": dataset.get("train_h5"),
        "test_h5": dataset.get("test_h5"),
        "connectivity_h5": dataset.get("connectivity_h5"),
    }
    without_workers = {**base, "rawprep": {k: v for k, v in raw.items() if k != "workers"}}
    return {_fingerprint(without_workers), _fingerprint({**base, "rawprep": raw})}


def _same_claim(existing: dict, incoming: dict) -> bool:
    if not existing or not incoming:
        return False
    left = existing.get("fingerprint")
    right = incoming.get("fingerprint")
    if left and right and left == right:
        return True
    left_id = existing.get("identity")
    right_id = incoming.get("identity")
    return bool(left_id and right_id and left_id == right_id)


def _claims_compatible(record: dict, incoming: dict, config: dict | None) -> bool:
    existing = record.get("claim") or {}
    if not incoming:
        return True
    if not existing:
        return True
    if _same_claim(existing, incoming):
        return True
    if config is not None and existing.get("fingerprint") in _legacy_fingerprints(config):
        return True
    other = existing.get("identity") or _identity_from_provenance(record)
    incoming_id = incoming.get("identity")
    return bool(other and incoming_id and other == incoming_id)


def _identity_from_provenance(record: dict) -> dict | None:
    provenance = record.get("provenance") or {}
    project = provenance.get("project")
    task_id = provenance.get("task_id")
    if not project or not task_id:
        return None
    path = Path(project) / "tasks" / str(task_id) / "recipe" / "config.yaml"
    if not path.is_file():
        return None
    try:
        import yaml

        loaded = yaml.safe_load(path.read_text()) or {}
    except (OSError, TypeError, ValueError):
        return None
    if not isinstance(loaded, dict):
        return None
    return _canonical_identity(loaded)


def _conflict_detail(record: dict, incoming: dict) -> str:
    """把声明差异写成可执行提示；线程数不是差异项。"""
    existing_id = (record.get("claim") or {}).get("identity") or _identity_from_provenance(record)
    incoming_id = incoming.get("identity")
    if not existing_id or not incoming_id:
        return "名称已存在。确认后将覆盖原登记。"
    parts = []
    for key, label in _IDENTITY_LABELS:
        if existing_id.get(key) == incoming_id.get(key):
            continue
        if key == "vtkhdf":
            old = "开" if existing_id.get(key) else "关"
            new = "开" if incoming_id.get(key) else "关"
            parts.append(f"已有登记 VTKHDF={old}，当前配置 VTKHDF={new}")
        else:
            parts.append(f"{label}不同")
    if not parts:
        return "名称已存在。确认后将覆盖原登记。"
    return "；".join(parts) + "。确认后将覆盖原登记。"


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
