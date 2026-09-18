"""模型参数的指数移动平均，仅在有效优化器更新后推进。"""

import torch


class MovingAverage:
    """维护独立状态字典，不修改训练模型。"""

    def __init__(self, model, decay: float = 0.9999, *, buffer_policy: str = "average"):
        """从当前权重初始化影子状态。"""
        if not 0 <= decay < 1:
            raise ValueError("EMA 因子必须位于 [0,1)")
        if buffer_policy not in {"average", "copy"}:
            raise ValueError("EMA 缓冲策略必须为 average 或 copy")
        self.buffer_policy = buffer_policy
        self.parameter_names = set(dict(model.named_parameters()))
        self.decay = decay
        self.state = {k: v.detach().clone() for k, v in model.state_dict().items()}

    @torch.no_grad()
    def update(self, model):
        """浮点权重取指数平均，整型缓冲直接复制。"""
        for key, value in model.state_dict().items():
            if self.buffer_policy == "copy" and key not in self.parameter_names:
                self.state[key].copy_(value)
            elif value.is_floating_point() or value.is_complex():
                self.state[key].mul_(self.decay).add_(value, alpha=1 - self.decay)
            else:
                self.state[key].copy_(value)
