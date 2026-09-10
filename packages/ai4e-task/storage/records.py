"""管理记录的具体持久化；不决定任务或版本规则。"""

import json
import sqlite3
from pathlib import Path

from .database import transaction


def put(db: sqlite3.Connection, kind: str, value: dict, *, replace: bool = False) -> None:
    """插入记录，更新时须显式指定 replace。"""
    sql = "INSERT OR REPLACE" if replace else "INSERT"
    db.execute(
        f"{sql} INTO records(kind,id,body) VALUES (?,?,?)",
        (kind, value["id"], json.dumps(value, ensure_ascii=False, allow_nan=False)),
    )


def get(db: sqlite3.Connection, kind: str, identity: str) -> dict:
    """按种类和稳定 ID 查询，不存在时明确报错。"""
    row = db.execute("SELECT body FROM records WHERE kind=? AND id=?", (kind, identity)).fetchone()
    if row is None:
        raise KeyError(f"not_found: {kind}/{identity}")
    return json.loads(row[0])


def all_records(db: sqlite3.Connection, kind: str) -> list[dict]:
    """读取某一类记录。"""
    return [
        json.loads(row[0])
        for row in db.execute("SELECT body FROM records WHERE kind=? ORDER BY rowid", (kind,))
    ]


def fetch(project: str | Path, kind: str, identity: str) -> dict:
    """只读查询门面。"""
    with transaction(project) as db:
        return get(db, kind, identity)


def listing(project: str | Path, kind: str) -> list[dict]:
    """只读列表门面。"""
    with transaction(project) as db:
        return all_records(db, kind)


def replay(db, key: str | None, fingerprint: str) -> dict | None:
    """核对幂等键的请求摘要，不同请求复用同一键时报冲突。"""
    if key is None:
        return None
    row = db.execute("SELECT fingerprint,kind,id FROM operations WHERE key=?", (key,)).fetchone()
    if row is None:
        return None
    if row[0] != fingerprint:
        raise ValueError("idempotency_conflict")
    return get(db, row[1], row[2])


def remember(db, key: str | None, fingerprint: str, kind: str, identity: str) -> None:
    """事务内登记已提交操作。"""
    if key is not None:
        db.execute("INSERT INTO operations VALUES (?,?,?,?)", (key, fingerprint, kind, identity))
