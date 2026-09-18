"""原始场的 GenCP 专属物理变换与训练条件构造，不读取文件。"""

import torch

from .normalization import nt_normalize


def fsi_physical_fields(arrays):
    """SDF 除一百后按 .02 mask 流体，保留 SDF 自身。"""
    sdf = arrays[3] / 100
    mask = torch.where(
        sdf > 0.02, torch.tensor(1.0, device=sdf.device), torch.tensor(0.0, device=sdf.device)
    )
    return torch.stack([value * mask for value in arrays[:3]] + [sdf], dim=-1)


def nt_sample_fields(values, field, *, decoupled):
    """已读取 T,H,W,C 数组转原训练条件、目标和物理真值。"""

    def normalized(name, kind):
        return nt_normalize(values[name], kind)

    if field == "neutron":
        bc = normalized("bc_neu" if decoupled else "bc", "neutron")
        fuel = normalized("fuel_neu" if decoupled else "fuel", "solid")
        fluid = (
            normalized("fluid_neu", "fluid")
            if decoupled
            else nt_normalize(values["fluid"][..., :1], "fluid")
        )
        physical = values["neu"]
        condition = torch.cat((torch.cat((fuel, fluid), dim=-2), bc.repeat(1, 1, 20, 1)), dim=-1)
    elif field == "solid":
        neu = (
            normalized("neu_fuel", "neutron")
            if decoupled
            else normalized("neu", "neutron")[:, :, :8, :]
        )
        fluid = (
            normalized("fluid_fuel", "fluid")
            if decoupled
            else nt_normalize(values["fluid"][:, :, :1, :1], "fluid")
        )
        physical = values["fuel"]
        left = nt_normalize(physical[:, :, :1, :], "solid")
        condition = torch.cat((neu, fluid.repeat(1, 1, 8, 1), left.repeat(1, 1, 8, 1)), dim=-1)
    elif field == "fluid":
        physical = values["fluid"]
        boundary = values["delta_fuel_fluid"] if decoupled else values["fuel"][:, :, -2:, :]
        condition = nt_normalize(boundary, "solid").repeat(1, 1, 6, 1)
    else:
        raise ValueError("未知核热场")
    return {"input": condition, "target": nt_normalize(physical, field), "physical": physical}
