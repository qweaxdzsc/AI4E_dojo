"""项目内模板目录，保存来源而不重复维护官方源码。"""

from pathlib import Path

from ..projects.project import open_project
from ..storage.database import transaction
from ..storage.records import listing, put
from ..storage.snapshots import digest, inventory


def register_template(project: str | Path, name: str, source: str | Path) -> dict:
    """登记本地模板及当前摘要；展开时使用并记录当前来源。"""
    open_project(project)
    path = Path(source).resolve()
    if not path.is_dir():
        raise NotADirectoryError(path)
    value = {"id": name, "source": str(path), "digest": digest(inventory(path))}
    with transaction(project) as db:
        put(db, "template", value)
    return value


def list_templates(project: str | Path) -> list[dict]:
    """列出已登记模板。"""
    return listing(project, "template")
