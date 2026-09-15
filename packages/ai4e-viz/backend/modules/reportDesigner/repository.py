"""报告草稿与编排修订的持久化实现。

本模块拥有草稿文档和 ``draft_revision`` 的读写语义。它复用 Infrastructure 的
SQLite 连接原语，但不导入 ``reportManage`` 的 Repository，因而可以随一级模块整体拆分。
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from typing import Any

from infrastructure.config import configured_database_path
from infrastructure.persistence.sqlite import connect

from .domain import validate_document


def _db_path() -> str:
    """解析报告模块共用的 SQLite 文件位置。"""

    return str(configured_database_path("QODER_REPORT_DB", "QODER_ASSET_DB", "QODER_SPEC_DB"))


def _connect() -> sqlite3.Connection:
    """建立启用公共 WAL 与外键配置的数据库连接。"""

    return connect(_db_path())


def _now() -> str:
    """返回用于乐观锁更新的 UTC 时间。"""

    return datetime.now(timezone.utc).isoformat()


def _initialize_draft_storage() -> None:
    """确保报告草稿表存在，同时不创建版本和导出等报告管理表。

    两个报告限界上下文暂时共用原有 ``reports`` 表以保持数据库兼容；本模块只声明并
    使用草稿所需列。``CREATE TABLE IF NOT EXISTS`` 使只读内置报告在空测试库中能够
    正确返回“不存在”，而不是泄漏 SQLite 的缺表异常。
    """

    with _connect() as conn:
        conn.execute(
            """
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
            )
            """
        )


def _report_row(row: sqlite3.Row) -> dict[str, Any]:
    """把报告表记录转换为前端草稿接口所需的业务对象。"""

    item = dict(row)
    item["brief"] = json.loads(item.pop("brief_json"))
    item["document"] = json.loads(item.pop("draft_json"))
    item["editable"] = bool(item["editable"])
    item["id"] = item["report_id"]
    item["generated_at"] = item["updated_at"][:16].replace("T", " ")
    item["formats"] = []
    item["status_note"] = "可编辑草稿" if item["status"] == "draft" else f"已冻结 v{item.get('current_version') or 1}"
    return item


def get_draft(report_id: str) -> dict[str, Any]:
    """读取报告当前草稿与修订号；报告不存在时抛出 ``KeyError``。"""

    _initialize_draft_storage()
    with _connect() as conn:
        row = conn.execute("SELECT * FROM reports WHERE report_id=?", (report_id,)).fetchone()
    if row is None:
        raise KeyError(report_id)
    return _report_row(row)


def replace_draft(report_id: str, base_revision: int, document: dict[str, Any]) -> dict[str, Any]:
    """校验并以乐观锁替换草稿，避免多人编排时静默覆盖。

    ``reports`` 表由报告上下文共同使用：报告管理拥有实体、版本和导出字段，报告编排只
    更新标题、作者、草稿文档、草稿修订号与状态。事务在一次连接上下文内原子提交。
    """

    errors = validate_document(document)
    if errors:
        raise ValueError(errors)
    _initialize_draft_storage()
    now = _now()
    with _connect() as conn:
        row = conn.execute(
            "SELECT draft_revision, editable FROM reports WHERE report_id=?",
            (report_id,),
        ).fetchone()
        if row is None:
            raise KeyError(report_id)
        if not row["editable"]:
            raise PermissionError(report_id)
        if int(row["draft_revision"]) != int(base_revision):
            raise RuntimeError(int(row["draft_revision"]))
        next_revision = int(base_revision) + 1
        metadata = document.get("metadata", {})
        conn.execute(
            """
            UPDATE reports SET title=?, author=?, draft_json=?, draft_revision=?,
              status='draft', updated_at=? WHERE report_id=?
            """,
            (
                str(metadata.get("title") or "未命名报告"),
                str(metadata.get("author") or "原力"),
                json.dumps(document, ensure_ascii=False),
                next_revision,
                now,
                report_id,
            ),
        )
    return get_draft(report_id)


__all__ = ["get_draft", "replace_draft"]
