"""SQLite连接、事务和迁移执行等无业务持久化原语。"""

from .sqlite import connect, transaction

__all__ = ["connect", "transaction"]
