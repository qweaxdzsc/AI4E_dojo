"""显式命名轴转换，不根据形状猜测通道。"""


def transpose(value, source, target):
    """返回指定轴顺序的张量/数组，拒绝遗漏或重复轴。"""
    if (
        len(source) != value.ndim
        or len(set(source)) != len(source)
        or sorted(source) != sorted(target)
    ):
        raise ValueError("轴声明不是同一维度集合")
    order = tuple(source.index(axis) for axis in target)
    return (
        value.permute(order).contiguous()
        if hasattr(value, "permute")
        else value.transpose(order).copy()
    )
