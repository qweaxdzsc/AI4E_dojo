"""跨模型物理准备的公开步骤；冻结身份与变换，采样在训练迭代发生。"""

import json
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path

from ai4e_core.abilities.data.source.split import apply_declared_split
from ai4e_core.abilities.data.stats.physical import freeze
from ai4e_core.abilities.data.validate.fingerprint import fingerprint
from ai4e_core.abilities.data.validate.physical import validate_bindings
from ai4e_core.abilities.inference.randomness import preserve_randomness
from ai4e_core.abilities.transform.normalization import Normalization
from ai4e_core.base.config import operation_record, plain, resolve_operation
from ai4e_core.base.config.steps import restore_operation


@dataclass
class PhysicalPreparation:
    """准备阶段状态；record 可持久化，运行对象仅保留在内存。"""

    config: dict
    view: object
    model_component: object
    old: dict | None = None
    normalization: object = None
    prepare: object = None
    record: dict | None = None
    bound: bool = False
    batching: bool = False
    extensions: dict | None = None


def open_dataset(config, dataset_component, model_component, reference=None, dataset=None):
    """打开物理清单或已冻结准备引用，不在此拟合变换或进行模型准备。"""
    config = deepcopy(config)
    config.setdefault("train", {})
    if dataset:
        if dataset.get("mode", "").endswith("_check"):
            raise ValueError("检查报告不是数据产物")
        value = dataset["manifest"]
        config["train"]["manifest"] = (
            value
            if isinstance(value, str)
            else str(Path(dataset["output"]["root"]) / "manifest.json")
        )
    if isinstance(reference, dict):
        reference = reference["preparation"]
    old = json.loads(Path(reference).read_text()) if reference else None
    if old and (old.get("version") == 2 or "dataset" not in old):
        raise ValueError("现行准备记录需用 trainprep.preparation 消费，不能走旧物理准备接口")
    if old:
        if not isinstance(old.get("manifest"), str):
            raise ValueError("冻结准备缺少物理数据清单引用")
        requested = config["train"].get("manifest")
        if (
            requested
            and Path(requested).is_file()
            and Path(requested).resolve() != Path(old["manifest"]).resolve()
        ):
            raise ValueError("已选物理清单与冻结准备引用不一致")
        config["train"]["manifest"] = old["manifest"]
    view = dataset_component.open_physical(config)
    apply_declared_split(view, config, None if old is None else old.get("partitions"))
    return PhysicalPreparation(config, view, model_component, old, extensions={})


def bind_fields(data, *, settings=None):
    """绑定领域输入和目标；缺失分片不能退回另一份数据。"""
    if settings is not None:
        data.config["trainprep"] = plain(settings)
        data.config["trainprep"].pop("normalization", None)
        data.config["trainprep"].pop("sampling", None)
    if not data.view.partitions.get("train"):
        raise ValueError("物理准备需要非空训练分片")
    data.bound = True
    return data


def freeze_normalization(data, *, settings=None):
    """从旧记录恢复或拟合训练变换；不推进模型随机状态。"""
    if not data.bound:
        raise ValueError("冻结归一化前必须绑定字段")
    if settings is not None:
        data.config["normalization"] = plain(settings)
    data.normalization = (
        Normalization(data.old["normalization"]) if data.old else freeze(data.view, data.config)
    )
    return data


def configure_sampling(data, *, settings=None, operation=None, model_component=None):
    """配置 sample/config/normalization → batch 能力，训练时逐轮调用。"""
    if settings is not None:
        data.config["sampling"] = plain(settings)
    selection = data.config["sampling"]
    data.prepare = resolve_operation(
        selection, default=data.model_component.prepare_sample, operation=operation
    )
    frozen_sampling = (data.old or {}).get("extensions", {}).get("sampling")
    if operation is None and not selection.get("target") and frozen_sampling:
        data.prepare = restore_operation(frozen_sampling)
    if operation is not None or selection.get("target") or frozen_sampling:
        data.extensions["sampling"] = operation_record(data.prepare)
    return data


def configure_batching(data, *, batch_size=None, model_component=None):
    """记录现有物理模型单实例批次约定，不额外拼接样本。"""
    # 旧独立物理准备不要求训练控制块，单实例是该公开接口的既有默认。
    size = data.config.get("train", {}).get("batch_size", 1) if batch_size is None else batch_size
    if size != 1:
        raise ValueError("当前共享物理路径要求 batch_size=1")
    data.batching = True
    return data


def validate_preparation(data):
    """核对数据与冻结声明，并在隔离随机状态下验证真实模型输入。"""
    if not data.bound or data.normalization is None or data.prepare is None or not data.batching:
        raise ValueError("准备需要字段、归一化、采样和拼批全部配置")
    config, old = data.config, data.old
    data_id = data.view.content_digest()
    declarations = deepcopy(
        {k: config[k] for k in ("model", "trainprep", "sampling", "normalization")}
    )
    declarations["component"] = data.model_component.SOURCE
    if old and (old.get("version") == 2 or "dataset" not in old):
        raise ValueError("现行准备记录需用 trainprep.preparation 消费，不能走旧物理准备接口")
    if old and (old["dataset"] != data_id or old["declarations"] != declarations):
        raise ValueError("数据、模型输入或准备声明已变化")
    record = {
        "version": 1,
        "dataset": data_id,
        "manifest": data.view.describe()["reference"],
        "declarations": declarations,
        "normalization": data.normalization.record,
        "split_counts": {k: len(v) for k, v in data.view.partitions.items()},
    }
    if (config.get("trainprep") or {}).get("split") or (old or {}).get("partitions"):
        record["partitions"] = {k: list(v) for k, v in data.view.partitions.items()}
        record["split"] = deepcopy(
            (config.get("trainprep") or {}).get("split") or (old or {}).get("split")
        )
    if data.extensions:
        record["extensions"] = deepcopy(data.extensions)
    record["digest"] = fingerprint(record)
    if old and old != record:
        raise ValueError("冻结准备内容或扩展实现不一致，请重新准备")
    with preserve_randomness():
        sample = data.view.read("train", 0)
        validate_bindings(sample, config["trainprep"])
        data.prepare(sample, config, data.normalization, evaluation=True)
    data.record = record
    return data


def check_report(data, *, session):
    """交付检查报告，不发布准备产物。"""
    result = {"mode": "trainprep_check", "split_counts": data.record["split_counts"]}
    session.report(result, stage="trainprep")
    return result


def publish(data, *, session):
    """通过唯一 writer 发布已校验的物理准备。"""
    if not data.record:
        raise ValueError("发布前必须验证准备")
    if session.dry_run:
        return check_report(data, session=session)
    path = session.artifact("preparation.json", data.record)
    result = {"preparation": str(path), "split_counts": data.record["split_counts"]}
    session.report(result, stage="trainprep")
    return result


def consume(config, dataset_component, model_component, reference=None):
    """重建同一公开准备链，用于训练和独立后处理的契约校验。"""
    data = open_dataset(config, dataset_component, model_component, reference)
    data = bind_fields(data)
    data = freeze_normalization(data)
    data = configure_sampling(data)
    data = configure_batching(data)
    return validate_preparation(data)


def open_preparation(config, dataset_component, model_component, reference=None):
    """兼容旧三元组入口；与显式步骤共用实现。"""
    data = consume(config, dataset_component, model_component, reference)
    return data.view, data.normalization, data.record


def normalized_fields(sample: dict, normalization: Normalization) -> dict:
    """点字段保持物理来源，样本条件由模型绑定显式变换。"""
    return normalization.apply(sample["fields"])
