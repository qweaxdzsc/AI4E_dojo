"""局部代理拟合装配；调用公开代数/统计后端，不另写优化循环。"""

import time
from copy import deepcopy

import numpy as np

from ai4e_core.abilities.modeling.modules.polynomial import PolynomialBasis


def _guard(deadline, cancelled):
    if cancelled is not None and cancelled():
        raise InterruptedError("代理拟合已取消")
    if deadline is not None and time.monotonic() >= deadline:
        raise TimeoutError("代理拟合超时；单次BLAS硬截止由外层进程负责")


def fit_predictor(family, x, y, params=None, *, deadline=None, cancelled=None):
    """输入明确二维特征/目标，返回(model,state,diagnostics)，不写文件。

    Kriging 的多目标通过多个独立标量后验组成，不能声称联合目标协方差。
    LightGBM 原生后端延迟加载；RSM/RBF 不依赖其安装。截止为 monotonic 绝对时间。
    """
    from .prediction import rebuild

    options = deepcopy(params or {})
    x, y = np.asarray(x), np.asarray(y)
    if y.ndim == 1:
        y = y[:, None]
    if x.ndim != 2 or y.ndim != 2 or len(x) != len(y) or not len(x) or not y.shape[1]:
        raise ValueError("代理拟合需要对齐非空 [N,d] 输入及 [N,q] 目标")
    _guard(deadline, cancelled)
    start = time.monotonic()
    if family == "rsm":
        from ai4e_core.abilities.training.algebraic import fit_rsm

        state = fit_rsm(x, y, **options)
        diagnostics = state["diagnostics"]
    elif family == "rbf":
        from ai4e_core.abilities.modeling.modules.radial import RadialBasis
        from ai4e_core.abilities.training.algebraic import fit_rbf

        radial = RadialBasis(kernel=options.pop("kernel", "cubic"))
        polynomial = PolynomialBasis(x.shape[1], options.pop("degree", 1))
        state = fit_rbf(x, y, radial=radial, polynomial=polynomial, **options)
        diagnostics = state["diagnostics"]
    elif family == "kriging":
        from ai4e_core.abilities.training.kriging import fit_kriging

        trend = PolynomialBasis(x.shape[1], options.pop("trend_degree", 0))
        states, reports = [], []
        for column in range(y.shape[1]):
            _guard(deadline, cancelled)
            model, report = fit_kriging(
                x, y[:, column], trend=trend, deadline=deadline, cancelled=cancelled, **options
            )
            states.append(model.get_state())
            reports.append(report)
        state = {
            "kind": "independent-kriging-v1",
            "models": states,
            "input_dim": x.shape[1],
            "output_dim": y.shape[1],
        }
        diagnostics = {"targets": reports, "covariance_scope": "independent scalar posteriors"}
    elif family == "lightgbm":
        from ai4e_core.abilities.training.boosting import fit_boosting

        target_names = options.pop(
            "target_names", [f"output_{index}" for index in range(y.shape[1])]
        )
        feature_names = options.pop("feature_names", None)
        rounds = options.pop("num_boost_round", 100)
        # 内层 params 为原生树参数；其余入口键不能静默进入原生参数。
        native_params = options.pop("params", None)
        if options:
            raise ValueError(f"未知 LightGBM 拟合入口参数: {sorted(options)}")
        model, diagnostics = fit_boosting(
            x,
            y,
            target_names=target_names,
            feature_names=feature_names,
            params=native_params,
            num_boost_round=rounds,
            deadline=deadline,
            cancelled=cancelled,
        )
        state = model.get_state()
    else:
        raise ValueError(f"未知代理模型族: {family}")
    _guard(deadline, cancelled)
    model = rebuild(state)
    return model, state, {"family": family, "seconds": time.monotonic() - start, **diagnostics}
