"""严格形状的监督比较与可配置权重。"""

import math

from ai4e_core.abilities.constraint.compare import compare


def supervised(predictions: dict, targets: dict, objectives: list[dict]) -> dict:
    """计算独立监督项；缺字段、广播、空项和非有限权重均失败。

    每项可声明比较方法，未声明时使用均方误差。
    """
    if not objectives:
        raise ValueError("至少需要一条有效监督项")
    losses = {}
    total = None
    for objective in objectives:
        name = objective["name"]
        if name in losses:
            raise ValueError("监督项名称重复")
        weight = float(objective.get("weight", 1.0))
        if not math.isfinite(weight) or weight < 0:
            raise ValueError("损失权重必须有限且非负")
        pred, target = predictions[objective["prediction"]], targets[objective["target"]]
        losses[name] = compare(
            pred,
            target,
            objective.get("loss", "mse"),
            delta=objective.get("delta", 1.0),
        )
        total = weight * losses[name] if total is None else total + weight * losses[name]
    if not any(float(o.get("weight", 1)) > 0 for o in objectives):
        raise ValueError("至少一条监督项具有正权重")
    return {"loss": total, "losses": losses}


def supervised_mse(predictions: dict, targets: dict, objectives: list[dict]) -> dict:
    """监督均方误差别名；各分项按均方误差计算。"""
    return supervised(predictions, targets, [{**item, "loss": "mse"} for item in objectives])
