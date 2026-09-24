"""统计代理独立参考：增广克里金系统与官方LightGBM，不导入Dojo计算。

克里金是本轮明确的GLS未知趋势/固定观测噪声变体，不冒称SMT或论文复现。
固定参数参考直接解增广鞍点系统；产品采用Cholesky与趋势Gram矩阵。
拟合/建树入口仅由主控统一串行调用；导入不会启动计算或安装依赖。
"""

from __future__ import annotations

import importlib
import time
from collections.abc import Callable, Mapping, Sequence

import numpy as np

SOURCES = {
    "kriging": {
        "variant": "ordinary/universal GLS, fixed observation noise, plug-in profile ML",
        "reference": "independent augmented covariance/trend saddle-point equations",
        "scipy_version": "1.18.1",
        "scipy_license": "BSD-3-Clause",
        "scipy_license_url": "https://raw.githubusercontent.com/scipy/scipy/v1.18.1/LICENSE.txt",
        "scipy_license_sha256": "221e59f5e910fd7f94e44f0dac77436a11338c285c6346232e4a850a50da0e94",
        "paper_reproduction": False,
    },
    "lightgbm": {
        "version": "4.6.0",
        "commit": "d02a01ac6f51d36c9e62388243bcb75c3b1b1774",
        "license": "MIT",
        "license_url": "https://raw.githubusercontent.com/microsoft/LightGBM/v4.6.0/LICENSE",
        "license_sha256": "b5cb7ff7859e7d282d98fc43ab081b0dda5dc659dc3385cf65740c759a7e6a6c",
        "engine_sha256": "c5010abf6bef08f407b64d4b1585bd18875213d594a7f068d9ddfc8bf3b47753",
    },
}


def _trend(x: np.ndarray, degree: int) -> np.ndarray:
    if degree == 0:
        return np.ones((len(x), 1), dtype=np.float64)
    if degree == 1:
        return np.column_stack((np.ones(len(x)), x))
    raise ValueError("独立克里金参考仅声明常数/线性趋势")


def _kernel(x: np.ndarray, z: np.ndarray, scale, variance: float) -> np.ndarray:
    # 按维累加，独立于产品的缩放特征/距离实现。
    scales = np.broadcast_to(np.asarray(scale, dtype=np.float64), (x.shape[1],))
    distances = np.zeros((len(x), len(z)), dtype=np.float64)
    for axis, length in enumerate(scales):
        distances += ((x[:, axis, None] - z[None, :, axis]) / length) ** 2
    return float(variance) * np.exp(-0.5 * distances)


def kriging_reference(
    train_x: np.ndarray,
    train_y: np.ndarray,
    query_x: np.ndarray,
    *,
    length_scale,
    variance: float,
    degree: int = 0,
    noise_variance=0.0,
    jitter: float = 0.0,
    query_noise=0.0,
    return_gradient: bool = False,
) -> dict:
    """独立求解增广系统，返回均值、含未知趋势修正的方差及profile-ML值。

    三种方差语义分开：variance是过程方差，noise_variance为观测噪声，
    jitter仅加入训练求解矩阵；查询方差只在显式query_noise时增加观测噪声。
    """
    from scipy.linalg import lu_factor, lu_solve

    x, y, q = (np.asarray(v, dtype=np.float64) for v in (train_x, train_y, query_x))
    f, fq = _trend(x, degree), _trend(q, degree)
    kernel = _kernel(x, x, length_scale, variance)
    c = kernel.copy()
    c += np.diag(np.broadcast_to(np.asarray(noise_variance), (len(x),)) + jitter)
    cross = _kernel(x, q, length_scale, variance)
    augmented = np.block([[c, f], [f.T, np.zeros((f.shape[1], f.shape[1]))]])
    solved = np.linalg.solve(augmented, np.vstack((cross, fq.T)))
    weights, lagrange = solved[: len(x)], solved[len(x) :]
    prediction = y @ weights
    uncertainty = variance - (weights * cross).sum(0) - (lagrange * fq.T).sum(0)
    uncertainty += np.broadcast_to(np.asarray(query_noise), (len(q),))
    # 此独立求解同时给出条件系数和GLS趋势，不调用产品状态构造。
    fitted = np.linalg.solve(augmented, np.r_[y, np.zeros(f.shape[1])])
    alpha, beta = fitted[: len(x)], fitted[len(x) :]
    lu, pivots = lu_factor(c)
    diagonal = np.diag(lu)
    sign = np.prod(np.sign(diagonal)) * (-1) ** np.count_nonzero(pivots != np.arange(len(x)))
    if sign <= 0 or not np.isfinite(diagonal).all():
        raise ValueError("参考协方差行列式非正")
    logdet = np.log(np.abs(diagonal)).sum()
    nll = 0.5 * (logdet + (y - f @ beta) @ alpha + len(x) * np.log(2 * np.pi))
    if not np.isfinite(nll):
        raise FloatingPointError("参考profile-ML值非有限")
    output = {"mean": prediction, "variance": uncertainty, "beta": beta, "nll": float(nll)}
    if return_gradient:
        scales = np.broadcast_to(np.asarray(length_scale), (x.shape[1],))
        gradient = []
        for dimension in range(x.shape[1] + 1):
            derivative = kernel.copy()
            if dimension < x.shape[1]:
                distance = np.subtract.outer(x[:, dimension], x[:, dimension])
                derivative *= distance**2 / scales[dimension] ** 2
            gradient.append(
                0.5
                * (
                    np.trace(lu_solve((lu, pivots), derivative))
                    - np.dot(alpha, np.dot(derivative, alpha))
                )
            )
        output["gradient"] = np.asarray(gradient)
        if not np.isfinite(output["gradient"]).all():
            raise FloatingPointError("独立参考解析梯度非有限")
    return output


