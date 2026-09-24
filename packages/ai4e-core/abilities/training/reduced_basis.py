"""训练快照的中心化加权经济型分解；不认识分片名称或运行目录。"""

import numpy as np


def fit_pod(snapshots: np.ndarray, rank: int, *, weights=None) -> dict:
    """拟合 [N,D] 的 POD；调用方只传训练快照，返回显式数值状态。

    正权重定义空间度量而不是样本权重。通过 sqrt(W) 加权后做经济型 SVD，
    不构造 D×D 矩阵。数值秩使用 eps*max(N,D)*最大奇异值，不截取零能量方向。
    """
    if np.iscomplexobj(snapshots) or np.iscomplexobj(weights):
        raise ValueError("POD 只接受实数")
    x = np.asarray(snapshots, dtype=np.float64)
    if x.ndim != 2 or x.shape[0] < 2 or x.shape[1] < 1 or not np.isfinite(x).all():
        raise ValueError("POD 快照须为至少两行有限 [N,D]")
    if type(rank) is not int or rank < 1 or rank > min(x.shape[0] - 1, x.shape[1]):
        raise ValueError("POD 秩必须为中心化维数内正整数")
    w = np.ones(x.shape[1]) if weights is None else np.array(weights, dtype=np.float64, copy=True)
    if w.shape != (x.shape[1],) or not np.isfinite(w).all() or (w <= 0).any():
        raise ValueError("POD 权重须为有限正 [D]")
    mean = x.mean(axis=0)
    weighted = (x - mean) * np.sqrt(w)
    _, singular, vh = np.linalg.svd(weighted, full_matrices=False)
    threshold = np.finfo(np.float64).eps * max(x.shape) * singular[0]
    numerical_rank = int(np.count_nonzero(singular > threshold))
    if singular[0] == 0 or rank > numerical_rank:
        raise ValueError(f"POD 零能量或请求秩超过数值秩 {numerical_rank}")
    basis = vh[:rank].T / np.sqrt(w[:, None])
    energy = singular**2
    return {
        "kind": "pod-v1",
        "mean": mean,
        "weights": w,
        "basis": basis,
        "singular_values": singular,
        "rank": rank,
        "diagnostics": {
            "sample_count": len(x),
            "numerical_rank": numerical_rank,
            "retained_energy": float(energy[:rank].sum() / energy.sum()),
            "rank_threshold": float(threshold),
        },
    }
