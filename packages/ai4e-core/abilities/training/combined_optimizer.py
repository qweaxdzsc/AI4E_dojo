"""互斥参数的组合优化器；公开完整状态用于精确恢复。"""

import torch


class CombinedOptimizer(torch.optim.Optimizer):
    """按声明次序更新子优化器，调度器直接使用同一 param_groups。"""

    def __init__(self, optimizers):
        self.optimizers = list(optimizers)
        if not self.optimizers:
            raise ValueError("优化器不能为空")
        groups = [g for opt in self.optimizers for g in opt.param_groups]
        params = [p for g in groups for p in g["params"]]
        if len(set(map(id, params))) != len(params):
            raise ValueError("优化器参数重叠")
        super().__init__(params, {})
        self.param_groups = groups

    def step(self, closure=None):
        """闭包仅求值一次，再按顺序更新互斥参数。"""
        loss = None
        if closure is not None:
            with torch.enable_grad():
                loss = closure()
        for optimizer in self.optimizers:
            optimizer.step()
        return loss

    def zero_grad(self, set_to_none=True):
        """清空每个子优化器梯度。"""
        for optimizer in self.optimizers:
            optimizer.zero_grad(set_to_none=set_to_none)

    def state_dict(self):
        """保存子优化器类型与完整状态，拒绝恢复时错换算法。"""
        return {
            "types": [type(o).__module__ + "." + type(o).__qualname__ for o in self.optimizers],
            "optimizers": [o.state_dict() for o in self.optimizers],
        }

    def load_state_dict(self, state_dict):
        """恢复后重新关联参数组，避免调度器修改过期字典。"""
        if state_dict["types"] != self.state_dict()["types"] or len(
            state_dict["optimizers"]
        ) != len(self.optimizers):
            raise ValueError("组合优化器结构不匹配")
        for optimizer, state in zip(self.optimizers, state_dict["optimizers"], strict=True):
            optimizer.load_state_dict(state)
        self.param_groups = [g for o in self.optimizers for g in o.param_groups]
