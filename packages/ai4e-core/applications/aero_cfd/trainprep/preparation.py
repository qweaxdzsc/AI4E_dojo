"""训练准备的公开步骤：冻结变换与数据身份，模型页采样预算不进入准备记录。"""

import hashlib
import inspect
import json
from copy import deepcopy
from dataclasses import dataclass, field
from functools import partial
from pathlib import Path

from ai4e_core.abilities.data.save.normalization import materialize, save_record
from ai4e_core.abilities.data.source.manifest import ManifestIndex
from ai4e_core.abilities.data.source.split import (
    SPLIT_BUCKETS,
    apply_declared_split,
    complete_split_buckets,
)
from ai4e_core.base.config import operation_record, plain, resolve_operation

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
    if overlay is not None:
        if not any(index.partitions.get(name) for name in SPLIT_BUCKETS):
            raise ValueError("准备切片全部为空")
    elif not index.partitions.get("train"):
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
    partitions = complete_split_buckets(data.index.partitions)
    split = deepcopy((data.config.get("trainprep") or {}).get("split")) or {
        "method": "original",
        "seed": 0,
        "counts": {name: len(partitions[name]) for name in SPLIT_BUCKETS},
    }
    if isinstance(split, dict):
        counts = split.setdefault("counts", {})
        if not isinstance(counts, dict):
            split["counts"] = {name: len(partitions[name]) for name in SPLIT_BUCKETS}
        else:
            for name in SPLIT_BUCKETS:
                counts.setdefault(name, len(partitions[name]))
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
        "split_counts": {name: len(samples) for name, samples in partitions.items()},
        "partitions": partitions,
        "split": split,
    }
    return data


def declarations(config: dict) -> dict:
    """只写准备真正消费的冻结项，不含模型页采样预算。"""
    trainprep = _mapping(config.get("trainprep"))
    return {
        "sampling": _sampling_record(config.get("sampling")),
        "trainprep": {
            "domains": deepcopy(trainprep.get("domains") or {}),
            "physical_rules": deepcopy(trainprep.get("physical_rules") or {}),
            "geometry_field": trainprep.get("geometry_field"),
            "use_physics_features": bool(trainprep.get("use_physics_features")),
            "conditioning": _conditioning_declaration(trainprep.get("conditioning")),
            "geometry_conditioning": _conditioning_declaration(
                trainprep.get("geometry_conditioning")
            ),
        },
        "data_specs": deepcopy((config.get("model") or {}).get("data_specs")),
        "geometry_conditioning_dims": (config.get("model") or {})
        .get("parameters", {})
        .get("geometry_conditioning_dims"),
    }


def _mapping(value) -> dict:
    return value if isinstance(value, dict) else {}


def _conditioning_declaration(value) -> dict:
    """条件只比名称与非路径字段，路径内容由 external_inputs 另行核对。"""
    result = {}
    for name, declaration in _mapping(value).items():
        if isinstance(declaration, dict):
            result[name] = {key: item for key, item in declaration.items() if key != "path"}
        else:
            result[name] = declaration
    return result


def _sampling_record(sampling) -> dict:
    """新准备只登记采样方法；超节点、点数和种子属于模型页，不写入。"""
    sampling = _mapping(sampling)
    result = {}
    if sampling.get("target"):
        result["target"] = sampling["target"]
    geometry = sampling.get("geometry")
    if isinstance(geometry, dict) and geometry.get("method"):
        result["geometry"] = {"method": geometry["method"]}
    domains = {}
    for name, domain in _mapping(sampling.get("domains")).items():
        if not isinstance(domain, dict):
            continue
        methods = {
            role: {"method": spec["method"]}
            for role, spec in domain.items()
            if isinstance(spec, dict) and spec.get("method")
        }
        if methods:
            domains[name] = methods
    if domains:
        result["domains"] = domains
    return result


def sampling_methods(sampling) -> dict:
    """比较用的采样方法视图；忽略超节点和模型页点数。"""
    return _sampling_declaration(sampling)


def _sampling_declaration(sampling: dict) -> dict:
    """只冻结几何/域采样方法与自定义入口，不冻结点数、种子或超节点。"""
    sampling = _mapping(sampling)
    result = {}
    if sampling.get("target"):
        result["target"] = sampling["target"]
    geometry = sampling.get("geometry")
    if isinstance(geometry, dict) and geometry.get("method"):
        result["geometry_method"] = geometry["method"]
    domains = {}
    for name, domain in _mapping(sampling.get("domains")).items():
        if not isinstance(domain, dict):
            continue
        methods = {
            role: spec["method"]
            for role, spec in domain.items()
            if isinstance(spec, dict) and spec.get("method")
        }
        if methods:
            domains[name] = methods
    if domains:
        result["domain_methods"] = domains
    return result


