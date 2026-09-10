"""外流实验对照事实：声明、实际模型输入和来源分开记录，不预判可比性。"""

import importlib
import inspect
import platform
from pathlib import Path

import torch

from ai4e_core.abilities.data.validate.fingerprint import (
    file_fingerprint,
    fingerprint,
    source_fingerprint,
)
from ai4e_core.base.events import sample_context
from ai4e_spec.components.model import describe_model

from ..trainprep.preparation import external_inputs


def dataset_fingerprint(index, config):
    """对模型消费的物理字段逐样本取摘要，数据路径不作为内容身份。"""
    bindings = config["trainprep"]
    fields = {bindings["geometry_field"]}
    for domain in bindings["domains"].values():
        fields.add(domain["position"])
        fields.update(domain.get("targets", {}).values())
        if bindings.get("use_physics_features", True):
            fields.update(domain.get("features", {}).values())
    zero_fields = bindings.get("physical_rules", {}).get("zero_fields", {})
    fields -= zero_fields.keys()
    records = {}
    for partition, names in index.partitions.items():
        records[partition] = []
        for item, name in enumerate(names):
            with sample_context("对照输入读取", [{"sample_id": name, "index": item}]):
                values = index.read(partition, item)
                records[partition].append(
                    [name, fingerprint({field: values[field] for field in fields})]
                )
    conditions = external_inputs(config)
    if conditions:
        return fingerprint({"samples": records, "external_conditions": conditions})
    return fingerprint(records)


def describe(
    config, index, normalization, model, construct, *, initial=None, dataset=None, entrypoint=None
):
    """生成由运行实际状态确定的元信息；旧检查点缺少初始化事实时保留未知。"""
    module = importlib.import_module(construct.__module__.split(".")[0])
    import ai4e_core

    execution = config.get("execution", {})
    script = entrypoint or execution.get("script")
    return {
        "version": 1,
        "dataset": dataset or dataset_fingerprint(index, config),
        "partitions": index.partitions,
        "normalization": normalization.record,
        "layout": describe_model(construct, model)["input_layout"],
        "model": {
            key: value
            for key, value in config["model"].items()
            if key not in {"initial_weights", "freeze"}
        },
        "initialization": initial,
        "sampling": config["sampling"],
        "bindings": config["trainprep"],
        "training": {
            key: value
            for key, value in config["train"].items()
            if key
            not in {
                "manifest",
                "preparation",
                "resume",
                "device",
                "snapshot",
                "log_every",
                "log_every_updates",
            }
        },
        "weights": fingerprint(model.state_dict()),
        "inference": {
            key: config.get("post", {}).get(key)
            for key in ("split", "query_chunk_size", "random_stream")
        },
        "execution": {
            "device": str(next(model.parameters()).device),
            "precision": config["train"].get("precision", "fp32"),
            "torch": torch.__version__,
            "python": platform.python_version(),
            "entrypoint": script or "unknown",
            "constructor": f"{construct.__module__}.{construct.__name__}",
        },
        "source": {
            "core": source_fingerprint(Path(inspect.getfile(ai4e_core)).parent),
            "model": source_fingerprint(Path(inspect.getfile(module)).parent),
            "entrypoint": file_fingerprint(script) if script and Path(script).is_file() else None,
        },
        "inputs": {"evaluation": [], "predictions": [], "mesh": []},
    }


def record_inputs(protocol, branch, samples, inputs, positions=None, features=None):
    """记录实际前向消费内容的摘要；完整网格也包含几何与锚点条件。"""
    protocol["inputs"][branch].append(
        {
            "samples": samples,
            "digest": fingerprint({"inputs": inputs, "positions": positions, "features": features}),
        }
    )
