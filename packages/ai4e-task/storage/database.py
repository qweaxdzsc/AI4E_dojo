"""SQLite 管理记录；写事务串行化跨文件发布操作。"""

import sqlite3
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def transaction(project: str | Path):
    """打开项目数据库，失败回滚；调用者在事务内发布文件引用。"""
    path = Path(project) / ".dojo/task.sqlite"
    if not path.exists():
        raise FileNotFoundError(f"project_database_missing: {path}")
    db = sqlite3.connect(path, timeout=30)
    try:
        if db.execute("PRAGMA user_version").fetchone()[0] != 1:
            raise ValueError("unsupported_database_version")
        db.execute("PRAGMA foreign_keys=ON")
        db.execute("BEGIN IMMEDIATE")
        yield db
        db.commit()
    except BaseException:
        db.rollback()
        raise
    finally:
        db.close()


def initialize(project: Path) -> None:
    """创建初版表结构；未知 schema 版本拒绝访问。"""
    path = project / ".dojo/task.sqlite"
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    try:
        version = db.execute("PRAGMA user_version").fetchone()[0]
        if version not in (0, 1):
            raise ValueError("unsupported_database_version")
        db.execute(
            "CREATE TABLE IF NOT EXISTS records (kind TEXT NOT NULL, id TEXT NOT NULL, body TEXT NOT NULL, PRIMARY KEY(kind,id))"
        )
        db.execute(
            "CREATE TABLE IF NOT EXISTS operations (key TEXT PRIMARY KEY, fingerprint TEXT NOT NULL, kind TEXT NOT NULL, id TEXT NOT NULL)"
        )
        db.execute("PRAGMA user_version=1")
        db.commit()
    finally:
        db.close()
