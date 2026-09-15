"""训练准备的公开步骤：冻结变换与数据身份，采样仍在每次迭代执行。"""

import hashlib
import inspect
import json
from copy import deepcopy
from dataclasses import dataclass, field
from functools import partial
from pathlib import Path

from ai4e_core.abilities.data.save.normalization import materialize, save_record
from ai4e_core.abilities.data.source.manifest import ManifestIndex
from ai4e_core.abilities.data.source.split import apply_declared_split, default_counts
from ai4e_core.base.config import operation_record, plain, resolve_operation
from ai4e_core.base.config.steps import restore_operation

from .dataset import iter_partition_batches, prepare_physical_sample
from .normalization import Normalization, bind_normalization, validate_frozen


def digest(value: dict) -> str:
    """计算与 JSON 键排列无关的交付摘要。"""
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def component_record(component) -> dict:
    """冻结入口名称及其源码内容，安装位置不参与摘要。"""
    if isinstance(component, partial) or not inspect.isfunction(component):
        return operation_record(component)
    path = inspect.getsourcefile(component)
    if path is None:
        raise ValueError("准备组件必须有可快照的 Python 源码")
    return {
        "name": component.__module__ + "." + component.__qualname__,
        "sha256": hashlib.sha256(Path(path).read_bytes()).hexdigest(),
    }


def external_inputs(config: dict) -> dict:
    """条件文件按内容冻结，防止同路径替换造成静默输入变化。"""
    result = {}
    for group in ("conditioning", "geometry_conditioning"):
        for name, declaration in config["trainprep"].get(group, {}).items():
            if isinstance(declaration, dict) and "path" in declaration:
                result[group + "/" + name] = hashlib.sha256(
                    Path(declaration["path"]).read_bytes()
                ).hexdigest()
    return result


def dataset_digest(index: ManifestIndex) -> str:
    """流式核对清单与实际张量字节，捕获原地替换数据。"""
    return index.content_digest()


@dataclass
class Preparation:
    """一次准备的业务状态；只持久化 record，不持久化函数或张量。"""

    config: dict
    index: ManifestIndex
    normalization: Normalization | None = None
    physical_prepare: object = None
    prepare: object = None
    collate: object = None
    record: dict = field(default_factory=dict)


def open_dataset(config: dict, dataset=None, overlay=None) -> Preparation:
    """打开 datapre 产物或已有清单，独立入口无需执行原始数据处理。"""
    config = deepcopy(config)
    path = (
        config["train"].get("manifest")
        or Path(config["paths"]["datasets"]["root"]) / "manifest.json"
    )
    if dataset is not None:
        path = Path(dataset["output"]["root"]) / "manifest.json"
        config["train"]["manifest"] = str(path)
    index = ManifestIndex(path)
    apply_declared_split(index, config, overlay)
    if not index.partitions.get("train"):
        raise ValueError("训练分片缺失")
    return Preparation(config, index)


def prepare_fields(data: Preparation) -> Preparation:
    """按公开物理字段规则配置准备函数，不预先抽样。"""
    data.physical_prepare = partial(
        prepare_physical_sample, rules=data.config["trainprep"].get("physical_rules", {})
    )
    return data


def bind_fields(data: Preparation, *, settings=None) -> Preparation:
    """公开字段绑定步骤；用户配置中的归一化和采样另由相应步骤消费。"""
    if settings is not None:
        values = plain(settings)
        values.pop("normalization", None)
        values.pop("sampling", None)
        data.config["trainprep"] = values
    return prepare_fields(data)


def freeze_normalization(data: Preparation, *, settings=None) -> Preparation:
    """绑定实际统计值或已有冻结记录；不把归一化数据再次变换。"""
    if settings is not None:
        data.config["normalization"] = plain(settings)
    manifest = data.index.manifest
    if manifest["state"] == "normalized":
        data.normalization = Normalization(manifest["normalization"])
        if data.normalization.digest != manifest["normalization_digest"]:
            raise ValueError("归一化数据摘要冲突")
    else:
        data.normalization = bind_normalization(data.config, manifest, data.index)
    validate_frozen(data.config, data.normalization)
    return data


def configure_sampling(
    data: Preparation, *, prepare=None, settings=None, model_component=None, operation=None
) -> Preparation:
    """注入模型样本组织组件；每个 epoch 的采样由训练迭代器调用。"""
    if settings is not None:
        data.config["sampling"] = plain(settings)
    default = prepare or (model_component.prepare_inputs if model_component else None)
    data.prepare = resolve_operation(data.config["sampling"], default=default, operation=operation)
    return data


def configure_batching(
    data: Preparation, *, collate=None, batch_size=None, model_component=None
) -> Preparation:
    """注入模型拼批组件，保留跨样本索引偏移契约。"""
    if batch_size is not None:
        data.config["train"]["batch_size"] = batch_size
    data.collate = collate or model_component.collate
    return data


