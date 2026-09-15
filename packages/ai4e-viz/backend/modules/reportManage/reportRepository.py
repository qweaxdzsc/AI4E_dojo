"""报告实体、草稿、不可变版本和导出任务的迁移期Repository实现。

本文件由旧Store完整迁入模块以先消除根目录散乱实现；草稿与文档校验随后抽取到
``reportDesigner``，公开调用始终经过两个一级模块门面。
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import uuid
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from infrastructure.config import configured_database_path
from infrastructure.persistence.sqlite import connect
from modules.reportDesigner import get_draft, replace_draft, scaffold_document, validate_document


def _db_path() -> str:
    return str(configured_database_path("QODER_REPORT_DB", "QODER_ASSET_DB", "QODER_SPEC_DB"))


def _connect() -> sqlite3.Connection:
    return connect(_db_path())


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _hash(value: dict[str, Any]) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def initialize() -> None:
    """初始化报告、不可变版本和导出任务表。"""

    with _connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
              migration_id TEXT PRIMARY KEY,
              applied_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS reports (
              report_id TEXT PRIMARY KEY,
              title TEXT NOT NULL,
              author TEXT NOT NULL,
              status TEXT NOT NULL,
              origin TEXT NOT NULL,
              editable INTEGER NOT NULL,
              brief_json TEXT NOT NULL,
              draft_json TEXT NOT NULL,
              draft_revision INTEGER NOT NULL,
              current_version INTEGER,
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_reports_updated ON reports(updated_at DESC);
            CREATE TABLE IF NOT EXISTS report_versions (
              report_id TEXT NOT NULL,
              version INTEGER NOT NULL,
              document_json TEXT NOT NULL,
              content_hash TEXT NOT NULL,
              created_at TEXT NOT NULL,
              created_by TEXT NOT NULL,
              PRIMARY KEY (report_id, version),
              FOREIGN KEY (report_id) REFERENCES reports(report_id)
            );
            CREATE TABLE IF NOT EXISTS report_exports (
              export_id TEXT PRIMARY KEY,
              report_id TEXT NOT NULL,
              report_version INTEGER NOT NULL,
              format TEXT NOT NULL,
              mode TEXT NOT NULL,
              status TEXT NOT NULL,
              stage TEXT NOT NULL,
              output_path TEXT,
              manifest_json TEXT,
              error_json TEXT,
              log_path TEXT,
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL,
              FOREIGN KEY (report_id, report_version) REFERENCES report_versions(report_id, version)
            );
            CREATE INDEX IF NOT EXISTS idx_report_exports_report ON report_exports(report_id, created_at DESC);
            """
        )
        conn.execute(
            "INSERT OR IGNORE INTO schema_migrations (migration_id, applied_at) VALUES (?, ?)",
            ("2026-08-24-report-composer", _now()),
        )


