"""主控串行统计代理验收：独立参考、固定状态恢复及真实物理量评价。

导入不启动拟合；每次run_classical只执行一个组合。deadline由累计预算账本
提供，单次BLAS/原生树的硬截止由外层进程执行。绝不根据测试误差调参。
"""

from __future__ import annotations

import json
import time
from copy import deepcopy
from pathlib import Path

import numpy as np

from ai4e_contrib.application.surrogate_modeling.fitting import fit_predictor
from ai4e_contrib.application.surrogate_modeling.prediction import predict_prepared, rebuild
from ai4e_contrib.application.surrogate_modeling.preparation import (
    preparation_identity,
    read_pod,
    read_prepared,
)
from ai4e_core.abilities.data.save.array_manifest import read_arrays, save_arrays
from ai4e_core.abilities.data.save.arrays import save_json
from ai4e_core.abilities.data.save.surrogate import read_state, save_state

from . import reference_algebraic as algebraic
from . import reference_statistical as statistical

# 全部为运行前冻结的FP64门槛；拟合非凸优化单独采用较宽但明确的数值门槛。
TOLERANCES = {
    "algebraic": {"rtol": 1e-7, "atol": 1e-9},
    "pod_projection": {"rtol": 1e-7, "atol": 1e-9},
    "pod_coordinates": {"rtol": 1e-6, "atol": 1e-8},
    "kriging_fixed": {"rtol": 1e-7, "atol": 1e-9},
    "kriging_optimized": {"rtol": 2e-3, "atol": 2e-5},
    "kriging_objective": {"rtol": 1e-4, "atol": 1e-5},
    "lightgbm": {"rtol": 0.0, "atol": 1e-12},
    "state_reload": {"rtol": 0.0, "atol": 0.0},
}


def _json(value):
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, dict):
        return {str(k): _json(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json(v) for v in value]
    return value


def _guard(deadline, cancelled):
    if cancelled is not None and cancelled():
        raise InterruptedError("统一统计代理校验取消")
    if time.monotonic() >= deadline:
        raise TimeoutError("本组合累计时限已用尽")


def _compare(actual, reference, tolerance):
    actual, reference = np.asarray(actual), np.asarray(reference)
    np.testing.assert_allclose(actual, reference, equal_nan=False, **TOLERANCES[tolerance])
    difference = actual - reference
    return {
        "max_absolute_error": float(np.max(abs(difference))),
        "relative_l2": float(np.linalg.norm(difference) / max(np.linalg.norm(reference), 1e-30)),
        "tolerance": dict(TOLERANCES[tolerance]),
    }


def _metrics(prediction, target, valid, fields):
    prediction, target = np.asarray(prediction), np.asarray(target)
    if prediction.shape != target.shape or valid.shape != target.shape[:-1]:
        raise ValueError("评价预测/目标/有效标记布局不匹配")
    if not np.isfinite(prediction).all() or not np.isfinite(target).all() or not np.any(valid):
        raise ValueError("评价须具有有限预测/真值与有效实体")
    p, t = prediction[valid], target[valid]
    result = {}
    for index, field in enumerate(fields):
        delta = p[:, index] - t[:, index]
        norm = float(np.linalg.norm(t[:, index]))
        result[field] = {
            "mae": float(np.mean(abs(delta))),
            "rmse": float(np.sqrt(np.mean(delta**2))),
            "relative_l2": None if norm <= 1e-14 else float(np.linalg.norm(delta) / norm),
            "relative_l2_available": norm > 1e-14,
        }
    return result


def _parameters(family, meta, supplied):
    defaults = {
        "rsm": {"degree": 2, "ridge": 0.0},
        "rbf": {"kernel": "cubic", "degree": 1, "smoothing": 1e-5},
        "kriging": {
            "trend_degree": 0,
            "kernel_config": {"length_scale": 1.0, "variance": 1.0},
            "noise_variance": 1e-4,
            "jitter": 1e-10,
            "optimization": {
                "maxiter": 200,
                "maxfun": 1000,
                "ftol": 1e-8,
                "gtol": 1e-5,
                "length_scale_bounds": [0.1, 10.0],
                "variance_bounds": [0.001, 100.0],
            },
        },
        "lightgbm": {
            "num_boost_round": 12,
            "feature_names": meta.get("input_fields"),
            "target_names": meta["fields"],
            "params": {
                "learning_rate": 0.1,
                "num_leaves": 7,
                "min_data_in_leaf": 8,
                "objective": "regression",
                "boosting_type": "gbdt",
                "deterministic": True,
                "force_col_wise": True,
                "num_threads": 1,
                "seed": 42,
                "verbosity": -1,
            },
        },
    }
    result = deepcopy(defaults[family])
    for key, value in (supplied or {}).items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key].update(deepcopy(value))
        else:
            result[key] = deepcopy(value)
    return result