def frozen_contract(declared: dict) -> dict:
    """准备真正消费的冻结项：字段角色、数据规格和采样方法，不含模型页点数。"""
    declared = declared or {}
    trainprep = _mapping(declared.get("trainprep"))
    return {
        "data_specs": declared.get("data_specs"),
        "geometry_conditioning_dims": declared.get("geometry_conditioning_dims"),
        "trainprep": {
            "domains": trainprep.get("domains") or {},
            "physical_rules": trainprep.get("physical_rules") or {},
            "geometry_field": trainprep.get("geometry_field"),
            "use_physics_features": bool(trainprep.get("use_physics_features")),
            "conditioning": _conditioning_declaration(trainprep.get("conditioning")),
            "geometry_conditioning": _conditioning_declaration(
                trainprep.get("geometry_conditioning")
            ),
        },
        "sampling_declaration": _sampling_declaration(declared.get("sampling")),
    }


_CONTRACT_LABELS = {
    "data_specs": "数据规格",
    "geometry_conditioning_dims": "几何条件维度",
    "trainprep": "准备字段声明",
    "trainprep.domains": "字段角色",
    "trainprep.physical_rules": "物理场规则",
    "trainprep.geometry_field": "几何字段",
    "trainprep.use_physics_features": "物理特征开关",
    "trainprep.conditioning": "条件输入声明",
    "trainprep.geometry_conditioning": "几何条件声明",
    "sampling_declaration": "采样方法声明",
    "sampling_declaration.target": "自定义采样入口",
    "sampling_declaration.geometry_method": "几何采样方法",
    "sampling_declaration.domain_methods": "域采样方法",
}


def _contract_label(path: str, key: str) -> str:
    parts = path.split(".")
    for index in range(len(parts), 0, -1):
        candidate = ".".join(parts[:index])
        if candidate in _CONTRACT_LABELS:
            return _CONTRACT_LABELS[candidate]
    return _CONTRACT_LABELS.get(key) or path


def describe_contract_diffs(frozen: dict, current: dict, prefix: str = "") -> list[str]:
    """列出冻结语义差异，供检查页写明具体项而不是笼统重跑。"""
    diffs = []
    keys = list(dict.fromkeys([*frozen, *current]))
    for key in keys:
        path = f"{prefix}.{key}" if prefix else key
        left, right = frozen.get(key), current.get(key)
        if left == right:
            continue
        if isinstance(left, dict) and isinstance(right, dict):
            nested = describe_contract_diffs(left, right, path)
            if nested:
                diffs.extend(nested)
                continue
        diffs.append(_contract_label(path, key) + "不一致")
    return list(dict.fromkeys(diffs))


def contract_conflict_message(frozen: dict, current: dict) -> str:
    """消费冲突文案列出具体冻结项。"""
    diffs = describe_contract_diffs(frozen, current)
    if not diffs:
        return "配置与准备结果冲突，请重新运行 trainprep"
    return "配置与准备结果冲突：" + "；".join(diffs) + "。请重新运行 trainprep"


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
        run.record_asset("preparation", path, kind="preparation", stage="trainprep",
                         semantics={"type": "aero.preparation", "format_version": 2},
                         dependencies=[data.index.path.parent])
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
    """导入可读取的现行准备记录，按当前平台配置组计算，不拿冻结声明挡现行参数。"""
    prepare = resolve_operation(config["sampling"], default=prepare)
    path = reference["preparation"] if isinstance(reference, dict) else reference
    record = json.loads(Path(path).read_text())
    payload = {key: value for key, value in record.items() if key != "digest"}
    if record.get("version") != 2 or digest(payload) != record.get("digest"):
        raise ValueError("准备结果版本或摘要不一致")
    cfg = deepcopy(config)
    cfg["train"]["manifest"] = record["manifest"]
    data = prepare_fields(open_dataset(cfg, overlay=record.get("partitions")))
    data.normalization = Normalization(record["normalization"])
    if data.normalization.digest != record["normalization_digest"]:
        raise ValueError("准备归一化摘要不一致")
    data.prepare, data.collate, data.record = prepare, collate, record
    return data
