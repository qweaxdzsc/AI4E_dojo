"""按目标调用官方LightGBM训练，保留预算停止与原生接续语义。"""

from __future__ import annotations

import hashlib
import json
import time
from collections.abc import Callable, Mapping, Sequence
from typing import Any

import numpy as np

from ai4e_core.abilities.modeling.models.lightgbm import LightGBMPredictor, _backend, _names


def _matrix(value, label):
    raw = np.asarray(value)
    if raw.dtype.kind not in "fiu" or raw.ndim != 2 or not raw.size:
        raise ValueError(f"{label}须为非空二维实数数组")
    result = np.array(raw, dtype=np.float64, order="C", copy=True)
    if not np.isfinite(result).all():
        raise ValueError(f"{label}须有限，不做隐式补缺")
    return result


def _digest(x, y, features, targets):
    digest = hashlib.sha256()
    digest.update(
        json.dumps(
            {"features": features, "targets": targets}, ensure_ascii=False, sort_keys=True
        ).encode()
    )
    for value in (x, y):
        digest.update(str(value.shape).encode())
        digest.update(value.astype("<f8", copy=False).tobytes(order="C"))
    return digest.hexdigest()


def _parameters(params):
    supplied = dict(params or {})
    # 别名可能绕过实际轮数、CPU、目标和列身份的显式约定，统一拒绝。
    forbidden = {
        "num_iterations",
        "num_iteration",
        "n_iter",
        "num_tree",
        "num_trees",
        "num_round",
        "num_rounds",
        "nrounds",
        "num_boost_round",
        "n_estimators",
        "max_iter",
        "application",
        "app",
        "loss",
        "device",
        "device_type",
        "tree_learner",
        "num_class",
        "num_classes",
        "categorical_feature",
        "cat_feature",
        "categorical_column",
        "cat_column",
        "objective_seed",
        "early_stopping_round",
        "early_stopping_rounds",
        "early_stopping",
        "n_iter_no_change",
        "num_thread",
        "nthread",
        "nthreads",
        "n_jobs",
        "random_seed",
        "random_state",
        "boost",
        "boosting",
        "monotone_constraints_method",
    }
    if supplied.keys() & forbidden:
        raise ValueError(
            f"使用显式参数而不是后端别名/不支持模式: {sorted(supplied.keys() & forbidden)}"
        )
    effective = {
        "objective": "regression",
        "boosting_type": "gbdt",
        "deterministic": True,
        "force_col_wise": True,
        "num_threads": 1,
        "seed": 42,
        "verbosity": -1,
    }
    effective.update(supplied)
    if effective["objective"] != "regression" or effective["boosting_type"] != "gbdt":
        raise ValueError("首批只支持连续目标的gbdt平方误差回归")
    if (
        effective["deterministic"] is not True
        or effective["force_col_wise"] is not True
        or effective.get("force_row_wise", False)
    ):
        raise ValueError("需保持deterministic与force_col_wise设置")
    if type(effective["num_threads"]) is not int or effective["num_threads"] <= 0:
        raise ValueError("num_threads须为明确正整数")
    # 记录可移植的有效参数，拒绝可执行对象/NaN。
    try:
        json.dumps(effective, allow_nan=False)
    except (TypeError, ValueError) as error:
        raise ValueError("参数须为可序列化的有限普通值") from error
    return effective


def fit_boosting(
    x: Any,
    y: Any,
    *,
    target_names: Sequence[str],
    feature_names: Sequence[str] | None = None,
    params: Mapping | None = None,
    num_boost_round: int = 100,
    initial_model: LightGBMPredictor | None = None,
    cancelled: Callable[[], bool] | None = None,
    deadline: float | None = None,
) -> tuple[LightGBMPredictor, dict]:
    """训练[N,D]到[N,Q]独立提升树，返回普通预测对象和实际轮次诊断。

    num_boost_round为本次请求的追加轮数。接续须同训练数组/字段/有效参数与
    后端版本；原生追加不等于已证明与不中断逐值相同。每轮之前检查停止；
    任一目标取消/超时会抛异常，不把部分目标模型冒充完整结果。deadline为
    time.monotonic绝对时刻，单次原生树计算无法在内部抢占。
    """
    points = _matrix(x, "训练特征")
    raw_y = np.asarray(y)
    targets = _matrix(raw_y[:, None] if raw_y.ndim == 1 else raw_y, "训练响应")
    if len(points) != len(targets):
        raise ValueError("训练特征与响应行数不匹配")
    if type(num_boost_round) is not int or num_boost_round <= 0:
        raise ValueError("num_boost_round须为正整数")
    features = _names(
        feature_names
        if feature_names is not None
        else [f"feature_{i}" for i in range(points.shape[1])],
        points.shape[1],
        "特征名",
    )
    names = _names(target_names, targets.shape[1], "目标名")
    effective = _parameters(params)
    identity = _digest(points, targets, features, names)
    if deadline is not None and not np.isfinite(deadline):
        raise ValueError("deadline须为有限monotonic时刻")
    previous = None
    if initial_model is not None:
        if (
            initial_model.training_digest != identity
            or list(initial_model.feature_names) != features
            or list(initial_model.target_names) != names
            or initial_model.params != effective
        ):
            raise ValueError("接续须具有相同训练数组、字段次序与有效参数")
        previous = initial_model.get_state()

    def check_stop(_environment=None):
        if cancelled is not None and cancelled():
            raise InterruptedError("提升树训练取消；本次未交付完整多目标模型")
        if deadline is not None and time.monotonic() >= deadline:
            raise TimeoutError("提升树训练预算耗尽；本次未交付完整多目标模型")

    check_stop.before_iteration = True
    check_stop.order = -100
    check_stop()
    backend = _backend()
    if previous is not None and previous["backend_version"] != backend.__version__:
        raise ValueError("接续后端版本须与原生模型一致")
    start = time.monotonic()
    texts, iterations = [], []
    for index in range(targets.shape[1]):
        check_stop()
        dataset = backend.Dataset(points, label=targets[:, index], feature_name=features)
        initial = (
            None
            if previous is None
            else backend.Booster(model_str=previous["model_strings"][index])
        )
        model = backend.train(
            effective,
            dataset,
            num_boost_round=num_boost_round,
            init_model=initial,
            keep_training_booster=True,
            callbacks=[check_stop],
        )
        check_stop()
        texts.append(model.model_to_string(num_iteration=model.current_iteration()))
        iterations.append(model.current_iteration())
    predictor = LightGBMPredictor(
        model_strings=texts,
        feature_names=features,
        target_names=names,
        params=effective,
        training_digest=identity,
        backend_version=backend.__version__,
    )
    return predictor, {
        "backend_version": backend.__version__,
        "params": effective,
        "requested_additional_rounds": num_boost_round,
        "iterations": iterations,
        "initial_iterations": [0] * len(names) if previous is None else previous["iterations"],
        "target_names": names,
        "feature_names": features,
        "training_digest": identity,
        "elapsed_seconds": time.monotonic() - start,
        "completed": True,
        "continuation": previous is not None,
        "exact_resume_verified": False,
    }