def _pod_reference(prepared, records, arrays, deadline, cancelled):
    pod, context = read_pod(prepared)
    meta = records["train"]["metadata"]
    stats = meta["statistics"]["target"]
    mean, scale = np.asarray(stats["mean"]), np.asarray(stats["scale"])
    snapshots = {}
    for row, identity in enumerate(meta["ids"]):
        trajectory, _ = identity.rsplit("_", 1)
        frames = [*arrays["train"]["physical_input"][row], arrays["train"]["physical_target"][row]]
        for instant, frame in zip(arrays["train"]["times"][row], frames, strict=True):
            key = (trajectory, float(instant))
            snapshot = np.array(frame, dtype=np.float64, copy=True)
            if key in snapshots and not np.array_equal(snapshots[key], snapshot):
                raise ValueError("独立参考发现同时间快照不一致")
            snapshots[key] = snapshot
    if [[name, instant] for name, instant in snapshots] != context["fit_snapshot_ids"]:
        raise ValueError("独立参考去重训练帧身份与POD状态不一致")
    normalized = ((np.stack(list(snapshots.values())) - mean) / scale).reshape(len(snapshots), -1)
    _guard(deadline, cancelled)
    oracle = algebraic.fit_pod(normalized, meta["rank"])
    _guard(deadline, cancelled)
    # 先比较独立SVD物理投影；对齐只消除已等价子空间中的符号/简并旋转。
    projection = _compare(
        pod.reconstruct(normalized), oracle.reconstruct(normalized), "pod_projection"
    )
    product_basis = pod.to_state()["basis"]
    u, _, vh = np.linalg.svd(oracle.basis.T @ product_basis, full_matrices=False)
    alignment = u @ vh
    oracle.basis = oracle.basis @ alignment
    aligned = _compare(oracle.basis, product_basis, "pod_projection")
    encoded = {}
    for split in ("train", "test"):
        data = arrays[split]
        history = ((np.asarray(data["physical_input"], dtype=np.float64) - mean) / scale).reshape(
            len(data["input"]), 3, -1
        )
        future = ((np.asarray(data["physical_target"], dtype=np.float64) - mean) / scale).reshape(
            len(data["input"]), -1
        )
        encoded[split] = {
            "input": oracle.encode(history).reshape(len(history), -1),
            "target": oracle.encode(future),
        }
    input_mean = encoded["train"]["input"].mean(0)
    input_scale = encoded["train"]["input"].std(0)
    input_scale = np.where(input_scale > 0, input_scale, 1.0)
    coordinates = {}
    for split in ("train", "test"):
        encoded[split]["input"] = (encoded[split]["input"] - input_mean) / input_scale
        coordinates[split] = {
            name: _compare(encoded[split][name], arrays[split][name], "pod_coordinates")
            for name in ("input", "target")
        }
    shape = meta["field_shape"]
    target = arrays["test"]["physical_target"]
    truncation = oracle.decode(encoded["test"]["target"]).reshape(target.shape) * scale + mean
    return (
        oracle,
        encoded,
        {
            "projection": projection,
            "aligned_basis": aligned,
            "alignment": alignment.tolist(),
            "coordinate_comparison": coordinates,
            "unique_training_snapshots": len(snapshots),
            "rank": meta["rank"],
            "field_shape": shape,
            "test_truncation_metrics": _metrics(
                truncation, target, arrays["test"]["valid"], meta["fields"]
            ),
        },
    )


