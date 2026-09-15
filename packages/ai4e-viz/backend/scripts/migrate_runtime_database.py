"""把旧运行库安全备份到统一 ``var/db`` 目录。

脚本使用SQLite Backup API合并WAL内容，绝不直接复制正在使用的数据库文件。默认拒绝
覆盖目标；迁移成功后保留旧数据库，以便目录重构出现问题时回退。
"""

from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE = REPOSITORY_ROOT / "backend" / "state" / "ai4e_vis.sqlite3"
DEFAULT_TARGET = REPOSITORY_ROOT / "var" / "db" / "ai4e_vis.sqlite3"


def backup_database(source: Path, target: Path) -> dict[str, object]:
    """将源库一致性备份到新位置并返回校验摘要。

    目标已经存在时抛出 ``FileExistsError``，防止迁移脚本静默覆盖用户数据。
    """

    source = source.expanduser().resolve()
    target = target.expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    if target.exists():
        raise FileExistsError(target)

    target.parent.mkdir(parents=True, exist_ok=True)
    source_uri = f"file:{source}?mode=ro"
    try:
        with sqlite3.connect(source_uri, uri=True) as source_connection:
            source_integrity = source_connection.execute("PRAGMA integrity_check").fetchone()[0]
            if source_integrity != "ok":
                raise RuntimeError(f"源数据库完整性检查失败: {source_integrity}")
            with sqlite3.connect(target) as target_connection:
                source_connection.backup(target_connection)

        with sqlite3.connect(target) as target_connection:
            target_integrity = target_connection.execute("PRAGMA integrity_check").fetchone()[0]
            table_count = target_connection.execute(
                "SELECT COUNT(*) FROM sqlite_master WHERE type = 'table'"
            ).fetchone()[0]
        if target_integrity != "ok":
            raise RuntimeError(f"目标数据库完整性检查失败: {target_integrity}")
        return {
            "source": str(source),
            "target": str(target),
            "integrity": target_integrity,
            "table_count": int(table_count),
            "bytes": target.stat().st_size,
        }
    except Exception:
        # 失败目标不是有效备份；删除它可保证下次重试不会被“目标存在”误阻塞。
        if target.exists():
            target.unlink()
        raise


def main() -> None:
    """解析命令行参数并打印迁移校验摘要。"""

    parser = argparse.ArgumentParser(description="安全迁移AI4E_Vis SQLite运行库")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--target", type=Path, default=DEFAULT_TARGET)
    args = parser.parse_args()
    print(backup_database(args.source, args.target))


if __name__ == "__main__":
    main()
