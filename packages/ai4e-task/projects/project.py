"""创建及打开本地项目，支持整体移动项目目录。"""

import os
import shutil
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from ..storage.database import initialize
from ..storage.files import read_json, write_json
from .models import Project


def create_project(path: str | Path, *, name: str | None = None) -> Project:
    """原子创建新项目；拒绝覆盖任何已有目录。"""
    path = Path(path).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(f".{path.name}.{uuid4().hex}.tmp")
    value = Project(
        id=uuid4().hex,
        name=name or path.name,
        schema_version=1,
        created_at=datetime.now(UTC).isoformat(),
    )
    # mkdir 是竞争创建的门禁；失败清理只操作本次创建的目录。
    path.mkdir()
    try:
        temp.mkdir()
        for folder in ("tasks", "shared", ".dojo"):
            (temp / folder).mkdir()
        initialize(temp)
        write_json(temp / "project.json", value)
        os.replace(temp, path)
    except BaseException:
        shutil.rmtree(temp, ignore_errors=True)
        path.rmdir()
        raise
    return value


def open_project(path: str | Path) -> Project:
    """校验项目描述与数据库存在，不隐式新建丢失的索引。"""
    root = Path(path).resolve()
    value = read_json(root / "project.json")
    if value.get("schema_version") != 1:
        raise ValueError("unsupported_project_version")
    if not (root / ".dojo/task.sqlite").is_file():
        raise FileNotFoundError("project_database_missing")
    return value


def recover_project(path: str | Path) -> dict:
    """持有项目写锁清理中断的创建操作；保留已登记运行和用户目录。"""
    from ..storage.database import transaction
    from ..storage.records import all_records

    root = Path(path).resolve()
    open_project(root)
    removed = []
    with transaction(root) as db:
        known = {t["id"] for t in all_records(db, "task")}
        for folder in (root / "tasks").iterdir():
            record = folder / "task.json"
            if record.is_file() and folder.name not in known:
                value = read_json(record)
                if value.get("id") == folder.name:
                    shutil.rmtree(folder)
                    removed.append(str(folder.relative_to(root)))
        for folder in (root / ".dojo").glob("task-*.tmp"):
            if folder.is_dir():
                shutil.rmtree(folder)
                removed.append(str(folder.relative_to(root)))
    return {"removed": removed}
