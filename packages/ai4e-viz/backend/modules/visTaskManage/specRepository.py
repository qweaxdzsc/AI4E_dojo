"""VisualizationSpec表的模块内Repository实现。

本文件独占 ``visualization_specs`` 表、索引、迁移和SQL。SQLite连接、WAL、外键和事务
来自Infrastructure；Router与Server不得直接执行这里的SQL。
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from typing import Any

from .catalog import canonical_function
from infrastructure.config import configured_database_path
from infrastructure.persistence.sqlite import connect, transaction


SCHEMA_SQL = """
-- visualization_specs由visTaskManage独占，复合主键保证版本不可变。
CREATE TABLE IF NOT EXISTS visualization_specs (
  spec_id TEXT NOT NULL, version INTEGER NOT NULL, artifact_id TEXT NOT NULL,
  function_id TEXT NOT NULL, kind TEXT NOT NULL, params_json TEXT NOT NULL,
  content_hash TEXT NOT NULL, created_at TEXT NOT NULL, created_by TEXT NOT NULL,
  PRIMARY KEY (spec_id, version)
);
-- 按资产读取最新Spec是推荐和工作台的高频查询。
CREATE INDEX IF NOT EXISTS idx_visualization_specs_artifact
  ON visualization_specs(artifact_id, created_at DESC);
"""


def _database_path():
    """返回任务模块数据库路径，并兼容旧测试变量。"""

    return configured_database_path("QODER_SPEC_DB")


def _content_hash(payload: dict[str, Any]) -> str:
    """生成稳定摘要，用于识别内容等价的Spec。"""

    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def _migrate_previous_schema(connection: sqlite3.Connection) -> None:
    """原位迁移曾包含variant字段的旧表，保持记录和主键不变。"""

    exists = connection.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='visualization_specs'"
    ).fetchone()
    if not exists:
        return
    columns = {row["name"] for row in connection.execute("PRAGMA table_info(visualization_specs)").fetchall()}
    if "variant" not in columns:
        return
    connection.executescript(
        """
        -- 影子表迁移兼容不支持DROP COLUMN的SQLite版本。
        CREATE TABLE visualization_specs_current (
          spec_id TEXT NOT NULL, version INTEGER NOT NULL, artifact_id TEXT NOT NULL,
          function_id TEXT NOT NULL, kind TEXT NOT NULL, params_json TEXT NOT NULL,
          content_hash TEXT NOT NULL, created_at TEXT NOT NULL, created_by TEXT NOT NULL,
          PRIMARY KEY (spec_id, version)
        );
        INSERT INTO visualization_specs_current
          (spec_id, version, artifact_id, function_id, kind, params_json, content_hash, created_at, created_by)
        SELECT spec_id, version, artifact_id, function_id, kind, params_json, content_hash, created_at, created_by
        FROM visualization_specs;
        DROP TABLE visualization_specs;
        ALTER TABLE visualization_specs_current RENAME TO visualization_specs;
        """
    )


def initialize() -> None:
    """迁移并初始化任务模块表；Server入口不得直接调用。"""

    with transaction(_database_path()) as connection:
        _migrate_previous_schema(connection)
        connection.executescript(SCHEMA_SQL)
        if connection.execute("SELECT COUNT(*) FROM visualization_specs").fetchone()[0] == 0:
            _insert(
                connection, "vspec-0412", 1,
                {
                    "artifact_id": "A-1026", "function_id": "chart.echarts-tensor@2.1.0",
                    "kind": "tensor",
                    "params": {"channel": "sigma_xx", "slice": 128, "colormap": "viridis", "range": [-12, 486]},
                },
                "system",
            )


def _insert(connection: sqlite3.Connection, spec_id: str, version: int, payload: dict[str, Any], created_by: str) -> dict:
    """在当前事务插入不可变版本并返回统一领域映射。"""

    normalized = {**payload, "function_id": canonical_function(payload["function_id"])}
    connection.execute(
        """
        -- 所有字段一次写入，禁止后续UPDATE破坏不可变版本语义。
        INSERT INTO visualization_specs
          (spec_id, version, artifact_id, function_id, kind, params_json, content_hash, created_at, created_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            spec_id, version, normalized["artifact_id"], normalized["function_id"], normalized["kind"],
            json.dumps(normalized.get("params", {}), ensure_ascii=False, sort_keys=True),
            _content_hash(normalized), datetime.now(timezone.utc).isoformat(), created_by,
        ),
    )
    return get_version(spec_id, version, conn=connection)


def _row(row: sqlite3.Row) -> dict:
    """把数据库行映射为现有API契约字典。"""

    return {
        "spec_id": row["spec_id"], "version": row["version"], "artifact_id": row["artifact_id"],
        "function_id": canonical_function(row["function_id"]), "kind": row["kind"],
        "params": json.loads(row["params_json"]), "content_hash": row["content_hash"],
        "created_at": row["created_at"], "created_by": row["created_by"],
    }


def list_specs() -> list[dict]:
    """列出每个Spec的最新不可变版本。"""

    initialize()
    with closing(connect(_database_path())) as connection:
        rows = connection.execute(
            """
            -- 子查询先确定每个Spec最大版本，再回表读取完整内容。
            SELECT current.* FROM visualization_specs current
            JOIN (SELECT spec_id, MAX(version) AS version FROM visualization_specs GROUP BY spec_id) latest
              ON latest.spec_id = current.spec_id AND latest.version = current.version
            ORDER BY current.created_at DESC
            """
        ).fetchall()
    return [_row(row) for row in rows]


def list_versions(spec_id: str) -> list[dict]:
    """按版本倒序列出一个Spec的全部历史。"""

    initialize()
    with closing(connect(_database_path())) as connection:
        rows = connection.execute(
            "SELECT * FROM visualization_specs WHERE spec_id = ? ORDER BY version DESC", (spec_id,)
        ).fetchall()
    return [_row(row) for row in rows]


def get_version(spec_id: str, version: int, *, conn: sqlite3.Connection | None = None) -> dict:
    """读取指定不可变版本；不存在时抛出KeyError。"""

    own_connection = conn is None
    active = conn or connect(_database_path())
    try:
        row = active.execute(
            "SELECT * FROM visualization_specs WHERE spec_id = ? AND version = ?", (spec_id, version)
        ).fetchone()
        if row is None:
            raise KeyError((spec_id, version))
        return _row(row)
    finally:
        if own_connection:
            active.close()


def create_spec(spec_id: str, payload: dict[str, Any], created_by: str = "原力") -> dict:
    """创建Spec首版本；同ID已存在时抛出FileExistsError。"""

    initialize()
    with transaction(_database_path()) as connection:
        if connection.execute("SELECT 1 FROM visualization_specs WHERE spec_id = ?", (spec_id,)).fetchone():
            raise FileExistsError(spec_id)
        return _insert(connection, spec_id, 1, payload, created_by)


def append_version(spec_id: str, base_version: int, payload: dict[str, Any], created_by: str = "原力") -> dict:
    """基于乐观锁追加版本；基线过期时抛出RuntimeError。"""

    initialize()
    with transaction(_database_path()) as connection:
        latest = connection.execute(
            "SELECT MAX(version) FROM visualization_specs WHERE spec_id = ?", (spec_id,)
        ).fetchone()[0]
        if latest is None:
            raise KeyError(spec_id)
        if latest != base_version:
            raise RuntimeError(f"stale base version: expected {latest}, got {base_version}")
        return _insert(connection, spec_id, latest + 1, payload, created_by)


__all__ = ["append_version", "create_spec", "get_version", "initialize", "list_specs", "list_versions"]
