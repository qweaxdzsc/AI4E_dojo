"""显式坐标空间声明校验；不从场单位、坐标值或名称猜测。"""


def coordinate_space(value):
    """返回独立的 id/unit 声明；缺失保持未知，半声明或额外键拒绝。"""
    if value is None:
        return None
    if not isinstance(value, dict) or set(value) != {"id", "unit"}:
        raise ValueError("coordinate_space 必须同时声明 id 和 unit")
    if any(not isinstance(v, str) or not v.strip() or v != v.strip() for v in value.values()):
        raise ValueError("coordinate_space.id/unit 必须为非空无首尾空白字符串")
    return dict(value)
