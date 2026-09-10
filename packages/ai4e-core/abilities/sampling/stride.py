"""跨步分块与点序恢复；数据字段始终共用原始点下标。"""

import numpy as np


def indices(count: int, parts: int, part: int, *, stride: int = 1, offset: int = 0):
    """生成一个互补分块内的原始点下标，可再做跨步抽稀。"""
    if count < 1 or parts < 1 or not 0 <= part < parts:
        raise ValueError("点数、分块数或块下标不合法")
    if stride < 1 or not 0 <= offset < stride:
        raise ValueError("抽稀步长或起点不合法")
    return np.arange(part, count, parts, dtype=np.int64)[offset::stride]


def reconstruct(parts: list[np.ndarray], point_count: int) -> np.ndarray:
    """验证每块形状后按原点身份回填，禁止缺块或重复覆盖。"""
    if not parts or point_count < 1:
        raise ValueError("恢复需要非空分块与正点数")
    output = np.empty((point_count, *parts[0].shape[1:]), dtype=parts[0].dtype)
    for part, values in enumerate(parts):
        target = indices(point_count, len(parts), part)
        if values.shape != (len(target), *output.shape[1:]):
            raise ValueError(f"分块 {part} 形状错误: {values.shape}")
        if values.dtype != output.dtype or not np.isfinite(values).all():
            raise ValueError(f"分块 {part} 类型不一致或含非有限数值")
        output[target] = values
    return output
