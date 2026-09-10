"""初始状态字典加载与参数冻结，完整续训由训练层负责。"""

import torch


def initialize_weights(model, *, path=None, freeze: list[str] | None = None):
    """严格加载权重并按参数前缀冻结；无法匹配的前缀拒绝。"""
    if path:
        state = torch.load(path, map_location="cpu", weights_only=True)
        model.load_state_dict(state, strict=True)
    for prefix in freeze or []:
        matched = [
            p for n, p in model.named_parameters() if n == prefix or n.startswith(prefix + ".")
        ]
        if not matched:
            raise ValueError(f"冻结前缀没有匹配参数: {prefix}")
        for parameter in matched:
            parameter.requires_grad_(False)
    if not any(p.requires_grad for p in model.parameters()):
        raise ValueError("没有可训练参数")
