"""物理场底层数值内核。

函数只处理数值数组，不认识任务、数据集、云图配置、Trame状态或HTTP请求。
"""

from collections.abc import Iterable
import math


def scalar_range(values: Iterable[float]) -> tuple[float, float] | None:
    """计算忽略NaN后的标量范围；空输入返回None。"""

    finite = [float(value) for value in values if math.isfinite(float(value))]
    if not finite:
        return None
    return min(finite), max(finite)
