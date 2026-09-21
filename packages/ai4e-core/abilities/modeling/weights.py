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


def load_mapped_weights(model, state: dict, *, mapping: dict[str, str] | None = None):
    """显式键映射后严格加载参数及 buffer；冲突/缺失/形状错误先报错。"""
    mapping = mapping or {}
    if set(mapping) - set(state):
        raise ValueError("权重映射含不存在的来源键")
    converted = {}
    for key, value in state.items():
        target = mapping.get(key, key)
        if target in converted:
            raise ValueError(f"权重映射冲突: {target}")
        converted[target] = value
    expected = model.state_dict()
    if converted.keys() != expected.keys():
        raise ValueError(
            f"权重键不一致: missing={expected.keys() - converted.keys()}, extra={converted.keys() - expected.keys()}"
        )
    if any(converted[k].shape != expected[k].shape for k in expected):
        raise ValueError("权重形状不一致")
    return model.load_state_dict(converted, strict=True)
