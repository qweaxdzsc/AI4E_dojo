"""安全地在运行根目录与相对 ``storage_key`` 之间转换。"""

from __future__ import annotations

from pathlib import Path, PurePosixPath

from infrastructure.config import runtime_paths


class StoragePathError(ValueError):
    """存储键包含绝对路径、父级逃逸或越过运行根目录时抛出。"""


def resolve_storage_key(storage_key: str) -> Path:
    """将数据库中的相对存储键解析为受控绝对路径。

    该校验是文件服务的安全边界：即使数据库内容被意外修改，也不能读取运行根目录
    之外的文件。
    """

    key = PurePosixPath(storage_key)
    if key.is_absolute() or ".." in key.parts or not key.parts:
        raise StoragePathError(f"非法 storage_key: {storage_key!r}")
    root = runtime_paths().root
    resolved = (root / Path(*key.parts)).resolve()
    if root != resolved and root not in resolved.parents:
        raise StoragePathError(f"storage_key 越过运行根目录: {storage_key!r}")
    return resolved


def storage_key_for(path: str | Path) -> str:
    """把运行目录内的文件转换为POSIX相对存储键。"""

    root = runtime_paths().root
    resolved = Path(path).resolve()
    try:
        return resolved.relative_to(root).as_posix()
    except ValueError as exc:
        raise StoragePathError(f"文件不属于运行根目录: {resolved}") from exc
