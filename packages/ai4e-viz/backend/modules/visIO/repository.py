"""可视化资产Repository实现。

本模块独占 ``artifact_visualizations`` 表、SQL与表现清单映射。数据集外键由
``visDatasets`` 拥有，本Repository只通过数据库约束协作，不导入其他模块内部Repository。
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from typing import Any

from infrastructure.config import configured_database_path
from infrastructure.persistence.sqlite import connect, transaction


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS artifact_visualizations (
  visualization_id TEXT PRIMARY KEY, artifact_id TEXT NOT NULL,
  recommendation_id TEXT NOT NULL, spec_id TEXT NOT NULL, spec_version INTEGER NOT NULL,
  function_id TEXT NOT NULL, renderer TEXT NOT NULL, parameters_json TEXT NOT NULL,
  payload_json TEXT NOT NULL, status TEXT NOT NULL, created_at TEXT NOT NULL,
  representations_json TEXT, updated_at TEXT,
  FOREIGN KEY (artifact_id) REFERENCES artifacts(artifact_id)
);
CREATE INDEX IF NOT EXISTS idx_artifact_visualizations_artifact
  ON artifact_visualizations(artifact_id, created_at DESC);
"""


def _database_path():
    return configured_database_path("QODER_ASSET_DB", "QODER_SPEC_DB")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def initialize() -> None:
    """初始化可视化资产表并兼容旧库缺失的表现字段。"""

    with transaction(_database_path()) as connection:
        connection.executescript(SCHEMA_SQL)
        columns = {row["name"] for row in connection.execute("PRAGMA table_info(artifact_visualizations)").fetchall()}
        if "representations_json" not in columns:
            connection.execute("ALTER TABLE artifact_visualizations ADD COLUMN representations_json TEXT")
        if "updated_at" not in columns:
            connection.execute("ALTER TABLE artifact_visualizations ADD COLUMN updated_at TEXT")
            connection.execute("UPDATE artifact_visualizations SET updated_at=created_at WHERE updated_at IS NULL")


def create_visualization(item: dict[str, Any]) -> dict[str, Any]:
    """创建不可变可视化资产记录。"""

    initialize()
    now = _now()
    with transaction(_database_path()) as connection:
        connection.execute(
            """INSERT INTO artifact_visualizations (
            visualization_id, artifact_id, recommendation_id, spec_id, spec_version,
            function_id, renderer, parameters_json, payload_json, status, created_at,
            representations_json, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (item["visualization_id"], item["artifact_id"], item["recommendation_id"], item["spec_id"], int(item["spec_version"]), item["function_id"], item["renderer"], json.dumps(item.get("parameters", {}), ensure_ascii=False), json.dumps(item["payload"], ensure_ascii=False), item.get("status", "live"), now, json.dumps(item.get("representations", {}), ensure_ascii=False), now),
        )
    return get_visualization(item["visualization_id"])


def get_visualization(visualization_id: str) -> dict[str, Any]:
    """读取可视化资产并计算内容摘要。"""

    initialize()
    with closing(connect(_database_path())) as connection:
        row = connection.execute("SELECT * FROM artifact_visualizations WHERE visualization_id=?", (visualization_id,)).fetchone()
    if row is None:
        raise KeyError(visualization_id)
    item = dict(row)
    item["parameters"] = json.loads(item.pop("parameters_json"))
    item["payload"] = json.loads(item.pop("payload_json"))
    item["representations"] = json.loads(item.pop("representations_json") or "{}")
    frozen = {"artifact_id": item["artifact_id"], "spec_id": item["spec_id"], "spec_version": item["spec_version"], "parameters": item["parameters"], "payload": item["payload"], "representations": item["representations"]}
    item["content_hash"] = hashlib.sha256(json.dumps(frozen, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    return item


def list_visualizations(*, artifact_id: str | None = None, kind: str | None = None, renderer: str | None = None, dataset_id: str | None = None) -> list[dict[str, Any]]:
    """按数据集、类型和渲染器过滤可视化资产。"""

    initialize()
    clauses: list[str] = []
    parameters: list[Any] = []
    if artifact_id:
        clauses.append("v.artifact_id=?")
        parameters.append(artifact_id)
    if renderer:
        clauses.append("v.renderer=?")
        parameters.append(renderer)
    if dataset_id:
        clauses.append("a.dataset_id=?")
        parameters.append(dataset_id)
    # 只有按dataset_id过滤时才需要跨模块表JOIN；普通空库查询不能要求visDatasets先初始化。
    query = "SELECT v.visualization_id FROM artifact_visualizations v"
    if dataset_id:
        query += " JOIN artifacts a ON a.artifact_id=v.artifact_id"
    if clauses:
        query += " WHERE " + " AND ".join(clauses)
    query += " ORDER BY v.created_at DESC, v.visualization_id"
    with closing(connect(_database_path())) as connection:
        rows = connection.execute(query, parameters).fetchall()
    items = [get_visualization(row["visualization_id"]) for row in rows]
    return [item for item in items if not kind or item.get("payload", {}).get("artifact", {}).get("kind") == kind]


def update_visualization_representations(visualization_id: str, representations: dict[str, Any]) -> dict[str, Any]:
    """更新可重建的表现清单，但不修改冻结业务参数。"""

    initialize()
    with transaction(_database_path()) as connection:
        cursor = connection.execute("UPDATE artifact_visualizations SET representations_json=?, updated_at=? WHERE visualization_id=?", (json.dumps(representations, ensure_ascii=False), _now(), visualization_id))
        if cursor.rowcount == 0:
            raise KeyError(visualization_id)
    return get_visualization(visualization_id)


def latest_visualization(artifact_id: str) -> dict[str, Any] | None:
    """返回数据集最近创建的可视化资产。"""

    initialize()
    with closing(connect(_database_path())) as connection:
        row = connection.execute("SELECT visualization_id FROM artifact_visualizations WHERE artifact_id=? ORDER BY created_at DESC LIMIT 1", (artifact_id,)).fetchone()
    return get_visualization(row["visualization_id"]) if row else None

__all__ = ["create_visualization", "get_visualization", "latest_visualization", "list_visualizations", "update_visualization_representations"]
