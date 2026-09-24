"""克里金固定条件求解与有界最大似然拟合，不承担数据语义、记录或写盘。"""

from __future__ import annotations

import time
from collections.abc import Callable, Mapping
from typing import Any

import numpy as np

from ai4e_core.abilities.modeling.models.kriging import Kriging
from ai4e_core.abilities.modeling.modules.covariance import KrigingCondition, SquaredExponential
from ai4e_core.abilities.modeling.modules.polynomial import PolynomialBasis


def _array(value: Any, rank: int, name: str) -> np.ndarray:
    raw = np.asarray(value)
    if raw.dtype.kind not in "fiu" or raw.ndim != rank or not raw.size:
        raise ValueError(f"{name}须为非空{rank}维实数数组")
    result = np.asarray(raw, dtype=np.float64)
    if not np.isfinite(result).all():
        raise ValueError(f"{name}含非有限值")
    return result


def _nonnegative(value: Any, name: str) -> float:
    raw = np.asarray(value)
    if raw.ndim or raw.dtype.kind not in "fiu" or not np.isfinite(raw) or raw < 0:
        raise ValueError(f"{name}须为有限非负标量")
    return float(raw)


def solve_kriging_condition(
    covariance: Any,
    design: Any,
    y: Any,
    *,
    noise_variance: Any = 0.0,
    jitter: float = 1e-10,
    negative_variance_tolerance: float = 1e-10,
) -> tuple[KrigingCondition, dict]:
    """给定[N,N]过程协方差、[N,P]满秩趋势和[N]响应，求固定条件状态。

    显式GLS未知趋势，保留趋势估计方差。噪声与jitter分别登记；不自动增大
    扰动、不使用伪逆。矩阵不正定或趋势退化抛ValueError，不静默换模型。
    """
    from scipy.linalg import cho_solve, solve_triangular

    kernel, f, target = (
        _array(covariance, 2, "协方差"),
        _array(design, 2, "趋势"),
        _array(y, 1, "响应"),
    )
    n, p = f.shape
    if kernel.shape != (n, n) or target.shape != (n,) or n <= p:
        raise ValueError("协方差、趋势、响应形状错误或没有趋势剩余自由度")
    if not np.allclose(kernel, kernel.T, rtol=1e-12, atol=1e-14):
        raise ValueError("过程协方差须对称")
    if np.linalg.matrix_rank(f) != p:
        raise ValueError("趋势设计矩阵须满列秩")
    noise = np.asarray(noise_variance)
    if noise.dtype.kind not in "fiu" or noise.shape not in ((), (n,)):
        raise ValueError("观测噪声须为实数标量或[N]数组")
    noise = np.broadcast_to(noise, (n,)).astype(np.float64, copy=True)
    if not np.isfinite(noise).all() or (noise < 0).any():
        raise ValueError("观测噪声须有限且非负")
    perturbation = _nonnegative(jitter, "jitter")
    tolerance = _nonnegative(negative_variance_tolerance, "negative_variance_tolerance")
    c = (kernel + kernel.T) * 0.5 + np.diag(noise + perturbation)
    try:
        chol = np.linalg.cholesky(c)
        whitened = solve_triangular(chol, f, lower=True)
        chol_trend = np.linalg.cholesky(whitened.T @ whitened)
    except np.linalg.LinAlgError as error:
        raise ValueError("协方差或GLS趋势矩阵非正定；请显式调整数据、噪声或jitter") from error
    inv_f = cho_solve((chol, True), f)
    inv_y = cho_solve((chol, True), target)
    beta = cho_solve((chol_trend, True), f.T @ inv_y)
    residual = target - f @ beta
    alpha = cho_solve((chol, True), residual)
    nll = 0.5 * (2.0 * np.log(np.diag(chol)).sum() + residual @ alpha + n * np.log(2 * np.pi))
    if not np.isfinite(nll):
        raise FloatingPointError("克里金似然非有限")
    state = {
        "kind": "kriging_condition",
        "version": 1,
        "beta": beta,
        "alpha": alpha,
        "chol_covariance": chol,
        "inv_covariance_trend": inv_f,
        "chol_trend": chol_trend,
        "noise_variance": noise,
        "jitter": perturbation,
        "negative_variance_tolerance": tolerance,
    }
    return KrigingCondition(state), {
        "objective": "profile_maximum_likelihood",
        "nll": float(nll),
        "samples": n,
        "trend_terms": p,
        "jitter": perturbation,
        "noise_variance": noise.copy(),
    }


def condition_kriging(
    x: Any,
    y: Any,
    *,
    trend: Any = None,
    kernel_config: Mapping | None = None,
    noise_variance: Any = 0.0,
    jitter: float = 1e-10,
    negative_variance_tolerance: float = 1e-10,
) -> tuple[Kriging, dict]:
    """按显式固定核参数求条件模型，不做超参数优化；默认未知常数趋势。"""
    points = _array(x, 2, "训练特征")
    basis = PolynomialBasis(points.shape[1], 0) if trend is None else trend
    covariance = SquaredExponential(**dict(kernel_config or {}))
    condition, report = solve_kriging_condition(
        covariance(points, points),
        basis(points),
        y,
        noise_variance=noise_variance,
        jitter=jitter,
        negative_variance_tolerance=negative_variance_tolerance,
    )
    return Kriging(points, trend=basis, covariance=covariance, condition=condition), report


