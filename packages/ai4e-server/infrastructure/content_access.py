"""只允许访问已登记根内文件，拒绝目录穿越和外逃符号链接。"""

import hashlib
from datetime import UTC, datetime
from pathlib import Path

import ai4e_task as task


def roots(service, project, task_id=None):
    """返回可见根；浏览器使用根身份，不传绝对路径。"""
    result = {"project": service.project(project)}
    result.update(
        {f"data{i}": Path(p).resolve() for i, p in enumerate(service.settings.data_roots)}
    )
    if task_id:
        result["task"] = Path(task.get_task(service.project(project), task_id)["directory"])
    return result


def resolve(service, project, root, relative="", task_id=None):
    """解析受控文件引用。"""
    if Path(relative).is_absolute():
        raise ValueError("relative_file_reference_required")
    base = roots(service, project, task_id)[root].resolve()
    path = (base / relative).resolve()
    if not path.is_relative_to(base):
        raise ValueError("path_outside_root")
    if any(p.startswith(".") for p in Path(relative).parts):
        raise ValueError("private_file")
    if not path.exists():
        raise FileNotFoundError(relative)
    return path


def revision(path):
    """内容摘要用于检查与提交前校验。"""
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def listing(service, project, root, relative="", task_id=None):
    """仅列一级目录，返回真实修改时间。"""
    path = resolve(service, project, root, relative, task_id)
    base = roots(service, project, task_id)[root].resolve()
    if not path.is_dir():
        raise ValueError("directory_required")
    result = []
    for p in sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name)):
        if p.name.startswith(".") or p.name == "__pycache__" or p.is_symlink():
            continue
        stat = p.stat()
        result.append(
            {
                "path": str(p.relative_to(base)),
                "name": p.name,
                "directory": p.is_dir(),
                "size": stat.st_size,
                "modified_at": datetime.fromtimestamp(stat.st_mtime, UTC).isoformat(),
            }
        )
    return result
