"""参数到样条控制系数的唯一 PI-BSNet 实现；不包含训练循环。"""

import math

import torch
from torch import nn

from .spline import evaluate


class PIBSNet(nn.Module):
    """两层 ReLU MLP；硬定值边界通过开放样条边界控制系数实现。"""

    def __init__(self, parameter_names, control_points, *, hidden_dim=64, hard_boundaries=None):
        super().__init__()
        self.parameter_names = tuple(parameter_names)
        self.control_points = tuple(control_points)
        if len(self.control_points) not in (2, 3) or min(self.control_points) < 2:
            raise ValueError("控制网格维度无效")
        fixed = torch.zeros(self.control_points)
        mask = torch.zeros(self.control_points, dtype=torch.bool)
        for boundary, value in (hard_boundaries or {}).items():
            selection = [slice(None)] * len(self.control_points)
            if boundary in {"left", "right"}:
                selection[-1] = 0 if boundary == "left" else -1
            elif boundary in {"bottom", "top"} and len(selection) == 3:
                selection[-2] = 0 if boundary == "bottom" else -1
            else:
                raise ValueError(f"不支持的硬边界: {boundary}")
            key = tuple(selection)
            if mask[key].any() and not torch.all(fixed[key][mask[key]] == value):
                raise ValueError("硬边界交角目标冲突")
            mask[key] = True
            fixed[key] = value
        self.register_buffer("fixed", fixed)
        self.register_buffer("free_indices", (~mask).flatten().nonzero().flatten())
        count = len(self.free_indices)
        if not count:
            raise ValueError("无可训练控制系数")
        self.net = nn.Sequential(
            nn.Linear(len(parameter_names), hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, count),
        )

    def forward(self, parameters):
        """返回 [batch, control_t, control_x] 或 [batch,t,eta,xi] 控制网格。"""
        if parameters.ndim != 2 or parameters.shape[1] != len(self.parameter_names):
            raise ValueError("参数张量维度与声明不一致")
        free = self.net(parameters)
        base = self.fixed.flatten().expand(len(parameters), -1)
        full = base.scatter(1, self.free_indices.expand(len(parameters), -1), free)
        return full.reshape(len(parameters), *self.control_points)


def evaluate_fields(model, sample, bases, *, points, grid=False, hard_initial=False):
    """公开场与物理导数计算；Advection 可用解析初值 lifting 严格满足初值。"""
    parameter = next(model.parameters())
    inputs = torch.tensor(
        [[sample["parameters"][n] for n in model.parameter_names]],
        device=parameter.device,
        dtype=parameter.dtype,
    )
    values = evaluate(model(inputs)[0], bases, points=points, mapping=sample["mapping"], grid=grid)
    if hard_initial:
        if sample["case"] != "advection":
            raise ValueError("仅 Advection 支持解析初值 lifting，其他初值使用软约束")
        coords = points.to(parameter)
        time, x = coords[..., 0], coords[..., 1]
        phase = sample["parameters"]["phase"]
        initial = torch.sin(2 * math.pi * x + phase)
        factor = time / sample["bounds"]["t"][1]
        values = {
            "u": initial + factor * values["u"],
            "u_t": values["u"] / sample["bounds"]["t"][1] + factor * values["u_t"],
            "u_x": 2 * math.pi * torch.cos(2 * math.pi * x + phase) + factor * values["u_x"],
            "u_xx": -((2 * math.pi) ** 2) * initial + factor * values["u_xx"],
        }
    return values
