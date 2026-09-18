"""共享评估执行，保证结束和异常时恢复模型模式与随机流。"""

import random
from contextlib import nullcontext

import numpy as np
import torch

from ai4e_core.abilities.inference.randomness import preserve_randomness

from .metrics import field_metrics, selected_metrics


def evaluate(
    model,
    batches,
    predict,
    objectives,
    normalization,
    *,
    preserve_rng: bool = True,
    batch_context=None,
    metric_names=None,
) -> dict:
    """一次前向计算总分、加权分项和 metric_names 指定的物理指标。

    metric_names=None 保留原三项，空序列仅计算损失；未知或重复项在
    前向前抛 ValueError。返回格式不变，未选项不进入 metrics。
    """
    from ai4e_core.abilities.constraint.supervised import supervised

    selected = selected_metrics(metric_names)
    modes = {module: module.training for module in model.modules()}
    python_rng, numpy_rng = random.getstate(), np.random.get_state()
    totals, named, metrics = [], {}, {}
    sample_count = 0
    try:
        with preserve_randomness() if preserve_rng else nullcontext(), torch.no_grad():
            model.eval()
            for batch in batches:
                with batch_context(batch) if batch_context else nullcontext():
                    predictions = predict(model, batch["inputs"])
                    count = next(iter(predictions.values())).shape[0]
                    sample_count += count
                    results = [
                        supervised(
                            {k: v[i : i + 1] for k, v in predictions.items()},
                            {k: v[i : i + 1] for k, v in batch["targets"].items()},
                            objectives,
                        )
                        for i in range(count)
                    ]
                    totals.extend(result["loss"].item() for result in results)
                    for objective in objectives:
                        name = objective["name"]
                        weight = float(objective.get("weight", 1.0))
                        named[name] = named.get(name, 0.0) + sum(
                            weight * result["losses"][name].item() for result in results
                        )
                        if not selected:
                            continue
                        prediction = predictions[objective["prediction"]]
                        target = batch["targets"][objective["target"]]
                        field = objective.get("normalization", objective["prediction"])
                        for pred, truth in zip(prediction, target, strict=True):
                            values = field_metrics(
                                normalization.inverse(field, pred),
                                normalization.inverse(field, truth),
                                metrics=selected,
                            )
                            for key, value in values.items():
                                metrics.setdefault(objective["prediction"] + "/" + key, []).append(
                                    value
                                )
    finally:
        for module, mode in modes.items():
            module.training = mode
        if preserve_rng:
            random.setstate(python_rng)
            np.random.set_state(numpy_rng)
    if not totals:
        raise ValueError("评估分片为空")
    return {
        "loss": sum(totals) / sample_count,
        "losses": {name: value / sample_count for name, value in named.items()},
        "scope": "declared_predictions",
        "metrics": {
            key: {
                "value": sum(v for v in values if v is not None)
                / sum(v is not None for v in values)
                if any(v is not None for v in values)
                else None,
                "valid": sum(v is not None for v in values),
                "skipped": sum(v is None for v in values),
            }
            for key, values in metrics.items()
        },
    }
