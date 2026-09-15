"""数据资产元数据、分类历史和画像结果Repository实现。

dataAssets独占 ``artifacts`` 与 ``artifact_classification_history`` 的表、SQL和映射；SQLite
连接与事务使用Infrastructure。所有SQL使用参数绑定，分类修正和历史记录在同一事务提交。
"""

from __future__ import annotations

import json
import os
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from infrastructure.config import REPOSITORY_ROOT, configured_database_path, runtime_paths
from infrastructure.persistence.sqlite import connect, transaction


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS artifacts (
  artifact_id TEXT PRIMARY KEY, name TEXT NOT NULL, file_name TEXT NOT NULL,
  file_path TEXT NOT NULL, format TEXT NOT NULL, sha256 TEXT NOT NULL,
  size_bytes INTEGER NOT NULL, declared_kind TEXT NOT NULL, detected_kind TEXT,
  family TEXT, dataset_id TEXT, source TEXT NOT NULL,
  parse_status TEXT NOT NULL DEFAULT 'queued', validation_status TEXT NOT NULL DEFAULT 'pending',
  profile_json TEXT, recommendations_json TEXT, last_snapshot TEXT,
  version INTEGER NOT NULL DEFAULT 1, created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_artifacts_sha256 ON artifacts(sha256);
CREATE INDEX IF NOT EXISTS idx_artifacts_updated ON artifacts(updated_at DESC);
CREATE TABLE IF NOT EXISTS artifact_classification_history (
  artifact_id TEXT NOT NULL, version INTEGER NOT NULL, declared_kind TEXT NOT NULL,
  detected_kind TEXT, reason TEXT NOT NULL, created_at TEXT NOT NULL,
  PRIMARY KEY (artifact_id, version),
  FOREIGN KEY (artifact_id) REFERENCES artifacts(artifact_id)
);
"""


def _database_path():
    return configured_database_path("QODER_ASSET_DB", "QODER_SPEC_DB")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def initialize() -> None:
    """初始化数据资产模块拥有的表与索引。"""

    with transaction(_database_path()) as connection:
        connection.executescript(SCHEMA_SQL)


def _decode(row: sqlite3.Row) -> dict[str, Any]:
    item = dict(row)
    stored_path = item["file_path"]
    item["storage_key"] = stored_path
    path = Path(stored_path)
    if not path.is_absolute():
        if path.parts and path.parts[0] in {"resources", "fixtures"}:
            path = REPOSITORY_ROOT / path
        else:
            path = runtime_paths().root / path
    item["file_path"] = str(path.resolve())
    for key in ("profile_json", "recommendations_json"):
        value = item.pop(key, None)
        item[key.removesuffix("_json")] = json.loads(value) if value else None
    return item


def _storage_key(value: str | Path) -> str:
    """把仓库资源或运行文件转换为可迁移的相对键。

    单元测试可能使用系统临时目录；这类外部路径保留绝对值以维持测试隔离。生产内置资源
    与 ``var`` 文件一律写相对路径，数据库不再绑定当前机器用户名或仓库位置。
    """

    path = Path(value).expanduser()
    if not path.is_absolute():
        return path.as_posix()
    resolved = path.resolve()
    for root in (runtime_paths().root, REPOSITORY_ROOT):
        try:
            return resolved.relative_to(root).as_posix()
        except ValueError:
            continue
    return str(resolved)


def upsert_artifact(item: dict[str, Any]) -> dict[str, Any]:
    """新增或更新数据资产登记信息，并保持已有画像字段不被空值覆盖。"""

    initialize()
    now = item.get("updated_at") or _now()
    created = item.get("created_at") or now
    with transaction(_database_path()) as connection:
        connection.execute(
            """
            INSERT INTO artifacts (
              artifact_id, name, file_name, file_path, format, sha256, size_bytes,
              declared_kind, detected_kind, family, dataset_id, source, parse_status,
              validation_status, profile_json, recommendations_json, last_snapshot,
              version, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(artifact_id) DO UPDATE SET
              name=excluded.name, file_name=excluded.file_name, file_path=excluded.file_path,
              format=excluded.format, sha256=excluded.sha256, size_bytes=excluded.size_bytes,
              declared_kind=excluded.declared_kind,
              detected_kind=COALESCE(excluded.detected_kind, artifacts.detected_kind),
              family=COALESCE(excluded.family, artifacts.family),
              dataset_id=COALESCE(excluded.dataset_id, artifacts.dataset_id),
              source=excluded.source, updated_at=excluded.updated_at
            """,
            (
                item["artifact_id"], item["name"], item["file_name"], _storage_key(item["file_path"]),
                item["format"], item["sha256"], int(item["size_bytes"]), item["declared_kind"],
                item.get("detected_kind"), item.get("family"), item.get("dataset_id"),
                item.get("source", "uploaded"), item.get("parse_status", "queued"),
                item.get("validation_status", "pending"),
                json.dumps(item.get("profile"), ensure_ascii=False) if item.get("profile") is not None else None,
                json.dumps(item.get("recommendations"), ensure_ascii=False) if item.get("recommendations") is not None else None,
                item.get("last_snapshot"), int(item.get("version", 1)), created, now,
            ),
        )
    return get_artifact(item["artifact_id"])


def get_artifact(artifact_id: str) -> dict[str, Any]:
    """读取一个数据资产；不存在时抛出KeyError。"""

    initialize()
    with closing(connect(_database_path())) as connection:
        row = connection.execute("SELECT * FROM artifacts WHERE artifact_id = ?", (artifact_id,)).fetchone()
    if row is None:
        raise KeyError(artifact_id)
    return _decode(row)


def list_artifacts() -> list[dict[str, Any]]:
    """按上传优先和更新时间倒序列出数据资产。"""

    initialize()
    with closing(connect(_database_path())) as connection:
        rows = connection.execute("SELECT * FROM artifacts ORDER BY CASE source WHEN 'uploaded' THEN 0 WHEN 'gs-fixture' THEN 1 ELSE 2 END, updated_at DESC, artifact_id").fetchall()
    return [_decode(row) for row in rows]


def find_uploaded_by_sha256(digest: str) -> dict[str, Any] | None:
    """按SHA-256查找最早上传的重复数据资产。"""

    initialize()
    with closing(connect(_database_path())) as connection:
        row = connection.execute("SELECT * FROM artifacts WHERE sha256 = ? AND source = 'uploaded' ORDER BY created_at LIMIT 1", (digest,)).fetchone()
    return _decode(row) if row else None


def store_uploaded_bytes(content: bytes, file_name: str, digest: str, root: str | Path) -> Path:
    """把上传字节原子写入模块对象目录，并返回最终文件路径。

    临时文件和最终文件位于同一对象目录，``os.replace``可避免进程中断后留下半文件；
    文件名只取``Path.name``，不能通过上传名称越过资产目录。
    """

    safe_name = Path(file_name).name
    target = Path(root) / digest / safe_name
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        temporary = target.with_suffix(f"{target.suffix}.part")
        temporary.write_bytes(content)
        os.replace(temporary, target)
    return target


def save_analysis(artifact_id: str, profile: dict[str, Any], recommendations: dict[str, Any], *, validation_status: str, family: str, last_snapshot: str | None = None) -> dict[str, Any]:
    """原子保存解析画像、推荐和校验状态。"""

    initialize()
    with transaction(_database_path()) as connection:
        cursor = connection.execute(
            """UPDATE artifacts SET detected_kind=?, family=?, parse_status='ready', validation_status=?,
            profile_json=?, recommendations_json=?, last_snapshot=COALESCE(?, last_snapshot), updated_at=? WHERE artifact_id=?""",
            (profile.get("inferred_kind"), family, validation_status, json.dumps(profile, ensure_ascii=False), json.dumps(recommendations, ensure_ascii=False), last_snapshot, _now(), artifact_id),
        )
        if cursor.rowcount == 0:
            raise KeyError(artifact_id)
    return get_artifact(artifact_id)


def save_analysis_error(artifact_id: str, error: dict[str, Any]) -> dict[str, Any]:
    """保存解析失败诊断，同时保留数据集登记记录。"""

    initialize()
    profile = {"failed": True, "error": error}
    with transaction(_database_path()) as connection:
        cursor = connection.execute("UPDATE artifacts SET parse_status='error', validation_status='error', profile_json=?, updated_at=? WHERE artifact_id=?", (json.dumps(profile, ensure_ascii=False), _now(), artifact_id))
        if cursor.rowcount == 0:
            raise KeyError(artifact_id)
    return get_artifact(artifact_id)


def update_classification(artifact_id: str, declared_kind: str, reason: str) -> dict[str, Any]:
    """基于版本号修正分类，并在同一事务写入审计历史。"""

    initialize()
    with transaction(_database_path()) as connection:
        row = connection.execute("SELECT version, detected_kind FROM artifacts WHERE artifact_id=?", (artifact_id,)).fetchone()
        if row is None:
            raise KeyError(artifact_id)
        version = int(row["version"]) + 1
        now = _now()
        connection.execute("UPDATE artifacts SET declared_kind=?, version=?, updated_at=? WHERE artifact_id=?", (declared_kind, version, now, artifact_id))
        connection.execute("INSERT INTO artifact_classification_history VALUES (?, ?, ?, ?, ?, ?)", (artifact_id, version, declared_kind, row["detected_kind"], reason, now))
    return get_artifact(artifact_id)

__all__ = ["find_uploaded_by_sha256", "get_artifact", "list_artifacts", "save_analysis", "save_analysis_error", "store_uploaded_bytes", "update_classification", "upsert_artifact"]
