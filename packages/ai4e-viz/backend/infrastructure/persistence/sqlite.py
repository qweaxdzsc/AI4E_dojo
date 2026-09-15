"""原生SQLite连接与事务基座。

业务模块通过自己的 Repository 调用本文件。这里统一WAL、外键和锁等待策略，
但不声明表、不保存业务SQL，也不决定事务何时提交。
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path


def connect(path: str | Path) -> sqlite3.Connection:
    """创建启用WAL、外键和busy timeout的SQLite连接。

    调用方拥有连接生命周期。父目录会按需创建；业务表和迁移仍由模块Repository负责。
    """

    database = Path(path)
    database.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database, timeout=30)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute("PRAGMA foreign_keys=ON")
    connection.execute("PRAGMA busy_timeout=30000")
    connection.execute("PRAGMA synchronous=NORMAL")
    return connection


@contextmanager
def transaction(path: str | Path) -> Iterator[sqlite3.Connection]:
    """提供显式提交和回滚的事务上下文。

    Repository在完整写用例内使用该上下文；异常会回滚并继续向上抛出，Application
    决定如何转换为业务错误。
    """

    connection = connect(path)
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
