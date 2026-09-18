"""PI-BSNet 公开组件：准备、场计算及案例原生 PyTorch 损失函数。"""

import importlib

import torch

from ai4e_contrib.ability.constraint.equations import (
    advection,
    burgers,
    convection_diffusion,
    diffusion,
)
from ai4e_contrib.application.parametric_pde import pibsnet as preparation_adapter
from ai4e_core.abilities.constraint.physical import boundary_residual, residual_loss
from ai4e_core.abilities.sampling.physical import grid_points, periodic_points, sample_points

from . import source_cases, trapezoid
from .model import PIBSNet, evaluate_fields
from .spline import prepare_grid, prepare_points

# 声明影响物理目标和点集的公共依赖，以便准备/恢复发现跨目录源码变化。
SOURCE_MODULES = (
    "ai4e_contrib.ability.constraint.equations",
    "ai4e_core.abilities.constraint.physical",
    "ai4e_core.abilities.sampling.physical",
    "ai4e_core.abilities.geometry.parametric",
    "ai4e_core.abilities.transform.trapezoid",
)

PARAMETERS = {
    "convection_diffusion": ["lam", "a"],
    "neumann_diffusion": ["nu"],
    "advection": ["beta", "phase"],
    "burgers": ["mu", "m"],
    "diffusion_trapezoid": ["a"],
}


def build(config):
    """按已验证声明构建唯一模型；不启动优化器或运行会话。"""
    if config["case"] in source_cases.PROTOCOLS:
        return source_cases.build(config)
    if config["case"] == "diffusion_trapezoid":
        return trapezoid.build(config)
    model = config["model"]
    hard = {}
    if model["constraints"]["boundary_conditions"]["enforcement"] == "hard":
        for name, fields in model["boundary_conditions"].items():
            condition = fields["u"]
            if condition["type"] != "fixed_value" or not isinstance(
                condition["value"], (int, float)
            ):
                raise ValueError("PI-BSNet 硬边界仅支持标量 fixed_value")
            hard[name] = condition["value"]
    return PIBSNet(
        PARAMETERS[config["case"]],
        model["control_points"],
        hidden_dim=model["hidden_dim"],
        hard_boundaries=hard,
    )


def _initial(sample, points):
    """案例初值定义；优先独立解析表达式，梯形边界覆盖由配置显式处理。"""
    x = points[:, -1]
    p, case = sample["parameters"], sample["case"]
    if case == "neumann_diffusion":
        return torch.cos(torch.pi * x)
    if case == "advection":
        return torch.sin(2 * torch.pi * x + p["phase"])
    if case == "burgers":
        return torch.exp(-((x - p["m"]) ** 2) / 2)
    return torch.zeros_like(x)


def _target(value, points, sample):
    """计算显式目标函数；普通用户函数接收物理坐标与实例参数。"""
    if isinstance(value, dict):
        module, name = value["function"].rsplit(".", 1)
        return getattr(importlib.import_module(module), name)(points, sample["parameters"])
    return value


def prepare(sample, config):
    """准备冻结点集、标签及样条矩阵；不修改用户配置。"""
    if config["case"] in source_cases.PROTOCOLS:
        return source_cases.prepare(sample, config)
    if config["case"] == "diffusion_trapezoid":
        return trapezoid.prepare(sample, config)
    cfg = config["model"]
    sampling = cfg["sampling"]
    sets = {}
    for name, supervised in (("supervised", True), ("interior", False)):
        sets[name] = sample_points(
            sample, sampling[name], seed=sampling["seed"], name=name, supervised=supervised
        )
    sets["initial"] = sample_points(
        sample, sampling["initial"], seed=sampling["seed"], name="initial", initial=True
    )
    # 不连续初边界在边界点以 BC 为准，IC 不重复评价交角。
    if cfg["initial_conditions"]["u"].get("corner_policy") == "boundary_priority":
        initial = sets["initial"]
        keep = torch.ones(len(initial["points"]), dtype=torch.bool)
        for axis, name in enumerate(sample["axis_names"][1:], 1):
            lo, hi = sample["bounds"][name]
            keep &= (initial["points"][:, axis] > lo) & (initial["points"][:, axis] < hi)
        for key in ("points", "physical_points", "indices"):
            if initial.get(key) is not None:
                initial[key] = initial[key][keep]
        if not keep.any():
            raise ValueError("初值采样移除冲突交角后为空")
    initial_value = cfg["initial_conditions"]["u"]["value"]
    sets["initial"]["target"] = (
        _initial(sample, sets["initial"]["points"])
        if initial_value == "dataset_initial"
        else _target(initial_value, sets["initial"]["physical_points"], sample)
    )
    for boundary in cfg["boundary_conditions"]:
        sets[f"boundary/{boundary}"] = sample_points(
            sample,
            sampling["boundaries"][boundary],
            seed=sampling["seed"],
            name=f"boundary/{boundary}",
            boundary=boundary,
        )
    for name, condition in cfg["periodic_boundary_conditions"].items():
        sets[f"periodic/{name}"] = periodic_points(
            sample,
            sampling["periodic_pairs"][name],
            seed=sampling["seed"],
            name=name,
            boundaries=condition["boundaries"],
        )
    for value in sets.values():
        if value.get("indices") is None:
            value["bases"] = prepare_points(sample, value["points"], cfg)
        if "paired_points" in value:
            value["paired_bases"] = prepare_points(sample, value["paired_points"], cfg)
    return {"sample": sample, "sets": sets, "grid_bases": prepare_grid(sample, cfg)}


