"""物理时间历史/预测窗口；流时间与训练更新次数不进入此模块。"""


def window_count(length, history, horizon, *, interval=1, gap=0, stride=1):
    """按半开读取区间生成可用数量，保留端点契约。"""
    if min(length, history, horizon, interval, stride) < 1 or gap < 0:
        raise ValueError("时间窗口参数非法")
    return max(0, (length - (history + horizon) * interval - gap) // stride + 1)


def window_slices(index, length, history, horizon, *, interval=1, gap=0, stride=1):
    """返回历史、预测两个物理帧 slice；拒绝跨越轨迹末尾。"""
    count = window_count(length, history, horizon, interval=interval, gap=gap, stride=stride)
    if not 0 <= index < count:
        raise IndexError(f"窗口 {index} 超过 0..{count - 1}")
    start = index * stride
    end = start + history * interval
    return slice(start, end, interval), slice(end + gap, end + gap + horizon * interval, interval)
