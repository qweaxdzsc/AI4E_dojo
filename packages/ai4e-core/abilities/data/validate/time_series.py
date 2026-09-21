"""时间、字段与逐帧实体身份的一致性门禁。"""

import numpy as np


def validate_time_series(times, fields: dict, identities, *, expected_times=None):
    """校验 [T,N,...] 字段及 [N] 或 [T,N] 原身份；缺帧不能静默补齐。"""
    times, identities = np.asarray(times), np.asarray(identities)
    if (
        times.ndim != 1
        or not len(times)
        or not np.isfinite(times).all()
        or (np.diff(times) <= 0).any()
    ):
        raise ValueError("时间轴非法")
    if expected_times is not None and not np.array_equal(times, expected_times):
        raise ValueError("时间不一致或缺帧")
    ids = identities[0] if identities.ndim == 2 else identities
    if ids.ndim != 1 or len(np.unique(ids)) != len(ids):
        raise ValueError("实体身份非法或重复")
    if identities.ndim == 2 and (
        identities.shape != (len(times), len(ids)) or not np.all(identities == ids)
    ):
        raise ValueError("逐帧实体身份不一致")
    if not fields:
        raise ValueError("场不能为空")
    for name, value in fields.items():
        array = np.asarray(value)
        if array.shape[:2] != (len(times), len(ids)) or not np.isfinite(array).all():
            raise ValueError(f"时间/实体/有限值不一致: {name}")
