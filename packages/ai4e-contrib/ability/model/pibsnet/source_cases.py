"""Neumann与Advection原训练路径：参数样条、原初值赋值和逐点损失。

普通方程库仍表示物理方程；本组件不将参数导数冒称物理导数。
数据协议、采样和条件显式校验，历史物理导数产物必须重新准备。
"""

from functools import lru_cache

import torch
from torch import nn

from ai4e_core.abilities.constraint.physical import residual_loss
from ai4e_core.abilities.sampling.physical import sample_points

from . import advection_numerics as adv
from . import neumann_numerics as neu

PROTOCOLS = {
    "neumann_diffusion": "neumann-source-fp32-mt19937-v1",
    "advection": "advection-source-fp32-mt19937-v1",
}


def consume_neumann_initialization():
    """只重放原PINN/DeepONet构建时消耗的随机数；不维护或训练第二个模型。"""
    layers = [nn.Linear(3, 128), nn.Linear(128, 128), nn.Linear(128, 128), nn.Linear(128, 1)]
    for layer in layers:
        nn.init.xavier_normal_(layer.weight)
        nn.init.zeros_(layer.bias)
    for inputs, outputs in [(1, 128), (128, 128), (128, 128), (2, 128), (128, 128), (128, 128)]:
        nn.Linear(inputs, outputs)


class NeumannNet(neu.BSNetLoss):
    """原BSNetLoss结构，补充普通用户可调用的系数前向。"""

    def forward(self, parameters):
        """返回批量控制系数；与原forward_U相同。"""
        return self.forward_U(parameters)


def validate(config):
    """首期原案例支持全网格或标签网格子集；拒绝无实现的条件覆盖。"""
    cfg = config["model"]
    case = config["case"]
    expected = (
        {n: {"u": {"type": "zero_gradient"}} for n in ["left", "right"]}
        if case == "neumann_diffusion"
        else {}
    )
    if (
        cfg["boundary_conditions"] != expected
        or cfg["constraints"]["boundary_conditions"]["enforcement"] != "soft"
        or cfg["constraints"]["boundary_conditions"]["overrides"]
    ):
        raise ValueError("原Neumann/Advection组件不支持更换边界条件；特殊目标请注入用户step")
    if cfg["initial_conditions"]["u"] != {
        "value": "dataset_initial",
        "corner_policy": "initial_priority",
    }:
        raise ValueError("原案例初值必须来自dataset_initial")
    if cfg["hard_initial"] != (case == "advection"):
        raise ValueError("原Advection需要初始控制行插值；Neumann使用初值罚项")
    if any(
        v != {"method": "all"}
        for v in [cfg["sampling"]["initial"], *cfg["sampling"]["boundaries"].values()]
    ):
        raise ValueError("原案例初边界使用完整标签网格")
    if cfg["constraints"]["periodic_boundary_conditions"]["weight"] != 0:
        raise ValueError("原案例无额外周期罚项；特殊目标请注入用户step")
    if case == "advection" and cfg["constraints"]["initial_conditions"]["weight"] != 0:
        raise ValueError("原Advection不增加初值罚项")


def build(config):
    """保留原网络输出数和初始化顺序。"""
    validate(config)
    t, x = config["model"]["control_points"]
    h = config["model"]["hidden_dim"]
    if config["case"] == "neumann_diffusion":
        consume_neumann_initialization()
        return NeumannNet(t, x, h)
    return adv.BetaPhaseControlPointNet(x, t, h)


@lru_cache(maxsize=32)
def basis(case, controls, degree, count):
    """冻结原参数矩阵；不按物理域长度缩放。"""
    module = neu if case == "neumann_diffusion" else adv
    points, knots, values = module.BsKnots(controls, degree, count)
    first, second = module.BsKnots_derivatives(controls, degree, count, knots, points)
    return tuple(torch.tensor(v, dtype=torch.float32) for v in [values, first, second])


def prepare(sample, config):
    """独立准备网格身份、监督标签和原样条资产。"""
    validate(config)
    if sample.get("numerical_protocol") != PROTOCOLS[config["case"]]:
        raise ValueError("原案例数据协议不一致，请重新独立生成数据和准备产物")
    cfg = config["model"]
    sets = {}
    for name in ["supervised", "interior"]:
        sets[name] = sample_points(
            sample,
            cfg["sampling"][name],
            seed=cfg["sampling"]["seed"],
            name=name,
            supervised=name == "supervised",
        )
        if sets[name].get("indices") is None:
            raise ValueError("原参数样条组件只支持网格采样，不支持离网点")
    bases = [
        basis(config["case"], n, cfg["degree"], len(sample["axes"][axis]))
        for n, axis in zip(cfg["control_points"], sample["axis_names"], strict=True)
    ]
    return {"sample": sample, "sets": sets, "grid_bases": bases}


