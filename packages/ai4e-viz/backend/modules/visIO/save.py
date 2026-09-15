"""统一保存声明式配置；保存不读取/复制源数据，不渲染或自动截图。"""

import shutil
from datetime import UTC, datetime
from uuid import uuid4

from infrastructure.storage.atomic import digest, file_lock, identity

from modules.visTaskManage import read_file_spec, validate_file_spec, write_file_spec

from .assetRepository import asset_root, commit_index, get_asset, scope_root


def save_asset(
    scope: dict,
    spec: dict,
    *,
    name: str,
    visualization_id: str | None = None,
    expected_revision: int = 0,
    request_id: str | None = None,
) -> dict:
    """在作用域内原子追加配置；重复请求返回原提交，冲突不覆盖。"""
    root = scope_root(scope, write=True)
    spec = validate_file_spec(spec)
    if not name.strip():
        raise ValueError("visualization_name_required")
    asset_id = identity(
        visualization_id
        or ("viz-" + (digest([scope["scope_id"], request_id])[:24] if request_id else uuid4().hex))
    )
    content_hash = digest(spec)
    operation_hash = digest([name.strip(), content_hash])
    with file_lock(root, asset_id):
        try:
            old = get_asset(scope, asset_id)
        except FileNotFoundError:
            old = None
        if old and request_id and old.get("request_id") == request_id:
            if old.get("operation_hash") != operation_hash:
                raise ValueError("idempotency_conflict")
            return old
        if (old["revision"] if old else 0) != expected_revision:
            raise ValueError("visualization_revision_conflict")
        revision = expected_revision + 1
        now = datetime.now(UTC).isoformat()
        # 锁内清理索引尚未发布的残留修订，避免一次失败永久阻塞下一次保存。
        unpublished = asset_root(scope, asset_id) / "revisions" / f"{revision:06d}"
        if unpublished.exists():
            shutil.rmtree(unpublished)
        write_file_spec(asset_root(scope, asset_id), revision, spec)
        record = {
            "schema_version": 1,
            "visualization_id": asset_id,
            "project_id": scope["project_id"],
            "task_id": scope["task_id"],
            "kind": spec.get("kind", "phys_field"),
            "name": name.strip(),
            "revision": revision,
            "content_hash": content_hash,
            "created_at": old["created_at"] if old else now,
            "updated_at": now,
            "request_id": request_id,
            "operation_hash": operation_hash,
        }
        record["revision_hashes"] = {
            **(old or {}).get("revision_hashes", {}),
            str(revision): content_hash,
        }
        try:
            commit_index(scope, record)
        except Exception:
            shutil.rmtree(unpublished, ignore_errors=True)
            raise
        return record


def read_asset(scope: dict, asset_id: str, revision: int | None = None) -> dict:
    """读取固定修订；历史配置摘要独立于后续导出。"""
    record = get_asset(scope, asset_id)
    selected = revision or record["revision"]
    if selected > record["revision"]:
        raise ValueError("revision_not_committed")
    spec = read_file_spec(asset_root(scope, asset_id), selected)
    content_hash = digest(spec)
    expected = record.get("revision_hashes", {}).get(
        str(selected), record["content_hash"] if selected == record["revision"] else None
    )
    if expected and expected != content_hash:
        raise ValueError("visualization_configuration_tampered")
    return {**record, "revision": selected, "content_hash": content_hash, "spec": spec}
