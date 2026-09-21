"""双场地热预测、井级结果及固定数据输出；样本执行交给公开运行器。"""

import torch

from ai4e_core.abilities.constraint.geothermal import physical_loss
from ai4e_core.abilities.data.save.arrays import atomic_path


def predict_fields(networks, spatial, global_parameters, statistics):
    """只使用两个网络的预测；反归一化在监督裁剪之前，与原物理输入一致。"""
    fields = {}
    with torch.no_grad():
        for field, network in networks.items():
            value = torch.nan_to_num(
                network(spatial, global_parameters), nan=0.0, posinf=1e4, neginf=-1e4
            )
            fields[field] = value * statistics[field + "_std"] + statistics[field + "_mean"]
    if set(fields) != {"pres", "temp"}:
        raise ValueError("联合预测必须包含压力和温度")
    return fields


def predict_wells(fields, physical_parameters):
    """以预测压力和温度求解物理残差与井级量，不读取真实标签。"""
    with torch.no_grad():
        mass, energy, twh, hwh, pinj, ewh, qout = physical_loss(**physical_parameters).phy_loss(
            fields["pres"], fields["temp"]
        )
    return {"Twh": twh, "Hwh": hwh, "Pinj": pinj, "Ewh": ewh, "Qout": qout}, {
        "mass": float(mass),
        "energy": float(energy),
    }


def save_sample(path, result):
    """保存自包含单例，切断来源整批storage；拒绝非有限预测。"""

    def owned(value):
        if isinstance(value, torch.Tensor):
            if not torch.isfinite(value).all():
                raise ValueError("结果含非有限数值")
            return value.detach().cpu().clone()
        if isinstance(value, dict):
            return {k: owned(v) for k, v in value.items()}
        if isinstance(value, list):
            return [owned(v) for v in value]
        return value

    with atomic_path(path) as target:
        torch.save(owned(result), target)
