"""实验文件读写、摘要与不跨根的路径解析。"""

import hashlib
import json
from pathlib import Path


def digest(path):
    """返回文件 SHA-256；逐块读取，不反序列化科学产物。"""
    result = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def read_json(path):
    """读取明确指定的 JSON 文件。"""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, value):
    """原子替换 JSON；拒绝 NaN/Infinity，保留中文。"""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".pending")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
    temporary.replace(path)


def inside(root, relative):
    """解析实验内相对路径；拒绝绝对路径、父目录及软链接越界。"""
    root, relative = Path(root).resolve(), Path(relative)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"必须使用根内相对路径: {relative}")
    result = (root / relative).resolve()
    if not result.is_relative_to(root):
        raise ValueError(f"路径越界: {relative}")
    return result


def inventory(root):
    """冻结普通文件清单；软链接全部拒绝，防止跨组引用。"""
    root = Path(root)
    result = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"材料不能包含软链接: {path}")
        if path.is_file():
            result[path.relative_to(root).as_posix()] = digest(path)
    return result
