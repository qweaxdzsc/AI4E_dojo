"""Darcy 实际能力替换：平方相对误差及固定误差数组的独立消费。"""

import numpy as np

from ai4e_core.abilities.constraint.relative_norm import relative_norm


def squared_relative_loss(prediction, target):
    """逐样本相对 L2 平方改变优化目标，不改变模型接口。"""
    return relative_norm(prediction, target, reduction="none").square().mean()


def error_field(arrays):
    """保存物理空间有符号误差，附带明确轴及单位。"""
    return {"signed_error": arrays["prediction"] - arrays["target"]}, {
        "signed_error": {"units": "benchmark", "axes": ["sample", "time", "entity", "channel"]}
    }


def consume_error(arrays, descriptions):
    """独立 post 核对新增输出并给出最大绝对误差。"""
    np.testing.assert_array_equal(arrays["signed_error"], arrays["prediction"] - arrays["target"])
    if descriptions["signed_error"]["units"] != "benchmark":
        raise ValueError("误差单位不匹配")
    return {"max_abs_error": float(np.abs(arrays["signed_error"]).max())}
