"""具名数组流统计；不读取样本目录、不解释训练分片或物理字段名。"""

from collections.abc import Iterable, Mapping

import numpy as np

from ai4e_core.base.events import traced

from .moments import accumulate_moments


@traced("多字段统计")
def fit_statistics(fields: Mapping[str, Iterable[np.ndarray]]) -> dict:
    """逐字段消费一次数组流，保留每个字段的总体矩与实体数。"""
    if not fields:
        raise ValueError("至少选择一个统计字段")
    return {name: accumulate_moments(stream) for name, stream in fields.items()}
