"""研究者可修改的损失与派生误差，独立 post 核验固定数组。"""

import numpy as np

from ai4e_contrib.application.aero_cfd.geotransolver import predict
from ai4e_core.abilities.constraint.supervised import supervised


def l1_objective(model, batch, config):
    """选用 core 的 L1 比较，改变实际梯度。"""
    return supervised(
        predict(model, batch["inputs"]),
        batch["targets"],
        [{**term, "loss": "mae"} for term in config["model"]["supervision"]],
    )


def absolute_error(prediction, truth):
    """逐节点标量绝对误差，保持实体与单位。"""
    return (prediction - truth).abs()


def consume_error(sample):
    """只读固定误差、预测和真值，确认保存字段被下游真实消费。"""
    arrays = sample["fields"]
    value = arrays["surface.absolute_error"]
    expected = np.abs(arrays["surface.pressure.prediction"] - arrays["surface.pressure.truth"])
    np.testing.assert_array_equal(value, expected)
    return {"maximum": float(value.max()), "mean": float(value.mean()), "entities": len(value)}
