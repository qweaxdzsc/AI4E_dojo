"""物理场评价目录；公式和数值方向由算法层统一提供。"""

DEFAULT_METRICS = ["relative_l2", "mae", "rmse", "max_abs_error", "r2"]
DEFINITIONS = {
    "relative_l2": ("相对 L2", "误差指标", "||p-t||₂ / ||t||₂", "1", "min"),
    "mae": ("MAE", "误差指标", "mean(|p-t|)", "field", "min"),
    "rmse": ("RMSE", "误差指标", "sqrt(mean((p-t)²))", "field", "min"),
    "max_abs_error": ("Max Error", "误差指标", "max(|p-t|)", "field", "min"),
    "r2": ("R²", "统计指标", "1-sum((p-t)²)/sum((t-mean(t))²)", "1", "max"),
    "mse": ("MSE", "误差指标", "mean((p-t)²)", "field_squared", "min"),
    "relative_mae": ("相对 MAE", "误差指标", "sum(|p-t|)/sum(|t|)", "1", "min"),
    "mean_relative_error": (
        "平均逐点相对误差",
        "误差指标",
        "mean(|p-t|/|t|)，排除近零真值",
        "1",
        "min",
    ),
    "mape": ("MAPE 百分比误差", "误差指标", "100 × mean(|p-t|/|t|)，排除近零真值", "%", "min"),
}
METRICS = {key: item[0] for key, item in DEFINITIONS.items()}


def metric_catalog() -> list[dict]:
    """返回可执行的场指标及固定计时信息，缺失物理量不补造。"""
    return [
        {
            "id": key,
            "label": label,
            "category": category,
            "formula": formula,
            "unit_rule": unit,
            "direction": direction,
            "scope": "field",
            "default": key in DEFAULT_METRICS,
            "algorithm": "physical-metrics-v2",
        }
        for key, (label, category, formula, unit, direction) in DEFINITIONS.items()
    ] + [
        {
            "id": "prediction_seconds",
            "label": "预测耗时",
            "category": "性能指标",
            "formula": "设备同步后的样本预测时间",
            "unit_rule": "s",
            "scope": "sample",
            "default": False,
        },
        {
            "id": "throughput",
            "label": "预测吞吐量",
            "category": "性能指标",
            "formula": "成功样本数 / 预测总时间",
            "unit_rule": "sample/s",
            "scope": "sample",
            "default": False,
        },
    ]
