"""固定时空数组的样本等权评价，明确归约轴而非混合不同物理量。"""

import torch


def trajectory_metrics(prediction, target, *, axes=("B", "T", "H", "W", "C")):
    """输入 B,T,H,W,C；返回逐样本/逐分量/逐物理帧相对 L2。"""
    expected = ("B", "T", "H", "W", "C")
    if len(axes) != 5 or set(axes) != set(expected):
        raise ValueError("必须明确样本、时间、二维空间和分量轴")
    permutation = [axes.index(axis) for axis in expected]
    prediction, target = prediction.permute(permutation), target.permute(permutation)
    if prediction.shape != target.shape or prediction.ndim != 5 or not target.numel():
        raise ValueError("轨迹必须是同形 B,T,H,W,C 数组")
    if not torch.isfinite(prediction).all() or not torch.isfinite(target).all():
        raise ValueError("轨迹包含非有限值")
    difference = prediction - target

    def ratios(axes):
        numerator = difference.square().sum(dim=axes).sqrt()
        denominator = target.square().sum(dim=axes).sqrt()
        return torch.where(denominator > 0, numerator / denominator, torch.nan)

    components = ratios((1, 2, 3))

    def serial(value):
        if value.ndim == 0:
            return float(value) if torch.isfinite(value) else None
        return [serial(item) for item in value]

    return {
        "sample_component_relative_l2": serial(components),
        "component_relative_l2": serial(components.mean(dim=0)),
        "field_relative_l2": serial(components.mean()),
        "frame_component_relative_l2": serial(ratios((2, 3)).mean(dim=0)),
        "sample_trajectory_relative_l2": serial(ratios((1, 2, 3, 4))),
        "mse": serial(difference.square().mean()),
    }
