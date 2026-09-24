"""工作区已处理数据集登记：按名称保存清单路径与摘要，不复制张量。"""

from __future__ import annotations

import hashlib
import re
from datetime import UTC, datetime
from pathlib import Path

from .files import read_json, write_json

NAME_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9_]{0,63}$")


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
    context: dict | None = None,
) -> dict:
    """给页面回传名称状态；不抛冲突，未确认覆盖的正式提交仍走 check_processed_name。"""
    if not isinstance(name, str) or not name.strip():
        return {"status": "empty", "message": "正式执行前需要填写平台数据集名称。"}
    try:
        record = check_processed_name(workspace, name, claim=claim, context=context)
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
    context: dict | None = None,
    overwrite: bool = False,
) -> dict:
    """执行前核对名称；未确认覆盖时同名不同声明拒绝。"""
    value = validate_processed_name(name)
    path = processed_root(workspace) / value / "dataset.json"
    if not path.is_file():
        return {"name": value, "status": "available"}
    record = describe_processed_dataset(workspace, value)
    incoming = claim or {}
    if overwrite or _claims_compatible(record, incoming):
        return record
    detail = _conflict_detail(record, incoming)
    if context is not None:
        from ..tasks.operation_sources import invoke_source, with_operation

        detail = invoke_source(
            with_operation(context["source"], "inspect"),
            context["recipe"],
            {
                "operation": "dataset_conflict",
                "existing": record.get("claim", {}),
                "incoming": incoming,
            },
        )
        if not isinstance(detail, str):
            raise ValueError("invalid_dataset_conflict_description")
    raise ValueError("processed_dataset_name_conflict: " + detail)


def register_processed_dataset(
    workspace: str | Path,
    name: str,
    *,
    manifest_path: str | Path,
    digest: str,
    provenance: dict | None = None,
    claim: dict | None = None,
    semantics: dict | None = None,
    stage: str | None = None,
    overwrite: bool = False,
) -> dict:
    """登记或复用资源，原样保留显式 semantics/stage；缺标签不推断。

    同名不同声明未确认覆盖时拒绝；同摘要不同标签须明确覆盖。
    """
    value = validate_processed_name(name)
    manifest = Path(manifest_path).resolve()
    if not manifest.is_file() or manifest.name != "manifest.json":
        raise ValueError("processed_dataset_manifest_required")
    if digest != manifest_digest(manifest):
        raise ValueError("processed_dataset_digest_mismatch")
    labels = {"kind": "dataset", "semantics": semantics or {}, "stage": stage}
    path = _record_path(workspace, value)
    if path.is_file():
        current = read_json(path)
        incoming = claim or {}
        if overwrite:
            current.update(
                {
                    **labels,
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
            from ai4e_spec.artifacts.task_operations import exact_json_equal

            if (
                semantics is not None
                and not exact_json_equal(current.get("semantics", {}), semantics)
            ) or (stage is not None and current.get("stage") != stage):
                raise ValueError("asset_labels_conflict")
            return describe_processed_dataset(workspace, value)
        if _same_claim(current.get("claim") or {}, incoming):
            current.update(
                {
                    **labels,
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
        **labels,
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
    context: dict | None = None,
    overwrite: bool = False,
) -> dict | None:
    """登记捕获计划中的唯一成功共享输出；多输出报选择歧义。"""
    if run.get("status") != "succeeded" or run.get("operation_mode", "execute") != "execute":
        return None
    plans = run.get("shared_outputs", [])
    if not plans:
        return None
    if len(plans) != 1:
        raise ValueError("processed_output_selection_required")
    plan = plans[0]
    name = plan["name"]
    manifest = Path(project) / plan["path"] / plan["manifest"]
    if not manifest.is_file():
        return None
    claim = plan.get("identity", {})
    return register_processed_dataset(
        workspace,
        name,
        manifest_path=manifest,
        digest=manifest_digest(manifest),
        claim=claim,
        semantics=plan.get("semantics", {}),
        stage=plan.get("stage"),
        overwrite=overwrite,
        provenance={
            "project": str(Path(project).resolve()),
            "task_id": task_id,
            "run_id": run.get("id"),
        },
    )


def processed_claim(config: dict, *, context: dict) -> dict:
    """通过明确应用上下文生成处理身份；Task 不解释科学配置。"""
    from ..tasks.operation_sources import invoke_source, with_operation

    return invoke_source(
        with_operation(context["source"], "inspect"),
        context["recipe"],
        {"operation": "dataset_identity", "config": config},
    )


def _same_claim(existing: dict, incoming: dict) -> bool:
    from ai4e_spec.artifacts.task_operations import exact_json_equal

    return bool(existing and incoming and exact_json_equal(existing, incoming))


def _claims_compatible(record: dict, incoming: dict, config=None) -> bool:
    return bool(incoming and _same_claim(record.get("claim", {}), incoming))


def _conflict_detail(record: dict, incoming: dict) -> str:
    return "名称已存在且声明不同或缺失。确认后将覆盖原登记。"


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
