"""项目与任务的目录定位；所有相对名称均检查越界。"""

from pathlib import Path


def inside(root: str | Path, relative: str) -> Path:
    """定位根内非空相对路径，拒绝绝对路径、父路径与符号链接越界。"""
    root = Path(root).resolve()
    rel = Path(relative)
    if not relative or rel.is_absolute() or ".." in rel.parts or str(rel) == ".":
        raise ValueError(f"invalid_path: {relative}")
    target = (root / rel).resolve()
    if not target.is_relative_to(root) or target == root:
        raise ValueError(f"path_escape: {relative}")
    return target


def task_dir(project: str | Path, task_id: str) -> Path:
    """取得任务根目录。"""
    return inside(Path(project) / "tasks", task_id)