def validate_preparation(data: Preparation) -> Preparation:
    """逐样本校验全部已声明分片，不把随机探测结果作为训练数据缓存。"""
    import torch

    # 准备检查不推进训练随机流。
    with torch.random.fork_rng(devices=[]):
        for partition, samples in data.index.partitions.items():
            if not samples:
                continue
            for _batch in iter_partition_batches(
                data.index,
                partition,
                prepare=data.prepare,
                collate=data.collate,
                normalization=data.normalization,
                physical_prepare=data.physical_prepare,
                normalized_input=data.index.manifest["state"] == "normalized",
                sampling=data.config["sampling"],
                config=data.config,
                batch_size=int(data.config["train"]["batch_size"]),
                device=torch.device("cpu"),
                evaluation=True,
            ):
                pass
    data.record = {
        "version": 2,
        "manifest": str(data.index.path.resolve()),
        "dataset_digest": dataset_digest(data.index),
        "normalization": data.normalization.record,
        "normalization_digest": data.normalization.digest,
        "declarations": declarations(data.config),
        "external_inputs": external_inputs(data.config),
        "components": {
            name: component_record(component)
            for name, component in [("prepare", data.prepare), ("collate", data.collate)]
        },
        "split_counts": {name: len(samples) for name, samples in data.index.partitions.items()},
        "partitions": {name: list(samples) for name, samples in data.index.partitions.items()},
        "split": deepcopy((data.config.get("trainprep") or {}).get("split"))
        or {
            "method": "original",
            "seed": 0,
            "counts": default_counts(data.index.partitions),
        },
    }
    return data


def declarations(config: dict) -> dict:
    """影响模型实际输入的公开声明，用于阻止跨阶段隐式覆盖。"""
    return deepcopy(
        {
            "sampling": config["sampling"],
            "trainprep": config["trainprep"],
            "data_specs": config["model"]["data_specs"],
            "geometry_conditioning_dims": config["model"]
            .get("parameters", {})
            .get("geometry_conditioning_dims"),
            "batch_size": config["train"]["batch_size"],
        }
    )


def publish(data: Preparation, run=None, *, session=None) -> dict:
    """发布可独立消费的准备引用；检查模式不写归一化或阶段产物。"""
    run = session or run
    if not data.record:
        raise ValueError("发布前必须校验准备结果")
    if run.dry_run:
        result = {"mode": "trainprep_check", "split_counts": data.record["split_counts"]}
    else:
        cfg = data.config
        save_record(
            cfg["paths"]["datasets"]["normalize"]["root"],
            data.normalization.digest,
            data.normalization.record,
        )
        if cfg["normalization"].get("materialize") and data.index.manifest["state"] == "physical":
            materialize(
                data.index,
                data.normalization,
                cfg["paths"]["datasets"]["normalize"],
                data.physical_prepare,
            )
        record = {**data.record, "digest": digest(data.record)}
        path = run.artifact("preparation.json", record)
        result = {
            "mode": "trainprep",
            "preparation": str(path),
            "digest": record["digest"],
            "split_counts": record["split_counts"],
        }
    run.report(result, stage="trainprep")
    return result


def check_report(data, *, session):
    """准备检查报告，不发布任何持久化阶段产物。"""
    if not data.record:
        raise ValueError("检查前必须校验准备")
    result = {"mode": "trainprep_check", "split_counts": data.record["split_counts"]}
    session.report(result, stage="trainprep")
    return result


def consume(config: dict, reference, *, prepare, collate) -> Preparation:
    """从准备引用恢复并验证配置、组件和数据；不再读取原统计文件。"""
    prepare = resolve_operation(config["sampling"], default=prepare)
    path = reference["preparation"] if isinstance(reference, dict) else reference
    record = json.loads(Path(path).read_text())
    payload = {key: value for key, value in record.items() if key != "digest"}
    if record.get("version") != 2 or digest(payload) != record.get("digest"):
        raise ValueError("准备结果版本或摘要不一致")
    if record["declarations"] != declarations(config):
        raise ValueError("配置与准备结果冲突，请重新运行 trainprep")
    if (
        not config["sampling"].get("target")
        and record["components"]["prepare"]["name"] != component_record(prepare)["name"]
    ):
        prepare = restore_operation(record["components"]["prepare"])
    if record["components"]["collate"]["name"] != component_record(collate)["name"]:
        collate = restore_operation(record["components"]["collate"])
    if record["components"] != {
        name: component_record(component)
        for name, component in [("prepare", prepare), ("collate", collate)]
    }:
        raise ValueError("准备组件发生变化")
    if record["external_inputs"] != external_inputs(config):
        raise ValueError("准备后条件文件已变化，请重新运行 trainprep")
    requested = config["train"].get("manifest")
    if requested and Path(requested).resolve() != Path(record["manifest"]).resolve():
        raise ValueError("训练清单与准备结果冲突")
    cfg = deepcopy(config)
    cfg["train"]["manifest"] = record["manifest"]
    data = prepare_fields(open_dataset(cfg, overlay=record.get("partitions")))
    if dataset_digest(data.index) != record["dataset_digest"]:
        raise ValueError("准备后数据已变化，请重新运行 trainprep")
    data.normalization = Normalization(record["normalization"])
    if data.normalization.digest != record["normalization_digest"]:
        raise ValueError("准备归一化摘要不一致")
    validate_frozen(config, data.normalization)
    data.prepare, data.collate, data.record = prepare, collate, record
    return data
