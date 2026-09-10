"""点场通道整理与显式零场派生，不绑定场名或领域。"""

import torch


def prepare_fields(
    fields: dict[str, torch.Tensor], *, zero_fields: dict[str, str] | None = None
) -> dict[str, torch.Tensor]:
    """将一维标量补为单通道，按来源的点数、设备和类型创建零场。"""
    prepared = {
        name: value.unsqueeze(1) if value.ndim == 1 else value for name, value in fields.items()
    }
    for target, source in (zero_fields or {}).items():
        if source not in prepared:
            raise ValueError(f"派生字段缺少点集来源: {source}")
        prepared[target] = prepared[source].new_zeros((len(prepared[source]), 1))
    return prepared
