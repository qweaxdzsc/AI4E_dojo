"""基础 Burgers 场、小波准备和物理恢复的普通函数。"""

import torch
from pytorch_wavelets import DWT1DForward, DWTForward, DWTInverse

from .layout import coef_to_tensor, tensor_to_coef
from .preparation import get_wavelet_super_preprocess


def scale() -> torch.Tensor:
    """原实现逐通道缩放，同时也是损失权重。"""
    return torch.tensor([10, 3, 3, 1, 21, 5, 5, 1, 10]).view(1, 9, 1, 1)


def prepare(u: torch.Tensor, f: torch.Tensor) -> torch.Tensor:
    """保留反变换后提取 u0 的原训练条件舍入语义。"""
    fields = torch.stack((u, torch.nn.functional.pad(f, (0, 0, 0, 1))), dim=1)
    coefficients = coef_to_tensor(*DWTForward(J=1, mode="periodization", wave="bior2.4")(fields))
    values, shape, original = get_wavelet_super_preprocess(
        rescaler=scale(),
        mode="periodization",
        wave_type="bior2.4",
        is_condition_u0=True,
        is_condition_uT=False,
    )({"coef": [coefficients], "ori_shape": [81, 120]})
    if shape != [41, 60] or original != [81, 120]:
        raise ValueError("基础 Burgers 场维度不兼容")
    return values


def conditions(u: torch.Tensor, f: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
    """推理从原始 u0 求小波；不复用训练的反变换条件。"""
    low, high = DWT1DForward(J=1, mode="periodization", wave="bior2.4")(u[:, [0, -1]])
    initial = torch.zeros((len(u), 32, 64), dtype=u.dtype)
    initial[:, :16, :60] = low[:, [0]].expand(len(u), 16, 60)
    initial[:, 16:32, :60] = high[0][:, [0]].expand(len(u), 16, 60)
    force = torch.nn.functional.pad(f, (0, 0, 0, 1)).unsqueeze(1)
    force = coef_to_tensor(*DWTForward(J=1, mode="periodization", wave="bior2.4")(force))[:, 0]
    force = torch.nn.functional.pad(force, (0, 4, 0, 23))
    return initial / 10, force / scale()[:, 4:8]


def decode(coefficients: torch.Tensor) -> torch.Tensor:
    """恢复 u/f；不把预测初始时刻硬覆盖为真值。"""
    inverse = DWTInverse(mode="periodization", wave="bior2.4").to(coefficients.device)
    return inverse(tensor_to_coef(coefficients * scale().to(coefficients.device), [41, 60]))[
        :, :, :81, :120
    ]
