"""发现并执行一级模块迁移的公共执行器。

迁移文件归业务模块所有；本执行器只保证确定顺序和幂等登记。当前重构保留旧表，
后续新增Schema时再由模块显式注册迁移。
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from sqlite3 import Connection


@dataclass(frozen=True)
class Migration:
    """模块迁移描述，标识必须全局唯一且带模块名称。"""

    migration_id: str
    apply: Callable[[Connection], None]


def run_migrations(connection: Connection, migrations: Iterable[Migration]) -> None:
    """按标识顺序执行未登记迁移，失败时由外层事务统一回滚。"""

    connection.execute(
        "CREATE TABLE IF NOT EXISTS schema_migrations "
        "(migration_id TEXT PRIMARY KEY, applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)"
    )
    applied = {row[0] for row in connection.execute("SELECT migration_id FROM schema_migrations")}
    for migration in sorted(migrations, key=lambda item: item.migration_id):
        if migration.migration_id in applied:
            continue
        migration.apply(connection)
        connection.execute("INSERT INTO schema_migrations(migration_id) VALUES (?)", (migration.migration_id,))
