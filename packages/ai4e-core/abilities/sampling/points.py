"""无放回抽点与独立可复现随机流，不绑定模型字段。"""

import hashlib

import torch


def point_indices(
    count: int,
    budget: int,
    *,
    seed: int,
    sample: str,
    operation: str,
    epoch: int = 0,
    keep_all: bool = False,
) -> torch.Tensor:
    """根据样本、操作和轮次独立取样；完整保留时维持原顺序。"""
    if count < 1 or budget < 1:
        raise ValueError("候选数与预算必须为正")
    if keep_all and count <= budget:
        return torch.arange(count)
    if budget > count:
        raise ValueError(f"候选不足: {count} < {budget}")
    digest = hashlib.sha256(f"{seed}:{sample}:{operation}:{epoch}".encode()).digest()
    generator = torch.Generator().manual_seed(int.from_bytes(digest[:8], "little"))
    return torch.randperm(count, generator=generator)[:budget]


def select_aligned(fields: dict[str, torch.Tensor], indices: torch.Tensor) -> dict:
    """使用同一下标联动选择同一实体集合上的所有字段。"""
    sizes = {value.shape[0] for value in fields.values()}
    if len(sizes) != 1:
        raise ValueError("同组字段行数不一致")
    return {name: value[indices.to(value.device)] for name, value in fields.items()}
