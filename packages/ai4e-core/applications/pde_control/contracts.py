"""控制数据交接的兼容公开门面；实现由数组持久化能力复用。"""

from ai4e_core.abilities.data.save.array_manifest import digest, read_arrays, save_arrays

__all__ = ["digest", "read_arrays", "save_arrays"]
