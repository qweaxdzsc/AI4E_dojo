"""只允许访问已登记根内文件，拒绝目录穿越和外逃符号链接。"""

import hashlib
from datetime import UTC, datetime
from pathlib import Path

import ai4e_task as task


def roots(service, project, task_id=None):
    """返回可见根；浏览器使用根身份，不传绝对路径。"""
    result = {
        "project": service.project(project),
        "workspace": Path(service.settings.root).resolve(),
    }
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


def listing_stamp(path):
    """列表用路径、修改时间和大小识别同一文件，不把检查点整份读进摘要。"""
    if path.is_symlink():
        raise ValueError("asset_symlink_forbidden")
    stat = path.stat()
    stamp = hashlib.sha256(
        f"{path.resolve()}\n{stat.st_mtime_ns}\n{stat.st_size}".encode()
    ).hexdigest()
    return stamp, stat.st_mtime_ns, stat.st_size


def revision(path):
    """文件与目录共用稳定摘要；目录按成员名和内容累计，拒绝符号链接。"""
    if path.is_symlink():
        raise ValueError("asset_symlink_forbidden")
    if path.is_dir():
        digest = hashlib.sha256()
        for member in sorted(path.rglob("*")):
            if member.is_symlink():
                raise ValueError("asset_symlink_forbidden")
            if member.is_file():
                digest.update(str(member.relative_to(path)).encode())
                digest.update(revision(member).encode())
        return digest.hexdigest()
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _listing_entry(path, base, directory=None):
    """一层列举的公共字段；目录与 .zarr 叶子共用修改时间。"""
    stat = path.stat()
    is_dir = path.is_dir() if directory is None else directory
    return {
        "path": str(path.relative_to(base)),
        "name": path.name,
        "directory": is_dir,
        "size": stat.st_size,
        "modified_at": datetime.fromtimestamp(stat.st_mtime, UTC).isoformat(),
    }


def listing(service, project, root, relative="", task_id=None, query=""):
    """仅列一级目录；有关键字时在当前层下按路径匹配，不进 .zarr。"""
    path = resolve(service, project, root, relative, task_id)
    base = roots(service, project, task_id)[root].resolve()
    if not path.is_dir():
        raise ValueError("directory_required")
    result = []
    if query:
        needle = query.casefold()
        for p in path.rglob("*"):
            if p.name.startswith(".") or p.name == "__pycache__" or p.is_symlink():
                continue
            if any(part.endswith(".zarr") for part in p.relative_to(path).parts[:-1]):
                continue
            rel = str(p.relative_to(base))
            if needle not in p.name.casefold() and needle not in rel.casefold():
                continue
            if p.is_dir() and p.suffix != ".zarr":
                continue
            result.append(_listing_entry(p, base, directory=False))
            if len(result) >= 200:
                break
        return result
    for p in sorted(path.iterdir(), key=lambda item: (not item.is_dir(), item.name)):
        if p.name.startswith(".") or p.name == "__pycache__" or p.is_symlink():
            continue
        result.append(_listing_entry(p, base, directory=p.is_dir() and p.suffix != ".zarr"))
    return result
