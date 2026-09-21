"""单次预测原语，不认识案例配置、数据集和输出目录。"""

from collections.abc import Callable
from typing import Any

from .execution import inference_execution


def predict(
    model, inputs: Any, *args: Any, operation: Callable, preserve_rng: bool = True, **kwargs
) -> Any:
    """调用注入的预测函数，禁止梯度并恢复模式；不改写函数的输出语义。"""
    with inference_execution(model, preserve_rng=preserve_rng):
        return operation(model, inputs, *args, **kwargs)


def named_array_batch(arrays, ids, *, device, names):
    """具名数组按同一索引取批，始终转换 float32 并保持字段对齐。"""
    import numpy as np
    import torch

    indices = np.asarray(ids)
    return {
        name: torch.from_numpy(np.array(arrays[name][indices], copy=True)).to(
            device=device, dtype=torch.float32
        )
        for name in names
    }


def predict_named_batches(model, count, batch, *, input_names, decode, batch_size):
    """包含不足整批的末批，恢复模型模式及随机状态，返回 CPU 张量。"""
    import torch

    if count < 1 or batch_size < 1:
        raise ValueError("预测数量/批量非法")
    values = []
    with inference_execution(model):
        for start in range(0, count, batch_size):
            item = batch(list(range(start, min(start + batch_size, count))))
            raw = model(**{name: item[name] for name in input_names})
            values.append(decode(raw, item).detach().cpu())
    return torch.cat(values)
