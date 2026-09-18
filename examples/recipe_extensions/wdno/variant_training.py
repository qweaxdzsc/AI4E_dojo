"""复制到研究目录；只选择需要改变的训练函数，保存/恢复仍由框架负责。"""

import torch


def optimizer(model, options):
    """沿用训练学习率，研究 AdamW 权重衰减变体。"""
    return torch.optim.AdamW(model.parameters(), lr=options["lr"], weight_decay=0.01)


def scheduler(optimizer, options):
    """固定周期，延长总训练步数不暗改原调度曲线。"""
    return torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=10000)


def update(model, optimizer, value, objective, *, max_grad_norm):
    """单优化器完整精度梯度缩放示例；不叠加框架累积或混合精度。"""
    optimizer.zero_grad(set_to_none=True)
    loss = objective(model, value)
    if loss.ndim or not torch.isfinite(loss):
        raise FloatingPointError("目标必须是有限标量")
    loss.backward()
    for parameter in model.parameters():
        if parameter.grad is not None:
            parameter.grad.mul_(0.5)
    if max_grad_norm is not None:
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_grad_norm)
    optimizer.step()
    return float(loss.detach()), True