def create_report(brief: dict[str, Any], *, origin: str = "user", editable: bool = True) -> dict[str, Any]:
    """创建报告实体及首个可编辑草稿。"""

    initialize()
    report_id = str(brief.get("report_id") or f"rep-{uuid.uuid4().hex[:12]}")
    document = scaffold_document(brief)
    errors = validate_document(document)
    if errors:
        raise ValueError(errors)
    now = _now()
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO reports (
              report_id, title, author, status, origin, editable, brief_json,
              draft_json, draft_revision, current_version, created_at, updated_at
            ) VALUES (?, ?, ?, 'draft', ?, ?, ?, ?, 1, NULL, ?, ?)
            """,
            (
                report_id, document["metadata"]["title"], document["metadata"]["author"],
                origin, 1 if editable else 0, json.dumps(brief, ensure_ascii=False),
                json.dumps(document, ensure_ascii=False), now, now,
            ),
        )
    return get_draft(report_id)


def _report_row(row: sqlite3.Row) -> dict[str, Any]:
    item = dict(row)
    item["brief"] = json.loads(item.pop("brief_json"))
    item["document"] = json.loads(item.pop("draft_json"))
    item["editable"] = bool(item["editable"])
    item["id"] = item["report_id"]
    item["generated_at"] = item["updated_at"][:16].replace("T", " ")
    item["formats"] = []
    item["status_note"] = "可编辑草稿" if item["status"] == "draft" else f"已冻结 v{item.get('current_version') or 1}"
    return item


def list_reports() -> list[dict[str, Any]]:
    """按更新时间倒序列出报告中心可见报告。"""

    initialize()
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM reports WHERE origin != 'reader-snapshot' ORDER BY updated_at DESC, report_id"
        ).fetchall()
    return [_report_row(row) for row in rows]


def restore_reports_from_snapshot(snapshot_database: str | Path) -> dict[str, int]:
    """从一致性SQLite快照恢复缺失报告，并拒绝覆盖同ID的不同内容。

    恢复属于 ``reportManage`` 的持久化职责，因此由Repository执行。源库只读打开并先做
    完整性检查；目标库在单个事务中写入报告、不可变版本和导出任务。任何主键内容冲突
    都会在写入前失败，防止为了“恢复”而静默覆盖当前用户数据。
    """

    initialize()
    source_path = Path(snapshot_database).expanduser().resolve()
    if not source_path.is_file():
        raise FileNotFoundError(source_path)
    source_uri = f"file:{source_path}?mode=ro"
    table_columns = {
        "reports": (
            "report_id", "title", "author", "status", "origin", "editable", "brief_json",
            "draft_json", "draft_revision", "current_version", "created_at", "updated_at",
        ),
        "report_versions": (
            "report_id", "version", "document_json", "content_hash", "created_at", "created_by",
        ),
        "report_exports": (
            "export_id", "report_id", "report_version", "format", "mode", "status", "stage",
            "output_path", "manifest_json", "error_json", "log_path", "created_at", "updated_at",
        ),
    }

    with sqlite3.connect(source_uri, uri=True) as source:
        source.row_factory = sqlite3.Row
        integrity = source.execute("PRAGMA integrity_check").fetchone()[0]
        if integrity != "ok":
            raise RuntimeError(f"报告恢复源库完整性检查失败: {integrity}")
        available = {
            row[0] for row in source.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }
        source_rows = {
            table: source.execute(f"SELECT {', '.join(columns)} FROM {table}").fetchall()
            if table in available else []
            for table, columns in table_columns.items()
        }

    inserted = {"reports": 0, "report_versions": 0, "report_exports": 0}
    unchanged = {"reports": 0, "report_versions": 0, "report_exports": 0}
    primary_keys = {
        "reports": ("report_id",),
        "report_versions": ("report_id", "version"),
        "report_exports": ("export_id",),
    }
    with _connect() as target:
        # 先检查所有冲突，再进行任何写入，保证恢复事务不会留下半合并状态。
        for table, rows in source_rows.items():
            columns = table_columns[table]
            keys = primary_keys[table]
            where = " AND ".join(f"{key}=?" for key in keys)
            for row in rows:
                existing = target.execute(
                    f"SELECT {', '.join(columns)} FROM {table} WHERE {where}",
                    tuple(row[key] for key in keys),
                ).fetchone()
                if existing is None:
                    continue
                if tuple(existing[column] for column in columns) != tuple(row[column] for column in columns):
                    identity = ", ".join(f"{key}={row[key]}" for key in keys)
                    raise RuntimeError(f"报告恢复冲突: {table} {identity}")
                unchanged[table] += 1

        for table, rows in source_rows.items():
            columns = table_columns[table]
            keys = primary_keys[table]
            where = " AND ".join(f"{key}=?" for key in keys)
            placeholders = ", ".join("?" for _ in columns)
            for row in rows:
                existing = target.execute(
                    f"SELECT 1 FROM {table} WHERE {where}", tuple(row[key] for key in keys)
                ).fetchone()
                if existing is not None:
                    continue
                target.execute(
                    f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})",
                    tuple(row[column] for column in columns),
                )
                inserted[table] += 1
    return {
        "reports_inserted": inserted["reports"],
        "versions_inserted": inserted["report_versions"],
        "exports_inserted": inserted["report_exports"],
        "records_unchanged": sum(unchanged.values()),
    }


def freeze_report(report_id: str, created_by: str = "原力") -> dict[str, Any]:
    """把当前草稿冻结为新的不可变报告版本。"""

    initialize()
    with _connect() as conn:
        row = conn.execute("SELECT draft_json, current_version FROM reports WHERE report_id=?", (report_id,)).fetchone()
        if row is None:
            raise KeyError(report_id)
        document = json.loads(row["draft_json"])
        errors = validate_document(document)
        if errors:
            raise ValueError(errors)
        version = int(row["current_version"] or 0) + 1
        now = _now()
        digest = _hash(document)
        conn.execute(
            "INSERT INTO report_versions VALUES (?, ?, ?, ?, ?, ?)",
            (report_id, version, json.dumps(document, ensure_ascii=False), digest, now, created_by),
        )
        conn.execute(
            "UPDATE reports SET current_version=?, status='succeeded', updated_at=? WHERE report_id=?",
            (version, now, report_id),
        )
    return get_report_version(report_id, version)


def freeze_reader_snapshot(source_report_id: str, document: dict[str, Any], created_by: str = "原力") -> dict[str, Any]:
    """冻结内置阅读报告快照，但不把内部快照暴露为草稿。"""

    initialize()
    internal_id = f"reader-{hashlib.sha256(source_report_id.encode('utf-8')).hexdigest()[:16]}"
    metadata = document.get("metadata") or {}
    now = _now()
    digest = _hash(document)
    with _connect() as conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO reports (
              report_id, title, author, status, origin, editable, brief_json,
              draft_json, draft_revision, current_version, created_at, updated_at
            ) VALUES (?, ?, ?, 'succeeded', 'reader-snapshot', 0, '{}', ?, 1, NULL, ?, ?)
            """,
            (
                internal_id, str(metadata.get("title") or source_report_id),
                str(metadata.get("author") or created_by), json.dumps(document, ensure_ascii=False), now, now,
            ),
        )
        row = conn.execute(
            "SELECT COALESCE(MAX(version), 0) FROM report_versions WHERE report_id=?", (internal_id,)
        ).fetchone()
        version = int(row[0]) + 1
        conn.execute(
            "INSERT INTO report_versions VALUES (?, ?, ?, ?, ?, ?)",
            (internal_id, version, json.dumps(document, ensure_ascii=False), digest, now, created_by),
        )
        conn.execute(
            "UPDATE reports SET title=?, author=?, draft_json=?, current_version=?, updated_at=? WHERE report_id=?",
            (
                str(metadata.get("title") or source_report_id), str(metadata.get("author") or created_by),
                json.dumps(document, ensure_ascii=False), version, now, internal_id,
            ),
        )
    return get_report_version(internal_id, version)