def fit_kriging_reference(
    train_x: np.ndarray,
    train_y: np.ndarray,
    query_x: np.ndarray,
    *,
    degree: int,
    kernel_config: Mapping,
    noise_variance=0.0,
    jitter: float = 1e-10,
    optimization: Mapping | None = None,
    deadline: float | None = None,
    cancelled: Callable[[], bool] | None = None,
) -> dict:
    """主控专用独立有界拟合；同初值/界限但增广系统数学与产品分离。"""
    from scipy.optimize import minimize

    x = np.asarray(train_x, dtype=np.float64)
    settings = dict(optimization or {})
    initial = np.r_[
        np.broadcast_to(kernel_config["length_scale"], (x.shape[1],)), kernel_config["variance"]
    ]
    bounds = np.vstack(
        (
            np.broadcast_to(settings.get("length_scale_bounds", (0.05, 20.0)), (x.shape[1], 2)),
            settings.get("variance_bounds", (1e-6, 100.0)),
        )
    )

    def evaluate(parameters):
        if cancelled is not None and cancelled():
            raise InterruptedError("参考拟合取消")
        if deadline is not None and time.monotonic() >= deadline:
            raise TimeoutError("参考拟合预算耗尽")
        values = np.exp(parameters)
        return kriging_reference(
            x,
            train_y,
            query_x,
            length_scale=values[:-1],
            variance=values[-1],
            degree=degree,
            noise_variance=noise_variance,
            jitter=jitter,
            return_gradient=True,
        )

    options = {
        k: settings.get(k, default)
        for k, default in (("maxiter", 20), ("maxfun", 200), ("ftol", 1e-9), ("gtol", 1e-6))
    }

    def objective(parameters):
        result = evaluate(parameters)
        return result["nll"], result["gradient"]

    result = minimize(
        objective,
        np.log(initial),
        method="L-BFGS-B",
        jac=True,
        bounds=np.log(bounds),
        options=options,
    )
    return {
        **evaluate(result.x),
        "length_scale": np.exp(result.x[:-1]),
        "process_variance": float(np.exp(result.x[-1])),
        "success": bool(result.success),
        "message": str(result.message),
        "iterations": int(result.nit),
        "evaluations": int(result.nfev),
        "gradient_method": "analytic_profile_ml_augmented_gls_lu",
    }


def lightgbm_reference(
    train_x: np.ndarray,
    train_y: np.ndarray,
    query_x: np.ndarray,
    *,
    params: Mapping,
    num_boost_round: int,
    feature_names: Sequence[str],
    initial_models: Sequence[str] | None = None,
    deadline: float | None = None,
    cancelled: Callable[[], bool] | None = None,
) -> dict:
    """主控专用官方独立建树，返回原生文本和预测；不调用Dojo包装。"""
    lgb = importlib.import_module("lightgbm")
    y = np.asarray(train_y)
    if y.ndim == 1:
        y = y[:, None]
    models, predictions = [], []

    def check_stop(_environment=None):
        if cancelled is not None and cancelled():
            raise InterruptedError("官方参考建树取消")
        if deadline is not None and time.monotonic() >= deadline:
            raise TimeoutError("官方参考建树预算耗尽")

    check_stop.before_iteration = True
    check_stop.order = -100
    for index in range(y.shape[1]):
        check_stop()
        data = lgb.Dataset(train_x, label=y[:, index], feature_name=list(feature_names))
        previous = None if initial_models is None else lgb.Booster(model_str=initial_models[index])
        model = lgb.train(
            dict(params),
            data,
            num_boost_round=num_boost_round,
            init_model=previous,
            keep_training_booster=True,
            callbacks=[check_stop],
        )
        check_stop()
        predictions.append(model.predict(query_x, num_iteration=model.current_iteration()))
        models.append(model.model_to_string(num_iteration=model.current_iteration()))
    return {
        "prediction": np.column_stack(predictions),
        "models": models,
        "version": lgb.__version__,
    }
