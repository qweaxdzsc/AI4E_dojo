"""无业务含义的可视化内核、缓存和抽样原语测试。"""

import math

import pytest

from modules.visEngine import KernelCache, evenly_spaced_indices, scalar_range


def test_engine_cache_evicts_least_recently_used_value() -> None:
    """缓存到达容量后应淘汰最久未访问项。"""

    cache = KernelCache[int](capacity=2)
    cache.put("a", 1)
    cache.put("b", 2)
    assert cache.get("a") == 1
    cache.put("c", 3)
    assert cache.get("b") is None
    assert cache.get("c") == 3


def test_engine_numeric_primitives_cover_boundaries() -> None:
    """抽样覆盖首尾，标量范围忽略非有限值。"""

    indices = evenly_spaced_indices(11, 4)
    assert indices[0] == 0 and indices[-1] == 10
    assert scalar_range([math.nan, -2.0, 4.5, math.inf]) == (-2.0, 4.5)
    assert scalar_range([math.nan]) is None
    with pytest.raises(ValueError):
        evenly_spaced_indices(-1, 4)
