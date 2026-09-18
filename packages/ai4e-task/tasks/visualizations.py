"""分配任务的可视化区域；不解释配置、不生成研究版本。"""

from pathlib import Path

from ..projects.project import open_project
from ..storage.layout import inside, task_dir
from .records import get_task


def visualization_storage(project: str | Path, task_id: str, *, write: bool = False) -> dict:
    """返回经过身份、归档和路径核验的任务区域，写入时才创建目录。"""
    project = Path(project).resolve()
    owner = open_project(project)
    record = get_task(project, task_id)
    writable = not bool(record.get("archived") or owner.get("archived"))
    if write and not writable:
        raise ValueError("visualization_task_archived")
    directory = task_dir(project, task_id)
    if not directory.is_relative_to(project) or not directory.is_dir():
        raise ValueError("visualization_task_directory_invalid")
    root = inside(directory, "visualizations")
    if write:
        root.mkdir(parents=True, exist_ok=True)
    return {
        "scope_id": f"{owner['id']}:{task_id}",
        "project_id": owner["id"],
        "task_id": task_id,
        "root": str(root),
        "writable": writable,
    }
