"""渲染数据抽样和性能优化纯函数。"""


def evenly_spaced_indices(length: int, maximum: int) -> tuple[int, ...]:
    """返回覆盖首尾的均匀索引，避免高密数据直接压入渲染管线。"""

    if length < 0 or maximum <= 0:
        raise ValueError("length不能为负且maximum必须大于零")
    if length <= maximum:
        return tuple(range(length))
    step = (length - 1) / (maximum - 1) if maximum > 1 else 0
    return tuple(round(index * step) for index in range(maximum))