def predictions(model, prepared, config):
    """输出完整u和明确具名的参数导数，不隐式归一化。"""
    sample = prepared["sample"]
    p = sample["parameters"]
    parameter = next(model.parameters())
    t, x = [[a.to(parameter) for a in group] for group in prepared["grid_bases"]]
    if config["case"] == "neumann_diffusion":
        control = model(torch.tensor([[p["nu"]]], device=parameter.device, dtype=parameter.dtype))[
            0
        ]
    else:
        control = model(
            torch.tensor([[p["beta"]]], device=parameter.device, dtype=parameter.dtype),
            torch.tensor([[p["phase"]]], device=parameter.device, dtype=parameter.dtype),
        )
        adv.assign_first_row_direct(control, sample["u"][0].float().cpu().numpy())
        control = control[0]
    return {
        "u": t[0] @ control @ x[0].T,
        "parameter_t": t[1] @ control @ x[0].T,
        "parameter_x": t[0] @ control @ x[1].T,
        "parameter_xx": t[0] @ control @ x[2].T,
    }


def step(model, prepared, config):
    """原运算和归约顺序；权重仍由用户配置提供。"""
    values = predictions(model, prepared, config)
    u = values["u"]
    sample = prepared["sample"]
    cfg = config["model"]
    settings = cfg["constraints"]
    p = sample["parameters"]
    if config["case"] == "neumann_diffusion":
        residual = values["parameter_t"] - p["nu"] * values["parameter_xx"]
    else:
        beta = torch.tensor([[p["beta"]]], device=u.device, dtype=u.dtype)
        residual = values["parameter_t"] + beta * values["parameter_x"]
    data = u - sample["u"].to(u)
    losses = {}
    for name, r, key in [("pde", residual, "equations"), ("data", data, "supervision")]:
        group = "interior" if name == "pde" else "supervised"
        expected = (
            {"method": "all", "include_boundary": True}
            if group == "interior"
            else {"method": "all"}
        )
        if cfg["sampling"][group] != expected:
            r = r.flatten()[prepared["sets"][group]["indices"].to(u.device)]
        if config["case"] == "advection" and settings[key]["loss"] == "mse":
            # 原nn.MSELoss反向使用融合核，不能用square().mean()替换后声称逐值等价。
            if name == "data" and cfg["sampling"][group] == expected:
                losses[name] = nn.functional.mse_loss(
                    u, sample["u"].to(u), reduction=settings[key]["reduction"]
                )
            else:
                losses[name] = nn.functional.mse_loss(
                    r, torch.zeros_like(r), reduction=settings[key]["reduction"]
                )
        else:
            losses[name] = residual_loss(
                r, loss=settings[key]["loss"], reduction=settings[key]["reduction"]
            )

    total = (
        settings["equations"]["weight"] * losses["pde"]
        + settings["supervision"]["weight"] * losses["data"]
    )
    if config["case"] == "neumann_diffusion":
        target = sample["u"][0].to(u)
        losses["initial"] = residual_loss(
            u[0] - target,
            loss=settings["initial_conditions"]["loss"],
            reduction=settings["initial_conditions"]["reduction"],
        )
        left = values["parameter_x"][:, 0]
        right = values["parameter_x"][:, -1]
        losses["boundary"] = residual_loss(
            left,
            loss=settings["boundary_conditions"]["loss"],
            reduction=settings["boundary_conditions"]["reduction"],
        ) + residual_loss(
            right,
            loss=settings["boundary_conditions"]["loss"],
            reduction=settings["boundary_conditions"]["reduction"],
        )
        total = (
            total
            + settings["initial_conditions"]["weight"] * losses["initial"]
            + settings["boundary_conditions"]["weight"] * losses["boundary"]
        )
    else:
        with torch.no_grad():
            losses["initial"] = (u[0] - sample["u"][0].to(u)).square().mean()
            losses["periodic"] = (u[:, 0] - u[:, -1]).square().mean()
    return {"loss": total, "losses": losses}
