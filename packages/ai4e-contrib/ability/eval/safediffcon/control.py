"""基于实际响应的论文控制指标，源码目标和原始 targets 分别命名。"""

import numpy as np


def metrics(
    response: np.ndarray, target: np.ndarray, *, case: str, paper_target: np.ndarray | None = None
) -> dict:
    """样本等权评价，拒绝非有限响应而非将失败当零违规。"""
    response, target = np.asarray(response, dtype=np.float64), np.asarray(target, dtype=np.float64)
    if case not in {"burgers", "tokamak"}:
        raise ValueError("未知控制案例")
    expected_shape = (11, 128) if case == "burgers" else (3, 122)
    if (
        response.ndim != 3
        or len(response) == 0
        or response.shape[1:] != expected_shape
        or response.shape != target.shape
        or not np.isfinite(response).all()
        or not np.isfinite(target).all()
    ):
        raise ValueError("响应形状或数值非法")
    if paper_target is not None:
        paper_target = np.asarray(paper_target, dtype=np.float64)
        if paper_target.shape != response.shape or not np.isfinite(paper_target).all():
            raise ValueError("数据集目标形状或数值非法")
    if case == "burgers":
        j = np.square(response[:, -1] - target[:, -1]).mean(-1)
        mask = np.abs(response) > 0.8
        result = {
            "J": float(j.mean()),
            "R_sample": float(mask.any(axis=(1, 2)).mean()),
            "R_time": float(mask.any(axis=-1).mean()),
            "R_point": float(mask.mean()),
        }
    else:
        j = np.square(response[:, [0, 2]] - target[:, [0, 2]]).mean(-1).sum(-1)
        mask = response[:, 1] < 4.98
        result = {
            "J_source_outputs": float(j.mean()),
            "R_sample": float(mask.any(axis=1).mean()),
            "R_time": float(mask.mean()),
        }
        if paper_target is not None:
            result["J_dataset_targets"] = float(
                np.square(response[:, [0, 2]] - np.asarray(paper_target)[:, [0, 2]])
                .mean(-1)
                .sum(-1)
                .mean()
            )
    result["per_sample_objective"] = j.tolist()
    return result
