"""训练中当前模型的单样本物理快照，不读取磁盘检查点。"""

from __future__ import annotations

from copy import deepcopy
from time import perf_counter
from types import SimpleNamespace
from typing import Any

import torch

from ai4e_core.abilities.data.validate.fingerprint import fingerprint
from ai4e_core.abilities.inference.execution import inference_execution

from .stage import InferenceSample, configure_physical_output, configure_prediction


def predict_snapshot(
    model: torch.nn.Module,
    *,
    prepared: Any,
    model_component: Any,
    sample: str,
    split: str,
    origin: dict,
    dataset_component: Any = None,
) -> dict:
    """借用当前模型预测一次；返回独立 CPU 字段并恢复模式与随机流。"""
    names = prepared.view.partitions.get(split, [])
    if sample not in names:
        raise ValueError("快照样本不属于指定准备分片")
    started = perf_counter()
    config = deepcopy(prepared.config)
    # 采样与解码仍由同一模型组件解释；不改训练中的准备或配置。
    config.setdefault("infer", {})
    job = SimpleNamespace(
        config=config,
        data=prepared,
        model=model,
        model_component=model_component,
        dataset_component=dataset_component,
        steps=[],
        extensions={},
    )
    with inference_execution(model, preserve_rng=True):
        torch.manual_seed(config["sampling"]["seed"])
        item = InferenceSample(sample, prepared.view.read(split, names.index(sample)))
        configure_prediction(job)
        configure_physical_output(job)
        for _, operation in job.steps:
            item = operation(item)
        fields = {name: value.detach().cpu().clone() for name, value in item.payloads.items()}
        meshes = {}
        if dataset_component is not None:
            for domain, declaration in item.domains.items():
                meshes[domain] = dataset_component.comparison_mesh(
                    config, sample, domain, fields[declaration["position"]].numpy()
                )
    origin = {**origin, "weights": fingerprint(model.state_dict()), "split": split}
    origin["id"] = fingerprint(origin)
    return {
        "metadata": {
            "identity": {**item.sample["identity"], "sample": sample},
            "domains": item.domains,
        },
        "fields": fields,
        "source_meshes": meshes,
        "origin": origin,
        "timings": {"snapshot_seconds": perf_counter() - started},
    }
