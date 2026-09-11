"""服务自有项目位置索引与报告记录，不访问 task 数据库。"""

import json
import sqlite3
from pathlib import Path


class Store:
    """每次操作独立连接，支持服务重启。"""

    def __init__(self, root: Path):
        root.mkdir(parents=True, exist_ok=True)
        self.path = root / "server.sqlite"
        with self.connect() as db:
            version = db.execute("PRAGMA user_version").fetchone()[0]
            if version not in (0, 1):
                raise ValueError("unsupported_server_database_version")
            db.execute("PRAGMA user_version=1")
            db.execute(
                "CREATE TABLE IF NOT EXISTS documents(kind TEXT,id TEXT,body TEXT,PRIMARY KEY(kind,id))"
            )

    def connect(self):
        """打开服务数据库。"""
        return sqlite3.connect(self.path, timeout=30)

    def put(self, kind, identity, value):
        """保存服务自有记录。"""
        with self.connect() as db:
            db.execute(
                "INSERT OR REPLACE INTO documents VALUES (?,?,?)",
                (kind, identity, json.dumps(value, ensure_ascii=False)),
            )
        return value

    def get(self, kind, identity):
        """读取存在的记录。"""
        with self.connect() as db:
            row = db.execute(
                "SELECT body FROM documents WHERE kind=? AND id=?", (kind, identity)
            ).fetchone()
        if row is None:
            raise KeyError(identity)
        return json.loads(row[0])

    def list(self, kind):
        """列出同类服务记录。"""
        with self.connect() as db:
            return [
                json.loads(x[0])
                for x in db.execute(
                    "SELECT body FROM documents WHERE kind=? ORDER BY rowid", (kind,)
                )
            ]

    def compare_and_swap(self, kind, identity, value, *, expected_revision):
        """同一事务核对修订并保存，避免两个编辑者静默覆盖。"""
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute(
                "SELECT body FROM documents WHERE kind=? AND id=?", (kind, identity)
            ).fetchone()
            if row is None:
                raise KeyError(identity)
            if json.loads(row[0]).get("revision") != expected_revision:
                raise ValueError(kind + "_revision_conflict")
            db.execute(
                "UPDATE documents SET body=? WHERE kind=? AND id=?",
                (json.dumps(value, ensure_ascii=False), kind, identity),
            )
        return value
