"""选定十实例梯形 PI-BSNet：原数值行为的模型组件，不含训练循环。

系数内部使用 t、xi、eta，场与数据使用 t、eta、xi。原参数空间导数和
近似 PDE 有意保留；不得将其标记为物理坐标导数或完整映射方程。
"""

import torch
from torch import nn

from ai4e_core.abilities.constraint.physical import residual_loss
from ai4e_core.abilities.sampling.physical import sample_points

from .trapezoid_basis import grid_basis

DATA_PROTOCOL = "trapezoid-euler-row-spacing-v1"


class TrapezoidPIBSNet(nn.Module):
    """完整输出后覆盖初边界，保留原输出头大小和初始化顺序。"""

    def __init__(self, control_points, hidden_dim=64):
        super().__init__()
        nt, ny, nx = control_points
        self.control_points = (nt, nx, ny)
        self.mlp = nn.Sequential(
            nn.Linear(1, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, nt * nx * ny),
        )

    def forward(self, parameters):
        """输出原始 t、xi、eta 控制系数；覆盖由公开 constrained_coefficients 执行。"""
        return self.mlp(parameters).view(-1, *self.control_points)


def validate(config):
    """只接受本组件实际支持的条件，不允许配置成功却被训练静默忽略。"""
    cfg = config["model"]
    boundaries = {
        n: {"u": {"type": "fixed_value", "value": 1.0}} for n in ("left", "right", "bottom", "top")
    }
    if (
        cfg["boundary_conditions"] != boundaries
        or cfg["constraints"]["boundary_conditions"]["enforcement"] != "hard"
        or cfg["constraints"]["boundary_conditions"].get("overrides")
        or cfg["periodic_boundary_conditions"]
        or cfg["hard_initial"]
        or cfg["initial_conditions"]["u"]
        != {"value": "dataset_initial", "corner_policy": "boundary_priority"}
        or cfg["constraints"]["initial_conditions"]["weight"] != 0
    ):
        raise ValueError("梯形组件要求初始系数内部零、四边一、boundary_priority 和无额外初值罚项")
    for name in ("initial",):
        if cfg["sampling"][name] != {"method": "all"}:
            raise ValueError("梯形初边界监测使用完整网格")
    if any(v != {"method": "all"} for v in cfg["sampling"]["boundaries"].values()):
        raise ValueError("梯形初边界监测使用完整网格")


def build(config):
    """构建选定梯形网络；未改变其他四例的模型行为。"""
    validate(config)
    return TrapezoidPIBSNet(config["model"]["control_points"], config["model"]["hidden_dim"])


def constrained_coefficients(model, parameters):
    """按原赋值顺序覆盖初始平面，再覆盖四边；交角以边界为准。"""
    value = model(parameters).clone()
    value[:, 0, :, :] = 0.0
    value[:, :, 0, :] = 1.0
    value[:, :, -1, :] = 1.0
    value[:, :, :, 0] = 1.0
    value[:, :, :, -1] = 1.0
    return value


def prepare(sample, config):
    """准备原全轴矩阵和网格采样身份；拒绝旧完整映射数据与离网点。"""
    validate(config)
    if sample.get("numerical_protocol") != DATA_PROTOCOL:
        raise ValueError("梯形数据协议不一致，需要独立重新生成；不接收历史完整映射数据")
    cfg = config["model"]
    for name in sample["axis_names"]:
        axis = sample["axes"][name]
        expected = torch.linspace(0, 1, len(axis), dtype=torch.float64)
        if sample["bounds"][name] != [0.0, 1.0] or not torch.allclose(
            axis.double(), expected, atol=1e-7, rtol=0
        ):
            raise ValueError("选定梯形样条需要 [0,1] 等距网格")
    sets = {}
    for name in ("supervised", "interior"):
        sets[name] = sample_points(
            sample,
            cfg["sampling"][name],
            seed=cfg["sampling"]["seed"],
            name=name,
            supervised=name == "supervised",
        )
        if sets[name].get("indices") is None:
            raise ValueError("选定梯形参数样条只支持网格点采样，不支持离网配点")
    bases = [
        grid_basis(n, cfg["degree"], len(sample["axes"][axis]))
        for n, axis in zip(cfg["control_points"], sample["axis_names"], strict=True)
    ]
    return {"sample": sample, "sets": sets, "grid_bases": bases}


def predictions(model, prepared, config):
    """原 einsum 收缩顺序输出完整场及参数导数，键名明确区分物理导数。"""
    parameter = next(model.parameters())
    a = torch.tensor(
        [[prepared["sample"]["parameters"]["a"]]], device=parameter.device, dtype=parameter.dtype
    )
    control = constrained_coefficients(model, a)
    t, y, x = [[v.to(parameter) for v in axis] for axis in prepared["grid_bases"]]

    def contract(bt, bx, by):
        return torch.einsum("btij,Tt,Xi,Yj->bTYX", control, bt, bx, by)[0]

    return {
        "u": contract(t[0], x[0], y[0]),
        "parameter_t": contract(t[1], x[0], y[0]),
        "parameter_xixi": contract(t[0], x[2], y[0]),
        "parameter_etaeta": contract(t[0], x[0], y[2]),
    }


def step(model, prepared, config):
    """原近似 PDE 与数据均方损失；硬条件只报告违约，不额外加罚。"""
    values = predictions(model, prepared, config)
    u = values["u"].unsqueeze(0)
    a = torch.tensor(prepared["sample"]["parameters"]["a"], device=u.device, dtype=u.dtype).view(
        1, 1, 1, 1
    )
    eta = torch.linspace(0, 1, u.shape[2], device=u.device, dtype=u.dtype).view(1, 1, -1, 1)
    residual = values["parameter_t"].unsqueeze(0) - 0.5 * (
        values["parameter_xixi"].unsqueeze(0) / (2.0 - eta) ** 2
        + a * values["parameter_etaeta"].unsqueeze(0)
    )
    constraints, groups = config["model"]["constraints"], prepared["sets"]
    # 全网格保留原非连续 einsum 布局的归约顺序；子集才通过索引收集。
    pde = (
        residual
        if config["model"]["sampling"]["interior"] == {"method": "all", "include_boundary": True}
        else residual.flatten()[groups["interior"]["indices"].to(u.device)]
    )
    data = (
        (u - prepared["sample"]["u"].to(u).unsqueeze(0))
        if config["model"]["sampling"]["supervised"] == {"method": "all"}
        else (
            u.flatten()[groups["supervised"]["indices"].to(u.device)]
            - groups["supervised"]["target"].to(u)
        )
    )
    losses = {}
    total = []
    for name, r, key in (("pde", pde, "equations"), ("data", data, "supervision")):
        settings = constraints[key]
        losses[name] = residual_loss(r, loss=settings["loss"], reduction=settings["reduction"])
        total.append(settings["weight"] * losses[name])
    with torch.no_grad():
        u = u[0]
        losses["initial"] = u[0, 1:-1, 1:-1].square().mean()
        for name, edge in (
            ("left", u[:, :, 0]),
            ("right", u[:, :, -1]),
            ("bottom", u[:, 0, :]),
            ("top", u[:, -1, :]),
        ):
            losses[f"boundary/{name}"] = (edge - 1).square().mean()
    # 与原先 data + lambda_phys * physics 的运算顺序相同。
    return {"loss": total[1] + total[0], "losses": losses}