def _reference(family, train, test, params, deadline, cancelled):
    _guard(deadline, cancelled)
    x, y, q = train["input"], train["target"], test["input"]
    if family == "rsm":
        model = algebraic.fit_rsm(x, y, **params)
        result = {"prediction": model.predict(q)}
    elif family == "rbf":
        model = algebraic.fit_rbf(x, y, **params)
        result = {"prediction": model(q)}
    elif family == "kriging":
        reports = []
        for column in range(y.shape[1]):
            options = deepcopy(params)
            degree = options.pop("trend_degree")
            reports.append(
                statistical.fit_kriging_reference(
                    x,
                    y[:, column],
                    q,
                    degree=degree,
                    deadline=deadline,
                    cancelled=cancelled,
                    **options,
                )
            )
        result = {
            "prediction": np.column_stack([r["mean"] for r in reports]),
            "variance": np.column_stack([r["variance"] for r in reports]),
            "reports": reports,
        }
    else:
        result = statistical.lightgbm_reference(
            x,
            y,
            q,
            params=params["params"],
            num_boost_round=params["num_boost_round"],
            feature_names=params["feature_names"],
            deadline=deadline,
            cancelled=cancelled,
        )
    _guard(deadline, cancelled)
    return result


def run_classical(family, prepared, output, deadline, *, parameters=None, cancelled=None):
    """串行校验NASA四类或双圆柱POD-RBF/Kriging，返回JSON兼容指标与证据路径。

    prepared为自包含代理准备manifest，POD已由主控预算内串行准备。output须
    不存在；失败保留failure.json后抛异常。阈值事前固定，失败不得静默放宽。
    LightGBM附原生追加2轮及同参数不中断对照；不虚构优化器任意步恢复。
    """
    if family not in {"rsm", "rbf", "kriging", "lightgbm"}:
        raise ValueError("未知传统代理模型")
    if not np.isscalar(deadline) or not np.isfinite(deadline):
        raise ValueError("须传主控monotonic绝对截止")
    _guard(deadline, cancelled)
    root = Path(output).resolve()
    root.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    stage = "read_preparation"
    try:
        records, arrays = {}, {}
        for split in ("train", "test"):
            records[split], arrays[split] = read_prepared(prepared, split)
        meta = records["train"]["metadata"]
        if records["test"]["metadata"]["fields"] != meta["fields"]:
            raise ValueError("训练和测试字段次序不同")
        case = meta["case"]
        if case == "double_cylinder_pod" and family not in {"rbf", "kriging"}:
            raise ValueError("本批降阶验证只登记RBF/Kriging")
        params = _parameters(family, meta, parameters)
        save_json(
            root / "protocol.json",
            {
                "case": case,
                "family": family,
                "parameters": _json(params),
                "tolerances": TOLERANCES,
                "train_ids": meta["ids"],
                "test_ids": records["test"]["metadata"]["ids"],
                "deadline_monotonic": float(deadline),
                "paper_reproduction": False,
            },
        )
        pod_report, pod_reference = None, None
        reference_arrays = arrays
        if case == "double_cylinder_pod":
            stage = "independent_pod"
            pod_reference, reference_arrays, pod_report = _pod_reference(
                prepared, records, arrays, deadline, cancelled
            )
        stage = "independent_reference"
        reference = _reference(
            family, reference_arrays["train"], reference_arrays["test"], params, deadline, cancelled
        )
        save_state(
            root / "reference_candidate",
            reference,
            context={"case": case, "family": family, "parameters": _json(params)},
        )
        stage = "dojo_fit"
        model, state, diagnostics = fit_predictor(
            family,
            arrays["train"]["input"],
            arrays["train"]["target"],
            params,
            deadline=deadline,
            cancelled=cancelled,
        )
        save_state(
            root / "candidate_model",
            state,
            context={
                "case": case,
                "family": family,
                "parameters": _json(params),
                "preparation_identity": preparation_identity(prepared),
            },
        )
        save_json(root / "candidate_diagnostics.json", _json(diagnostics))
        if family == "kriging" and not all(
            item["success"] for item in diagnostics["targets"] + reference["reports"]
        ):
            raise AssertionError("正式克里金拟合须明确收敛；预算停止不能冒充完成")
        _guard(deadline, cancelled)
        predicted = model.predict(arrays["test"]["input"])
        comparison = _compare(
            predicted,
            reference["prediction"],
            "kriging_optimized"
            if family == "kriging"
            else "lightgbm"
            if family == "lightgbm"
            else "algebraic",
        )
        variance_report = None
        if family == "kriging":
            stage = "kriging_variance"
            _, variance = model.predict(arrays["test"]["input"], return_variance=True)
            if np.min(variance) < 0:
                raise AssertionError("潜在响应方差不得为负")
            fixed, objectives = [], []
            for column, part in enumerate(model.models):
                covariance = part.covariance
                condition = part.condition.get_state()
                oracle = statistical.kriging_reference(
                    arrays["train"]["input"],
                    arrays["train"]["target"][:, column],
                    arrays["test"]["input"],
                    length_scale=covariance.length_scale,
                    variance=covariance.variance,
                    degree=params["trend_degree"],
                    noise_variance=params["noise_variance"],
                    jitter=params["jitter"],
                )
                fixed.append(
                    {
                        "mean": _compare(predicted[:, column], oracle["mean"], "kriging_fixed"),
                        "variance": _compare(
                            variance[:, column], oracle["variance"], "kriging_fixed"
                        ),
                        "noise_variance": condition["noise_variance"].tolist(),
                        "jitter": condition["jitter"],
                    }
                )
                objectives.append(
                    _compare(
                        diagnostics["targets"][column]["nll"],
                        reference["reports"][column]["nll"],
                        "kriging_objective",
                    )
                )
            variance_report = {
                "minimum": float(np.min(variance)),
                "scope": "latent response; plug-in hyperparameters; independent outputs",
                "fixed_parameter_reference": fixed,
                "optimized_objectives": objectives,
                "optimizer_resume_verified": False,
            }
            variance_arrays = {"latent_variance": variance}
            variance_metadata = {
                "case": case,
                "space": "pod_coefficients"
                if case == "double_cylinder_pod"
                else "standardized_targets",
                "scope": "independent scalar latent posteriors; excludes observation noise and optimizer uncertainty",
            }
            if case == "nasa_global":
                variance_arrays["physical_variance"] = (
                    variance[:, None, :] * np.asarray(meta["statistics"]["target"]["scale"]) ** 2
                )
                variance_metadata["physical_variance_units"] = [
                    f"({unit})^2" for unit in meta["units"]
                ]
            variance_report["path"] = save_arrays(
                root / "variance",
                variance_arrays,
                kind="surrogate-variance-v1",
                metadata=variance_metadata,
            )
            _, variance_readback = read_arrays(
                variance_report["path"], kind="surrogate-variance-v1"
            )
            variance_report["fixed_variance_readback"] = _compare(
                variance_readback["latent_variance"], variance, "state_reload"
            )
        stage = "state_roundtrip"
        context = {
            "case": case,
            "family": family,
            "fields": meta["fields"],
            "input_fields": meta.get("input_fields"),
            "statistics": meta["statistics"],
            "preparation_identity": preparation_identity(prepared),
            "parameters": _json(params),
        }
        state_path = save_state(root / "model", state, context=context)
        loaded, loaded_context = read_state(state_path)
        if loaded_context != context:
            raise AssertionError("保存元信息读回不一致")
        restored = rebuild(loaded)
        reload_comparison = _compare(
            restored.predict(arrays["test"]["input"]), predicted, "state_reload"
        )
        if family == "kriging":
            variance_report["reload"] = _compare(
                restored.predict(arrays["test"]["input"], return_variance=True)[1],
                variance,
                "state_reload",
            )
        continuation = None
        if family == "lightgbm":
            from ai4e_core.abilities.training.boosting import fit_boosting

            stage = "lightgbm_native_continuation"
            continued, continuation_report = fit_boosting(
                arrays["train"]["input"],
                arrays["train"]["target"],
                target_names=restored.target_names,
                feature_names=restored.feature_names,
                params=restored.params,
                num_boost_round=2,
                initial_model=restored,
                deadline=deadline,
                cancelled=cancelled,
            )
            full_reference = statistical.lightgbm_reference(
                arrays["train"]["input"],
                arrays["train"]["target"],
                arrays["test"]["input"],
                params=restored.params,
                num_boost_round=params["num_boost_round"] + 2,
                feature_names=restored.feature_names,
                deadline=deadline,
                cancelled=cancelled,
            )
            continued_prediction = continued.predict(arrays["test"]["input"])
            exact = _compare(continued_prediction, full_reference["prediction"], "lightgbm")
            if any(
                new - old != 2
                for old, new in zip(restored.iterations, continued.iterations, strict=True)
            ):
                raise AssertionError("本次原生模型未实际追加2轮，不能作为追加训练验收")
            continuation_path = save_state(
                root / "continued_model", continued.get_state(), context=context
            )
            continuation_state, _ = read_state(continuation_path)
            continuation = {
                "report": continuation_report,
                "uninterrupted_reference": exact,
                "reload": _compare(
                    rebuild(continuation_state).predict(arrays["test"]["input"]),
                    continued_prediction,
                    "state_reload",
                ),
                "additional_actual_iterations": [
                    b - a for a, b in zip(restored.iterations, continued.iterations, strict=True)
                ],
                "state_path": continuation_path,
                "exact_for_this_fixed_run": True,
            }
        stage = "fixed_results"
        _guard(deadline, cancelled)
        results_path = predict_prepared(loaded, prepared, root / "results")
        result_record, results = read_arrays(results_path, kind="classic-results-v1")
        if family == "kriging":
            uncertainty = result_record["metadata"]["uncertainty"]
            name = "latent_variance" if case == "nasa_global" else "coefficient_latent_variance"
            if uncertainty["array"] != name:
                raise AssertionError("固定结果方差的空间声明错误")
            expected_variance = (
                variance[:, None, :] * np.asarray(meta["statistics"]["target"]["scale"]) ** 2
                if case == "nasa_global"
                else variance
            )
            variance_report["product_fixed_result"] = _compare(
                results[name], expected_variance, "state_reload"
            )
        stats = meta["statistics"]["target"]
        scale, mean = np.asarray(stats["scale"]), np.asarray(stats["mean"])
        if pod_reference is None:
            reference_physical = reference["prediction"][:, None, :] * scale + mean
        else:
            reference_physical = (
                pod_reference.decode(reference["prediction"]).reshape(results["target"].shape)
                * scale
                + mean
            )
        physical_comparison = _compare(
            results["prediction"],
            reference_physical,
            "kriging_optimized"
            if family == "kriging"
            else "lightgbm"
            if family == "lightgbm"
            else "algebraic",
        )
        reference_path = save_arrays(
            root / "reference",
            {
                "prediction": reference_physical,
                "target": results["target"],
                "valid": results["valid"],
            },
            kind="surrogate-reference-v1",
            metadata={"case": case, "family": family, "fields": meta["fields"]},
        )
        _, reference_readback = read_arrays(reference_path, kind="surrogate-reference-v1")
        _compare(reference_readback["prediction"], reference_physical, "state_reload")
        _guard(deadline, cancelled)
        report = _json(
            {
                "status": "passed",
                "case": case,
                "family": family,
                "parameters": params,
                "tolerances": TOLERANCES,
                "diagnostics": diagnostics,
                "reference_comparison": comparison,
                "physical_reference_comparison": physical_comparison,
                "reload": reload_comparison,
                "variance": variance_report,
                "pod": pod_report,
                "continuation": continuation,
                "metrics": _metrics(
                    results["prediction"],
                    results["target"],
                    results["valid"],
                    result_record["metadata"]["fields"],
                ),
                "reference_metrics": _metrics(
                    reference_physical, results["target"], results["valid"], meta["fields"]
                ),
                "sources": {
                    "algebraic": algebraic.source_identity(),
                    "statistical": statistical.SOURCES,
                },
                "reference_fit_diagnostics": [
                    {
                        key: value
                        for key, value in item.items()
                        if key not in {"mean", "variance", "beta"}
                    }
                    for item in reference.get("reports", [])
                ],
                "train_samples": len(arrays["train"]["input"]),
                "test_samples": len(arrays["test"]["input"]),
                "state_path": state_path,
                "results_path": results_path,
                "reference_path": reference_path,
                "elapsed_seconds": time.monotonic() - start,
                "paper_reproduction": False,
                "prediction_resume_verified": True,
            }
        )
        json.dumps(report, allow_nan=False)
        save_json(root / "report.json", report)
        return report
    except Exception as error:
        save_json(
            root / "failure.json",
            {
                "status": "failed",
                "stage": stage,
                "family": family,
                "error_type": type(error).__name__,
                "error": str(error),
                "elapsed_seconds": time.monotonic() - start,
            },
        )
        raise
