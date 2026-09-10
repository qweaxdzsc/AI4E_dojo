"""收批原语：密集堆叠、稀疏拼接与局部索引偏移。"""

import torch


def stack(values: list[torch.Tensor]) -> torch.Tensor:
    """同形状数据堆叠，不自动填充。"""
    if not values or len({tuple(v.shape) for v in values}) != 1:
        raise ValueError("密集收批需要非空且同形状的数据")
    return torch.stack(values)


def concatenate_geometry(positions: list, indices: list) -> dict:
    """根据各样本实际点数偏移局部索引，并生成几何批次身份。"""
    if not positions or len(positions) != len(indices):
        raise ValueError("几何与索引批次数不一致")
    offset, shifted, batches = 0, [], []
    for batch, (pos, idx) in enumerate(zip(positions, indices, strict=True)):
        if pos.ndim != 2 or idx.ndim != 1 or idx.dtype != torch.long or not len(idx):
            raise ValueError("几何布局或索引类型错误")
        if idx.min() < 0 or idx.max() >= len(pos):
            raise ValueError("超节点索引越界")
        shifted.append(idx + offset)
        batches.append(torch.full((len(pos),), batch, dtype=torch.long, device=pos.device))
        offset += len(pos)
    return {
        "position": torch.cat(positions),
        "indices": torch.cat(shifted),
        "batch": torch.cat(batches),
    }


def to_device(value, device):
    """递归移动嵌套输入，保持浮点、整数和布尔类型，不隐式修正精度。"""
    import torch

    if isinstance(value, torch.Tensor):
        return value.to(device)
    if isinstance(value, dict):
        return {k: to_device(v, device) for k, v in value.items()}
    if isinstance(value, list):
        return [to_device(v, device) for v in value]
    if isinstance(value, tuple):
        return tuple(to_device(v, device) for v in value)
    return value
