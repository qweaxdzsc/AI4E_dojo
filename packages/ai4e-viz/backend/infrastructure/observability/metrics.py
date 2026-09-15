"""轻量进程内指标接口；业务代码只上报名称和值，不依赖监控平台。"""

from __future__ import annotations

from collections import defaultdict

_COUNTERS: defaultdict[str, float] = defaultdict(float)


def increment(name: str, value: float = 1.0) -> None:
    """累加一个无敏感信息的技术指标。"""

    _COUNTERS[name] += value


def snapshot() -> dict[str, float]:
    """返回当前进程指标副本，防止调用方修改内部状态。"""

    return dict(_COUNTERS)
