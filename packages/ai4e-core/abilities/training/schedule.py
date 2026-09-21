"""公开学习率调度：按名构造，绑定总有效更新步。"""

import math

import torch


def total_updates(epochs: int, samples: int, accumulate: int = 1) -> int:
    """按轮数、样本数和累积步计算有效更新次数。"""
    if epochs < 1 or samples < 1 or accumulate < 1:
        raise ValueError("轮数、样本数与累积步必须为正")
    return epochs * (samples // accumulate)


def build_scheduler(
    name,
    optimizer,
    *,
    total_updates: int,
    warmup_ratio: float = 0.05,
    min_lr: float = 1e-6,
    last_epoch: int = -1,
):
    """按名构造调度。缺总步数或非法种类失败，不包一层空的 ``step``。"""
    if total_updates is None or int(total_updates) < 1:
        raise ValueError("调度需要总有效更新步")
    kind = str(name).lower()
    steps = int(total_updates)
    peak = float(optimizer.param_groups[0]["lr"])
    if peak <= 0:
        raise ValueError("峰值学习率必须为正")
    if kind in {"constant", "none"}:
        return torch.optim.lr_scheduler.LambdaLR(optimizer, lambda _: 1.0, last_epoch=last_epoch)
    if kind not in {"warmup_cosine", "cosine"}:
        raise ValueError(f"未知调度种类: {name}")
    if not 0 <= float(warmup_ratio) < 1:
        raise ValueError("预热比例必须位于 [0,1)")
    if not math.isfinite(min_lr) or min_lr < 0 or min_lr > peak:
        raise ValueError("终点学习率必须有限且不超过峰值")
    warmup = int((steps - 1) * float(warmup_ratio)) if kind == "warmup_cosine" else 0
    floor = min_lr / peak

    def factor(step: int) -> float:
        if warmup and step < warmup:
            return (step + 1) / (warmup + 1)
        span = max(1, steps - warmup - 1)
        progress = min(1.0, max(0.0, (step - warmup) / span))
        return floor + (1.0 - floor) * 0.5 * (1.0 + math.cos(math.pi * progress))

    return torch.optim.lr_scheduler.LambdaLR(optimizer, factor, last_epoch=last_epoch)


class EpochBoundaryScheduler:
    """将每更新调用转换为真实轮次末尾推进，包含恢复游标。"""

    def __init__(self, scheduler, updates_per_epoch: int):
        if type(updates_per_epoch) is not int or updates_per_epoch < 1:
            raise ValueError("每轮更新数须为正整数")
        self.scheduler, self.updates_per_epoch, self.updates = scheduler, updates_per_epoch, 0

    def step(self):
        """只在完整轮次结束时推进底层调度器。"""
        self.updates += 1
        if self.updates % self.updates_per_epoch == 0:
            self.scheduler.step()

    def state_dict(self):
        """保存底层状态和更新游标。"""
        return {
            "updates": self.updates,
            "updates_per_epoch": self.updates_per_epoch,
            "scheduler": self.scheduler.state_dict(),
        }

    def load_state_dict(self, state):
        """轮次定义改变时拒绝恢复。"""
        if state["updates_per_epoch"] != self.updates_per_epoch:
            raise ValueError("恢复轮次边界不一致")
        self.scheduler.load_state_dict(state["scheduler"])
        self.updates = state["updates"]
