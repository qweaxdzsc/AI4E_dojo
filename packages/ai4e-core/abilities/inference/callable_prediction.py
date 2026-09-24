"""普通预测操作的批量执行，保留数组精度和多输出结构，不假定神经网络协议。"""

import numpy as np


def predict_batches(inputs, operation, *, batch_size=256):
    """按样本轴调用普通函数；数组或数组元组输出保持顺序、精度及尾批。

    operation负责模型自身的执行上下文。本入口不调用eval、不关闭梯度，
    也不将全局空间算子切成局部网格；inputs的第一轴必须是真实样本轴。
    """
    inputs = np.asarray(inputs)
    if inputs.ndim < 1 or not len(inputs) or type(batch_size) is not int or batch_size < 1:
        raise ValueError("预测样本与批量必须非空且为正")
    collected, signature = [], None
    for start in range(0, len(inputs), batch_size):
        chunk = inputs[start : start + batch_size]
        output = operation(chunk)
        values = output if isinstance(output, tuple) else (output,)
        arrays = tuple(np.asarray(value) for value in values)
        if not arrays or any(
            value.ndim < 1
            or len(value) != len(chunk)
            or value.dtype.kind not in "biufc"
            or not np.isfinite(value).all()
            for value in arrays
        ):
            raise ValueError("预测输出须为有限数组且保留样本轴")
        current = (isinstance(output, tuple), tuple((a.shape[1:], a.dtype.str) for a in arrays))
        if signature is not None and current != signature:
            raise ValueError("预测分批输出结构、形状或精度变化")
        signature = current
        # 普通预测器可能复用工作缓冲；跨批保留独立快照，不能收集别名视图。
        collected.append(tuple(np.array(value, copy=True) for value in arrays))
    joined = tuple(
        np.concatenate([part[i] for part in collected]) for i in range(len(collected[0]))
    )
    return joined if signature[0] else joined[0]
