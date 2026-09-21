"""按显式排列分块预测和回贴；完整覆盖不代表全场一次前向等价。"""

from collections.abc import Callable

import torch


def predict_indexed(
    count: int,
    indices: torch.Tensor,
    *,
    chunk_size: int,
    operation: Callable[[torch.Tensor], torch.Tensor],
) -> tuple[torch.Tensor, dict]:
    """调用 operation(行索引) 返回 [块长,C]，交付原行序 CPU 张量与覆盖记录。

    在调用模型前检查排列完整性；失败不返回部分成功结果。模型模式由调用方管理。
    """
    if count < 1 or chunk_size < 1:
        raise ValueError("节点数和块大小须为正")
    if indices.ndim != 1 or indices.dtype not in (torch.int32, torch.int64):
        raise ValueError("排列须为一维整数")
    order = indices.detach().cpu().long()
    if len(order) != count or not torch.equal(order.sort().values, torch.arange(count)):
        raise ValueError("排列存在重复、遗漏或越界")
    output = None
    blocks = 0
    for selected in order.split(chunk_size):
        values = operation(selected).detach().cpu()
        if values.ndim != 2 or len(values) != len(selected) or not torch.isfinite(values).all():
            raise ValueError("预测形状不符或包含非有限值")
        if output is None:
            output = torch.empty((count, values.shape[1]), dtype=values.dtype)
        elif values.shape[1] != output.shape[1] or values.dtype != output.dtype:
            raise ValueError("预测块通道或精度发生变化")
        output[selected] = values
        blocks += 1
    return output, {"count": count, "written": count, "blocks": blocks, "chunk_size": chunk_size}
