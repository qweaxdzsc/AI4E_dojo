"""GenCP 单场训练目标；更新循环与优化器不进入此模块。"""

from ai4e_contrib.ability.transform.gencp.boundaries import clean_condition
from ai4e_contrib.ability.transform.gencp.state import joint_condition
from ai4e_core.abilities.constraint.flow_matching import velocity_mse
from ai4e_core.abilities.sampling.flow import flow_randomness
from ai4e_core.abilities.transform.flow_path import conditional_path


def objective(
    model, batch, *, dataset, field, sigma, clean_neutron=True, clean_solid=True, randomness=None
):
    """返回流速度 MSE；batch 已按场归一化为 B,T,H,W,C。"""
    condition, target = batch["input"], batch["target"]
    joint = joint_condition(condition, target) if dataset == "ntcouple" else target
    initial, time, noise = randomness or flow_randomness(joint)
    state, velocity = conditional_path(initial, joint, time, noise, sigma=sigma)
    if dataset == "ntcouple":
        state = clean_condition(
            state, condition, field, clean_neutron=clean_neutron, clean_solid=clean_solid
        )
        prediction = model(state, time * 1000, cond={})
        expected = velocity[..., -target.shape[-1] :]
    else:
        prediction = model(state, time, condition, {})
        expected = velocity[..., :3] if field == "fluid" else velocity[..., 3:4]
    return velocity_mse(prediction, expected)
