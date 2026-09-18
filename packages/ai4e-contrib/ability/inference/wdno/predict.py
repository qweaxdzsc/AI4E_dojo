"""普通权重基础预测与小波物理恢复。"""

import torch

from ai4e_contrib.ability.transform.wdno.burgers import conditions, decode


@torch.no_grad()
def predict(model, u: torch.Tensor, f: torch.Tensor, *, batch_index: int) -> torch.Tensor:
    """保留原评价的逐批 CPU seed 和固定 MPS seed。"""
    device = next(model.parameters()).device
    torch.manual_seed(batch_index)
    if device.type == "mps":
        torch.mps.manual_seed(0)
    initial, force = conditions(u, f)
    model.eval()
    return decode(
        model.sample(batch_size=len(u), u_init=initial.to(device), f=force.to(device))
    ).cpu()