def kriging_profile_gradient(model: Kriging) -> np.ndarray:
    """固定条件点的profile-ML解析梯度，次序为逐轴log长度尺度、log过程方差。

    GLS残差对趋势导数的项由F.T@alpha=0消去；这里不使用REML投影迹项。
    用已保存Cholesky解各个dC，不显式构造协方差逆，也不推进优化器。
    """
    from scipy.linalg import cho_solve

    x, covariance = model.training_x, model.covariance
    state = model.condition.get_state()
    kernel = covariance(x, x)
    scaled = (x[:, None, :] - x[None, :, :]) / covariance.length_scale
    derivatives = [kernel * scaled[:, :, axis] ** 2 for axis in range(x.shape[1])]
    derivatives.append(kernel)
    alpha = state["alpha"]
    gradient = np.array(
        [
            0.5
            * (
                np.trace(cho_solve((state["chol_covariance"], True), derivative))
                - alpha @ derivative @ alpha
            )
            for derivative in derivatives
        ]
    )
    if not np.isfinite(gradient).all():
        raise FloatingPointError("profile-ML梯度非有限")
    return gradient


def fit_kriging(
    x: Any,
    y: Any,
    *,
    trend: Any = None,
    kernel_config: Mapping | None = None,
    noise_variance: Any = 0.0,
    jitter: float = 1e-10,
    optimization: Mapping | None = None,
    cancelled: Callable[[], bool] | None = None,
    deadline: float | None = None,
) -> tuple[Kriging, dict]:
    """单初值L-BFGS-B优化对数长度尺度及过程方差，返回模型与真实终止诊断。

    deadline为time.monotonic绝对时刻；在每次目标计算前检查。超时或取消
    抛异常，不把不完整优化当成功。maxiter/maxfun限制正常返回诊断，模型
    采用优化器最终有效点。预测状态可重载，不声明优化器任意内部步恢复。
    """
    from scipy.optimize import minimize

    points, target = _array(x, 2, "训练特征"), _array(y, 1, "响应")
    basis = PolynomialBasis(points.shape[1], 0) if trend is None else trend
    settings = dict(optimization or {})
    allowed = {"maxiter", "maxfun", "ftol", "gtol", "length_scale_bounds", "variance_bounds"}
    if settings.keys() - allowed:
        raise ValueError(f"未知优化参数: {sorted(settings.keys() - allowed)}")
    options = {
        k: settings.get(k, v)
        for k, v in (("maxiter", 20), ("maxfun", 200), ("ftol", 1e-9), ("gtol", 1e-6))
    }
    for key in ("maxiter", "maxfun"):
        if type(options[key]) is not int or options[key] <= 0:
            raise ValueError(f"{key}须为正整数")
    for key in ("ftol", "gtol"):
        options[key] = _nonnegative(options[key], key)
    initial_covariance = SquaredExponential(**dict(kernel_config or {}))
    initial = np.r_[
        np.broadcast_to(initial_covariance.length_scale, (points.shape[1],)),
        initial_covariance.variance,
    ]
    bounds = np.vstack(
        (
            np.broadcast_to(
                settings.get("length_scale_bounds", (0.05, 20.0)), (points.shape[1], 2)
            ),
            settings.get("variance_bounds", (1e-6, 100.0)),
        )
    )
    if not np.isfinite(bounds).all() or (bounds <= 0).any() or np.any(bounds[:, 0] >= bounds[:, 1]):
        raise ValueError("超参数界限须有限、为正且下界小于上界")
    if np.any(initial < bounds[:, 0]) or np.any(initial > bounds[:, 1]):
        raise ValueError("超参数初值须在显式界限内")
    if deadline is not None and not np.isfinite(deadline):
        raise ValueError("deadline须为有限monotonic时刻")

    def evaluate(parameters):
        if cancelled is not None and cancelled():
            raise InterruptedError("克里金拟合取消")
        if deadline is not None and time.monotonic() >= deadline:
            raise TimeoutError("克里金拟合预算耗尽")
        values = np.exp(parameters)
        return condition_kriging(
            points,
            target,
            trend=basis,
            kernel_config={"length_scale": values[:-1], "variance": float(values[-1])},
            noise_variance=noise_variance,
            jitter=jitter,
        )

    def objective(parameters):
        conditioned, diagnostic = evaluate(parameters)
        return diagnostic["nll"], kriging_profile_gradient(conditioned)

    start = time.monotonic()
    result = minimize(
        objective,
        np.log(initial),
        method="L-BFGS-B",
        jac=True,
        bounds=np.log(bounds),
        options=options,
    )
    model, report = evaluate(result.x)
    report.update(
        {
            "success": bool(result.success),
            "status": int(result.status),
            "message": str(result.message),
            "iterations": int(result.nit),
            "evaluations": int(result.nfev),
            "elapsed_seconds": time.monotonic() - start,
            "initial": initial.copy(),
            "bounds": bounds.copy(),
            "options": options,
            "length_scale": model.covariance.length_scale.copy(),
            "process_variance": model.covariance.variance,
            "optimizer_resume": False,
            "gradient_method": "analytic_profile_ml_cholesky",
            "final_gradient": kriging_profile_gradient(model),
        }
    )
    return model, report
