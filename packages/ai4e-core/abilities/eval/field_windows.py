"""固定二维时空窗口的物理空间误差，保留时间及分量归约信息。"""

import numpy as np


def field_metrics(prediction, reference, weights):
    """返回每时间、每通道的MAE/RMSE/相对L2；零参考范数返回None。"""
    prediction = np.asarray(prediction, dtype=np.float64)
    reference = np.asarray(reference, dtype=np.float64)
    if prediction.shape != reference.shape or prediction.ndim != 4:
        raise ValueError("需要同形T/X/Y/C场")
    weights = np.broadcast_to(np.asarray(weights, dtype=np.float64)[..., None], prediction.shape)
    if (
        not np.isfinite(prediction).all()
        or not np.isfinite(reference).all()
        or (weights < 0).any()
        or not np.isfinite(weights).all()
    ):
        raise ValueError("非有限场或非法权重")
    count = weights.sum((1, 2))
    if (count <= 0).any():
        raise ValueError("评价有效域为空")
    error = prediction - reference
    mse = (error**2 * weights).sum((1, 2)) / count
    ref = (reference**2 * weights).sum((1, 2)) / count
    relative = np.sqrt(np.divide(mse, ref, out=np.full_like(mse, np.nan), where=ref > 0))
    return {
        "mae": ((np.abs(error) * weights).sum((1, 2)) / count).tolist(),
        "rmse": np.sqrt(mse).tolist(),
        "relative_l2": [
            [None if not np.isfinite(v) else float(v) for v in row] for row in relative
        ],
        "mse": mse.tolist(),
        "reference_mean_square": ref.tolist(),
        "valid_count": count.tolist(),
    }


def combine_field_metrics(windows: list[dict]) -> dict:
    """按实际有效点合并同一轨迹窗口，保留预测时距及分量。"""
    if not windows:
        raise ValueError("没有窗口指标")
    count = np.asarray([m["valid_count"] for m in windows], dtype=np.float64)
    total = count.sum(0)
    if (total <= 0).any():
        raise ValueError("评价有效域为空")
    mae = (np.asarray([m["mae"] for m in windows]) * count).sum(0) / total
    mse = (np.asarray([m["mse"] for m in windows]) * count).sum(0) / total
    reference = (np.asarray([m["reference_mean_square"] for m in windows]) * count).sum(0) / total
    relative = np.sqrt(
        np.divide(mse, reference, out=np.full_like(mse, np.nan), where=reference > 0)
    )
    overall_count = total.sum(0)
    overall_mse = (mse * total).sum(0) / overall_count
    overall_ref = (reference * total).sum(0) / overall_count
    overall_relative = np.sqrt(
        np.divide(
            overall_mse, overall_ref, out=np.full_like(overall_mse, np.nan), where=overall_ref > 0
        )
    )
    return {
        "mae_by_time": mae.tolist(),
        "rmse_by_time": np.sqrt(mse).tolist(),
        "relative_l2_by_time": [
            [float(x) if np.isfinite(x) else None for x in row] for row in relative
        ],
        "mae": ((mae * total).sum(0) / overall_count).tolist(),
        "rmse": np.sqrt(overall_mse).tolist(),
        "relative_l2": [float(x) if np.isfinite(x) else None for x in overall_relative],
    }
