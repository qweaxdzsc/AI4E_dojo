"""固定地热结果拼接为作者经济公式的输入，不重跑网络。"""

import torch

from .economy import evaluate_economy


def economic_table(record, arrays, *, temperature_threshold, capacity_factor):
    """输入二十年井级序列，输出与原程序列口径相同的经济表。"""
    pred = {key: torch.cat([a[key] for a in arrays], dim=0) for key in ["Pres", "Temp", "Qout"]}
    pred.update({key: [a[key][0] for a in arrays] for key in ["Twh", "Hwh", "Ewh", "Pinj"]})
    raw = {
        key: torch.cat([a[key] for a in arrays], dim=0)
        for key in ["spatial_params", "global_params"]
    }
    return evaluate_economy(pred, raw, record["statistics"], temperature_threshold, capacity_factor)
