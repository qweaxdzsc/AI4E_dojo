"""稳定多输出最小二乘与径向增广系统；只交付状态，不创建训练执行器。"""

import numpy as np

from ai4e_core.abilities.modeling.modules.polynomial import PolynomialBasis
from ai4e_core.abilities.modeling.modules.radial import RadialBasis


def _matrix(value, name):
    if np.iscomplexobj(value):
        raise ValueError(f"{name} 必须为实数")
    result = np.asarray(value, dtype=np.float64)
    if result.ndim != 2 or min(result.shape) < 1 or not np.isfinite(result).all():
        raise ValueError(f"{name} 必须为非空有限矩阵")
    return result


def _targets(targets, count):
    targets = np.asarray(targets)
    if targets.ndim == 1:
        targets = targets[:, None]
    result = _matrix(targets, "目标")
    if len(result) != count:
        raise ValueError("输入与目标行数不同")
    return result


def fit_least_squares(design, targets, *, ridge: float = 0.0) -> dict:
    """通过经济型 SVD 拟合；ridge 显式惩罚全部系数，含常数项。

    默认满列秩，不用伪逆掩盖不可识别的模型；显式正则化允许欠定设计，
    仍记录原设计的秩和条件数。没有正规方程求逆或静默添加稳定项。
    """
    x = _matrix(design, "设计矩阵")
    y = _targets(targets, len(x))
    if not np.isscalar(ridge) or not np.isfinite(ridge) or ridge < 0:
        raise ValueError("ridge 必须为有限非负数")
    u, singular, vh = np.linalg.svd(x, full_matrices=False)
    tolerance = np.finfo(np.float64).eps * max(x.shape) * singular[0]
    rank = int(np.count_nonzero(singular > tolerance))
    if ridge == 0 and rank != x.shape[1]:
        raise ValueError(f"设计矩阵秩不足: rank={rank}, columns={x.shape[1]}")
    factors = singular / (singular**2 + ridge) if ridge else 1 / singular
    coefficients = (vh.T * factors) @ (u.T @ y)
    residual = x @ coefficients - y
    return {
        "coefficients": coefficients,
        "ridge": float(ridge),
        "diagnostics": {
            "rank": rank,
            "columns": x.shape[1],
            "sample_count": len(x),
            "condition": float(singular[0] / singular[-1]) if rank == x.shape[1] else None,
            "residual_sum_squares": (residual**2).sum(axis=0).tolist(),
        },
    }


def fit_rsm(inputs, targets, *, degree: int = 2, basis=None, ridge: float = 0.0) -> dict:
    """用共享多项式基拟合一次/二次响应面；返回可重建预测器的状态。"""
    x = _matrix(inputs, "输入")
    if degree not in (1, 2):
        raise ValueError("响应面次数必须为 1 或 2")
    basis = PolynomialBasis(x.shape[1], degree) if basis is None else basis
    state = fit_least_squares(basis(x), targets, ridge=ridge)
    return {"kind": "rsm-v1", "basis": basis.to_state(), **state}


def fit_rbf(inputs, targets, *, radial=None, polynomial=None, smoothing: float = 0.0) -> dict:
    """解 [K+lambda*I,P;P.T,0] 增广系统，多输出共用一次分解。

    固定中心为输入训练行；尾项用中心包围盒平移缩放改善量级，但核距离仍
    使用原输入。重复中心仅在零平滑时拒绝；尾项始终要求满列秩。
    """
    x = _matrix(inputs, "中心")
    y = _targets(targets, len(x))
    if not np.isscalar(smoothing) or not np.isfinite(smoothing) or smoothing < 0:
        raise ValueError("smoothing 必须为有限非负数")
    radial = RadialBasis() if radial is None else radial
    polynomial = PolynomialBasis(x.shape[1], 1) if polynomial is None else polynomial
    if polynomial.degree < radial.minimum_degree or not polynomial.include_bias:
        raise ValueError("径向核缺少必要多项式尾项")
    if smoothing == 0 and len(np.unique(x, axis=0)) != len(x):
        raise ValueError("零平滑插值不允许重复中心")
    shift, scale = (x.max(0) + x.min(0)) / 2, (x.max(0) - x.min(0)) / 2
    scale[scale == 0] = 1
    p = polynomial((x - shift) / scale)
    if np.linalg.matrix_rank(p) != p.shape[1]:
        raise ValueError("径向多项式尾项秩不足")
    kernel = radial(x, x)
    system = np.block(
        [[kernel + smoothing * np.eye(len(x)), p], [p.T, np.zeros((p.shape[1], p.shape[1]))]]
    )
    rhs = np.concatenate((y, np.zeros((p.shape[1], y.shape[1]))))
    condition = float(np.linalg.cond(system))
    if not np.isfinite(condition) or condition >= 1 / np.finfo(np.float64).eps:
        raise ValueError("径向系统数值奇异；不自动添加抖动")
    try:
        coefficients = np.linalg.solve(system, rhs)
    except np.linalg.LinAlgError as error:
        raise ValueError("径向增广系统奇异") from error
    return {
        "kind": "rbf-v1",
        "centers": x.copy(),
        "radial": radial.to_state(),
        "polynomial": polynomial.to_state(),
        "shift": shift,
        "scale": scale,
        "radial_coefficients": coefficients[: len(x)],
        "polynomial_coefficients": coefficients[len(x) :],
        "smoothing": float(smoothing),
        "diagnostics": {
            "condition": condition,
            "sample_count": len(x),
            "tail_columns": p.shape[1],
            "system_residual_max": float(np.max(abs(system @ coefficients - rhs))),
        },
    }