def predictions(model, prepared, config):
    """公开完整场求值，保持数组轴顺序；返回全部物理导数。"""
    if config["case"] in source_cases.PROTOCOLS:
        return source_cases.predictions(model, prepared, config)
    if config["case"] == "diffusion_trapezoid":
        return trapezoid.predictions(model, prepared, config)
    sample = prepared["sample"]
    points = grid_points(sample).reshape(*sample["u"].shape, len(sample["axis_names"]))
    return evaluate_fields(
        model,
        sample,
        prepared["grid_bases"],
        points=points,
        grid=True,
        hard_initial=config["model"]["hard_initial"],
    )


def _values(model, prepared, group, config, grid):
    sample = prepared["sample"]
    if group.get("indices") is not None:
        return {
            name: value.flatten()[group["indices"].to(value.device)] for name, value in grid.items()
        }
    return evaluate_fields(
        model,
        sample,
        group["bases"],
        points=group["points"],
        hard_initial=config["model"]["hard_initial"],
    )


def equation(case, values, parameters, *, points=None):
    """用普通函数绑定本案例残差；用户可通过训练步入口替换。"""
    v, p = values, parameters
    if case == "convection_diffusion":
        return convection_diffusion(
            u_t=v["u_t"], u_x=v["u_x"], u_xx=v["u_xx"], velocity=-p["lam"], diffusivity=0.5
        )
    if case == "neumann_diffusion":
        return diffusion(u_t=v["u_t"], u_xx=v["u_xx"], diffusivity=p["nu"])
    if case == "advection":
        return advection(u_t=v["u_t"], u_x=v["u_x"], velocity=p["beta"])
    if case == "burgers":
        return burgers(
            u=v["u"],
            u_t=v["u_t"],
            u_x=v["u_x"],
            u_xx=v["u_xx"],
            convection_coefficient=p["mu"],
            viscosity=p["nu"],
        )
    if case == "diffusion_trapezoid":
        # 论文 Appendix D.3 Eq.(84) 明确使用去掉交叉项的近似物理损失。
        # 完整物理导数仍由模型输出，此通用函数不代表选定梯形组件的参数空间训练导数。
        if points is None:
            raise ValueError("梯形近似方程需要显式参考坐标")
        width = 2 - points[:, 1].to(v["u_t"])
        return diffusion(
            u_t=v["u_t"],
            u_xx=v["u_xixi"] / width.square(),
            u_yy=p["a"] * v["u_etaeta"],
            diffusivity=0.5,
        )
    raise ValueError(f"未知方程: {case}")


def step(model, prepared, config):
    """原生 PyTorch 单实例训练计算；损失/梯度聚合交给现有训练循环。"""
    if config["case"] in source_cases.PROTOCOLS:
        return source_cases.step(model, prepared, config)
    if config["case"] == "diffusion_trapezoid":
        return trapezoid.step(model, prepared, config)
    sample, groups = prepared["sample"], prepared["sets"]
    cfg = config["model"]
    constraints = cfg["constraints"]
    grid = predictions(model, prepared, config)
    losses, weighted = {}, []

    def add(name, residual, settings, *, monitor=False):
        raw = residual_loss(residual, loss=settings["loss"], reduction=settings["reduction"])
        losses[name] = raw
        if not monitor:
            weighted.append(settings["weight"] * raw)

    values = _values(model, prepared, groups["interior"], config, grid)
    add(
        "pde",
        equation(sample["case"], values, sample["parameters"], points=groups["interior"]["points"]),
        constraints["equations"],
    )
    data = _values(model, prepared, groups["supervised"], config, grid)["u"]
    add("data", data - groups["supervised"]["target"].to(data), constraints["supervision"])
    initial = _values(model, prepared, groups["initial"], config, grid)["u"]
    target = groups["initial"]["target"]
    target = target.to(initial) if isinstance(target, torch.Tensor) else target
    add("initial", initial - target, constraints["initial_conditions"], monitor=cfg["hard_initial"])
    for name, condition in cfg["boundary_conditions"].items():
        group = groups[f"boundary/{name}"]
        v = _values(model, prepared, group, config, grid)
        gradient = torch.stack([v["u_x"]] + ([v["u_y"]] if "u_y" in v else []), -1)
        condition = condition["u"]
        target = condition.get("value", condition.get("gradient"))
        if isinstance(target, dict):
            target = _target(target, group["physical_points"].to(v["u"]), sample)
        residual = boundary_residual(
            value=v["u"],
            gradient=gradient,
            normals=group["normals"].to(gradient),
            condition=condition,
            target=target,
        )
        settings = constraints["boundary_conditions"]
        specific = {**settings, **settings.get("overrides", {}).get(name, {}).get("u", {})}
        add(f"boundary/{name}", residual, specific, monitor=settings["enforcement"] == "hard")
    for name in cfg["periodic_boundary_conditions"]:
        group = groups[f"periodic/{name}"]
        left = _values(model, prepared, group, config, grid)["u"]
        right = evaluate_fields(
            model,
            sample,
            group["paired_bases"],
            points=group["paired_points"],
            hard_initial=cfg["hard_initial"],
        )["u"]
        add(f"periodic/{name}", left - right, constraints["periodic_boundary_conditions"])
    return {"loss": sum(weighted), "losses": losses}


preparation_parameters = preparation_adapter.preparation_parameters
