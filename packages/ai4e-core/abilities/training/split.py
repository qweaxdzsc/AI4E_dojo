"""预测与目标分流：缺键或多键发警告，不补默认值。"""

import warnings


def route(available: dict, expected: list[str], *, kind: str) -> dict:
    """按声明清单取字段；缺失或多余只警告，正权重空算仍由约束失败。"""
    names = list(expected)
    missing = [name for name in names if name not in available]
    extra = [name for name in available if name not in set(names)]
    if missing:
        warnings.warn(f"分流缺键({kind}): {missing}", stacklevel=2)
    if extra:
        warnings.warn(f"分流多键({kind}): {extra}", stacklevel=2)
    return {name: available[name] for name in names if name in available}
