"""索引缓存及调用方提供的几何/归一化身份验证。"""

from .array_manifest import read_arrays, save_arrays


def save_indexed_cache(path, indices, valid, *, identity: dict):
    """保存索引与有效性；身份由调用方显式声明。"""
    import numpy as np

    indices, valid = np.asarray(indices), np.asarray(valid)
    if (
        not identity
        or indices.shape != valid.shape
        or indices.dtype.kind not in "iu"
        or valid.dtype.kind != "b"
        or (indices < 0).any()
    ):
        raise ValueError("索引缓存或身份非法")
    return save_arrays(
        path,
        {"indices": indices, "valid": valid},
        kind="indexed-cache-v1",
        metadata={"identity": identity},
    )


def read_indexed_cache(path, *, identity: dict):
    """验证文件摘要和身份，不匹配时报错而非使用过期邻域。"""
    record, arrays = read_arrays(path, kind="indexed-cache-v1")
    if record["metadata"]["identity"] != identity:
        raise ValueError("索引缓存身份不匹配")
    return arrays["indices"], arrays["valid"]