def get_report_version(report_id: str, version: int | None = None) -> dict[str, Any]:
    """读取指定或当前不可变报告版本。"""

    initialize()
    with _connect() as conn:
        if version is None:
            version = conn.execute("SELECT current_version FROM reports WHERE report_id=?", (report_id,)).fetchone()
            if version is None or version[0] is None:
                raise KeyError((report_id, version))
            version = int(version[0])
        row = conn.execute(
            "SELECT * FROM report_versions WHERE report_id=? AND version=?", (report_id, version)
        ).fetchone()
    if row is None:
        raise KeyError((report_id, version))
    item = dict(row)
    item["document"] = json.loads(item.pop("document_json"))
    return item


def duplicate_report(report_id: str, created_by: str = "原力") -> dict[str, Any]:
    """复制报告并重新生成章节、行和内容块标识。"""

    source = get_draft(report_id)
    brief = deepcopy(source["brief"])
    brief.update({"title": f"{source['title']} 副本", "author": created_by})
    created = create_report(brief)
    document = deepcopy(source["document"])
    document["metadata"]["title"] = brief["title"]
    document["metadata"]["author"] = created_by
    # IDs must be unique inside the duplicated report to keep DnD and anchors stable.
    for section in document["sections"]:
        section["id"] = f"section-{uuid.uuid4().hex[:8]}"
        for row in section["rows"]:
            row["id"] = f"row-{uuid.uuid4().hex[:8]}"
            for block in row["blocks"]:
                block["id"] = f"block-{uuid.uuid4().hex[:10]}"
    return replace_draft(created["report_id"], created["draft_revision"], document)


def create_export(report_id: str, report_version: int, export_format: str, mode: str) -> dict[str, Any]:
    """为冻结版本创建排队中的导出任务。"""

    initialize()
    export_id = f"export-{uuid.uuid4().hex[:12]}"
    now = _now()
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO report_exports (
              export_id, report_id, report_version, format, mode, status, stage,
              output_path, manifest_json, error_json, log_path, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, 'queued', 'queued', NULL, NULL, NULL, NULL, ?, ?)
            """,
            (export_id, report_id, report_version, export_format, mode, now, now),
        )
    return get_export(export_id)


def update_export(export_id: str, **changes: Any) -> dict[str, Any]:
    """仅更新允许的导出状态、产物、清单和错误字段。"""

    allowed = {"status", "stage", "output_path", "manifest", "error", "log_path"}
    values = {key: value for key, value in changes.items() if key in allowed}
    if not values:
        return get_export(export_id)
    columns = []
    params = []
    for key, value in values.items():
        column = f"{key}_json" if key in {"manifest", "error"} else key
        columns.append(f"{column}=?")
        params.append(json.dumps(value, ensure_ascii=False) if key in {"manifest", "error"} else value)
    columns.append("updated_at=?")
    params.extend([_now(), export_id])
    with _connect() as conn:
        cursor = conn.execute(f"UPDATE report_exports SET {', '.join(columns)} WHERE export_id=?", params)
        if cursor.rowcount == 0:
            raise KeyError(export_id)
    return get_export(export_id)


def get_export(export_id: str) -> dict[str, Any]:
    """读取并解码一个报告导出任务。"""

    initialize()
    with _connect() as conn:
        row = conn.execute("SELECT * FROM report_exports WHERE export_id=?", (export_id,)).fetchone()
    if row is None:
        raise KeyError(export_id)
    item = dict(row)
    item["manifest"] = json.loads(item.pop("manifest_json") or "null")
    item["error"] = json.loads(item.pop("error_json") or "null")
    return item
