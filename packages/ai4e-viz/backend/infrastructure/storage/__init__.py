"""文件对象、相对存储键和清理策略的公共基础设施。"""

from .pathResolver import StoragePathError, resolve_storage_key

__all__ = ["StoragePathError", "resolve_storage_key"]
