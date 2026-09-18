"""GenCP 干净条件覆盖及可选边界路径回填。"""

import torch

from ai4e_core.abilities.transform.flow_path import conditional_path


def clean_condition(state, condition, field, *, clean_neutron=True, clean_solid=True):
    """覆盖已声明的条件通道，不修改监督目标速度。"""
    result = state.clone()
    if field == "neutron" and clean_neutron and condition.shape[-1] == 2:
        result[..., 1:2] = condition[..., 1:2]
    if field == "solid" and clean_solid and condition.shape[-1] == 3:
        result[..., 2:3] = condition[..., 2:3]
    return result


def neutron_inpainting(states, time, *, field, noise, clean):
    """顺序更新中子后，以同一边界噪声的概率路径回填左列。"""
    if field != "neutron":
        return states
    t = torch.full((len(clean),), float(time), device=clean.device, dtype=clean.dtype)
    bc, _ = conditional_path(noise, clean, t, torch.randn_like(noise), sigma=0.0)
    result = dict(states)
    result["neutron"] = states["neutron"].clone()
    result["neutron"][:, :, :, 0:1, :] = bc[:, :, :, 0:1, :]
    return result
