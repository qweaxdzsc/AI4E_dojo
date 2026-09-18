"""GenCP 模型流时间、单场生成及耦合速度求值。"""

import torch

from ai4e_contrib.ability.transform.gencp.boundaries import clean_condition
from ai4e_contrib.ability.transform.gencp.state import join_fsi, joint_condition
from ai4e_core.abilities.transform.flow_path import conditional_path


def fsi_velocity(model, states, time, *, history):
    """求当前 FSI 联合状态的一个场速度。"""
    joint = join_fsi(states)
    t = torch.full((len(joint),), float(time), device=joint.device, dtype=joint.dtype)
    return model(joint, t, history, {})


def nt_velocity(model, states, time, *, field, condition, boundary):
    """条件映射后仅缩放网络时间；积分时间仍为 [0,1]。"""
    joint = joint_condition(condition(states, boundary), states[field])
    t = torch.full((len(joint),), float(time) * 1000, device=joint.device, dtype=joint.dtype)
    result = model(joint, t, None)
    width = states[field].shape[-1]
    if result.shape[-1] not in {width, joint.shape[-1]}:
        raise ValueError("生成速度通道不兼容")
    return result[..., -width:]


def single_field(
    model, condition, target, *, dataset, field, points=10, clean_neutron=True, clean_solid=True
):
    """保留原单场验证 N 个网格点、N-1 步；已知其他场条件允许使用。"""
    nt = dataset == "ntcouple"
    endpoint = joint_condition(condition, target) if nt else target
    initial = torch.randn_like(endpoint)
    state = initial.clone()
    times = torch.linspace(0, 1, points, device=state.device)
    dt = (times[1] - times[0]).item() if points > 1 else 1.0
    count = target.shape[-1] if nt else (3 if field == "fluid" else 1)
    for time in times[:-1]:
        t = time.expand(len(state)).to(state)
        reference, _ = conditional_path(initial, endpoint, t, torch.randn_like(initial), sigma=0.0)
        if nt:
            state = torch.cat((reference[..., :-count], state[..., -count:]), dim=-1)
            state = clean_condition(
                state, condition, field, clean_neutron=clean_neutron, clean_solid=clean_solid
            )
            vt = model(state, t * 1000, cond={})
            state[..., -count:] = state[..., -count:] + vt * dt
        elif field == "fluid":
            state = torch.cat((state[..., :3], reference[..., 3:4]), dim=-1)
            state[..., :3] = state[..., :3] + model(state, t, condition, {}) * dt
        else:
            state = torch.cat((reference[..., :3], state[..., 3:4]), dim=-1)
            state[..., 3:4] = state[..., 3:4] + model(state, t, condition, {}) * dt
    return state[..., -count:] if nt else state


def fsi_synchronous_step(states, time, dt, velocities, order, boundary=None):
    """保留参考每步未使用路径噪声的消耗，再执行同步更新。"""
    from ai4e_core.abilities.inference.coupled_steps import synchronous_euler_step

    torch.randn_like(join_fsi(states))
    return synchronous_euler_step(states, time, dt, velocities, order, boundary)
