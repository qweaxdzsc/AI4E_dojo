"""固定时空数组的样本等权评价，明确归约轴而非混合不同物理量。"""

import torch


def horizon_mse(
    prediction: torch.Tensor,
    target: torch.Tensor,
    horizons: tuple[int, ...],
    *,
    time_dim: int = 1,
    includes_initial: bool = True,
) -> dict[str, float]:
    """计算从第一个预测帧到给定 horizon 的累计全元素 MSE。

    当输入包含初始帧时排除索引 0，并对 ``1..horizon`` 求均值；否则对
    ``0..horizon-1`` 求均值。超过已有时间长度的指标不返回。该定义与滚动预测中
    常见的 ``mse_H_steps`` 一致，不表示单独第 H 帧误差。
    """
    if prediction.shape != target.shape or prediction.ndim < 2:
        raise ValueError("预测和目标必须同形且包含时间轴")
    if not horizons or any(step <= 0 for step in horizons) or len(set(horizons)) != len(horizons):
        raise ValueError("horizons 必须是非空、唯一的正整数")
    time_dim = time_dim % prediction.ndim
    errors = (prediction - target).square().movedim(time_dim, 0)
    start = 1 if includes_initial else 0
    available = errors.shape[0] - start
    result = {}
    for horizon in horizons:
        if horizon <= available:
            result[f"mse_{horizon}_steps"] = float(errors[start : start + horizon].mean())
    return result


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


def named_frame_metrics(prediction, target, *, ids, times, fields, units):
    """CPU float64 的逐样本/时间/场 MSE 与相对 L2，零范数写 None。"""
    import numpy as np

    p, t = np.asarray(prediction, dtype=np.float64), np.asarray(target, dtype=np.float64)
    if (
        p.shape != t.shape
        or p.ndim != 4
        or p.shape[0] != len(ids)
        or p.shape[1] != len(times)
        or p.shape[-1] != len(fields)
        or len(units) != len(fields)
    ):
        raise ValueError("预测布局应为[B,T,N,C]且身份/字段/时间对齐")
    if not np.isfinite(p).all() or not np.isfinite(t).all():
        raise ValueError("评价非有限")
    rows = []
    for i, identity in enumerate(ids):
        for j, time in enumerate(times):
            for k, name in enumerate(fields):
                delta, truth = p[i, j, :, k] - t[i, j, :, k], t[i, j, :, k]
                denominator = np.linalg.norm(truth)
                rows.append(
                    {
                        "sample": identity,
                        "time": float(time),
                        "field": name,
                        "unit": units[k],
                        "mse": float(np.mean(delta**2)),
                        "relative_l2": float(np.linalg.norm(delta) / denominator)
                        if denominator
                        else None,
                    }
                )
    ratios = []
    for delta, truth in zip(p - t, t, strict=True):
        norm = np.linalg.norm(truth.reshape(-1))
        ratios.append(float(np.linalg.norm(delta.reshape(-1)) / norm) if norm else None)
    return {
        "rows": rows,
        "mse": float(np.mean((p - t) ** 2)),
        "sample_relative_l2": ratios,
        "mean_relative_l2": float(np.mean(ratios)) if all(v is not None for v in ratios) else None,
    }
