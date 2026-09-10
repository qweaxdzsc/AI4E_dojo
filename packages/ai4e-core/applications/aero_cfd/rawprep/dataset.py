"""Dataset 前处理装配：登记顺序步骤，提交数据清单与训练分片统计。"""

import json
from copy import deepcopy
from pathlib import Path
from uuid import uuid4

from omegaconf import OmegaConf

from ai4e_core.applications.base.dataset import Dataset
from ai4e_core.base.events import LOGGER, event, operation

from .derive import derive_geometry as derive_one
from .read import dataread
from .read import extract_fields as extract_one
from .save import tensorize, write_tensors
from .select import filter_points as filter_one
from .select import select_fields as select_one
from .select import validate_fields as validate_one
from .stats import resolve_statistics


def read(dataset: Dataset, *, sources) -> Dataset:
    """登记读取；sources 选择 manifest 中的来源，可用映射覆盖文件名。"""
    sources = (
        OmegaConf.to_container(sources, resolve=True) if OmegaConf.is_config(sources) else sources
    )
    sources = list(sources) if isinstance(sources, (list, tuple)) else dict(sources)
    config = {"dataset": {"root": str(dataset.root)}, "source": {"files": []}, "pre": {}}
    for role in sources:
        if role not in dataset.metadata["sources"]:
            raise ValueError(f"未知来源 {role}")
        spec = deepcopy(dataset.metadata["sources"][role])
        if isinstance(sources, dict):
            spec.update(sources[role])
        config["source"]["files"].append({"name": role, "filename": spec["filename"]})
        config["pre"][role] = {"source": role, "fields": {}}
        if spec.get("cell_type") is not None:
            config["pre"][role]["cell_type"] = spec["cell_type"]
    return dataset.then("读取", lambda ctx: dataread(ctx), config=config)


def extract_fields(data, *, fields=None):
    """选择字段与分量并登记提取；字典输入保留单样本公开能力。"""
    if not isinstance(data, Dataset):
        return extract_one(data)
    config = deepcopy(data.options["config"])
    for role, requested in fields.items():
        if role not in config["pre"]:
            raise ValueError(f"提取域未读取: {role}")
        for name, overrides in requested.items():
            available = data.metadata["fields"].get(role, {})
            if name not in available:
                raise ValueError(f"未知字段 {role}.{name}；可用字段={list(available)}")
            spec = {**available[name], **dict(overrides)}
            if isinstance(spec["components"], bool) or spec["components"] not in (1, 3):
                raise ValueError(f"字段 {role}.{name} 当前仅支持 1 或 3 分量")
            spec["kind"] = "scalar" if spec["components"] == 1 else "vector"
            config["pre"][role]["fields"][name] = spec
    return data.then("字段提取", extract_one, config=config)


def derive_geometry(data, *, features=None, enabled=None):
    """登记显式几何能力；不启用的能力不执行。"""
    if not isinstance(data, Dataset):
        return derive_one(data, enabled=enabled)
    features = (
        OmegaConf.to_container(features, resolve=True)
        if OmegaConf.is_config(features)
        else features
    )
    selected = list(features)
    parameters = features if isinstance(features, dict) else {}
    return data.then(
        "几何派生", lambda ctx: derive_one(ctx, enabled=selected, parameters=parameters)
    )


def select_fields(data, *, fields=None, output=None):
    """按 manifest 的输出契约选场，文件名由逻辑字段生成。"""
    if not isinstance(data, Dataset):
        return select_one(data, output=output)
    if len(fields) != len(set(fields)):
        raise ValueError("保存字段重复")
    unknown = set(fields) - set(data.metadata["outputs"])
    if unknown:
        raise ValueError(f"未知保存字段: {sorted(unknown)}")
    output = {
        "fields": {name: data.metadata["outputs"][name] for name in fields},
        "filemap": {name: name + ".pt" for name in fields},
        "optional": [],
    }
    return data.then("字段选择", lambda ctx: select_one(ctx, output=output), output=output)


def validate_fields(data):
    """登记原始/筛选后的实体身份校验。"""
    return data.then("字段校验", validate_one) if isinstance(data, Dataset) else validate_one(data)


def filter_points(data, *, filters):
    """登记同步筛选；记录各组实际保留与删除数量。"""
    filters = (
        OmegaConf.to_container(filters, resolve=True) if OmegaConf.is_config(filters) else filters
    )

    def apply(ctx):
        before = {k: g["count"] for k, g in ctx["groups"].items()}
        result = filter_one(ctx, filters=dict(filters))
        for key, group in result["groups"].items():
            event(
                "筛选",
                "结果",
                组=key,
                筛选前=before[key],
                保留=group["count"],
                删除=before[key] - group["count"],
            )
        return result

    return data.then("筛选", apply) if isinstance(data, Dataset) else apply(data)


def to_tensors(data: Dataset, *, vtkhdf: bool = False) -> Dataset:
    """登记单样本张量编码，不在登记阶段读取数组。"""
    return data.then("张量编码", lambda ctx: {**tensorize(ctx), "vtkhdf": vtkhdf})


def save_sample(ctx: dict, *, output: dict) -> dict:
    """按所属分片保存；保留安全提交、实体身份和字段形状。"""
    ctx = dict(ctx)
    ctx["config"] = deepcopy(ctx["config"])
    ctx["config"]["pre"]["output"] = {"dir": output[ctx["partition"]], "root_subdir": "."}
    shapes = {
        name: {"shape": list(value.shape), "dtype": str(value.dtype), "state": "physical"}
        for name, value in ctx["payloads"].items()
    }
    result = write_tensors(ctx)["result"]
    result.update(partition=ctx["partition"], fields=shapes)
    for notice in result["warnings"]:
        LOGGER.warning("[样本提交/警告] 样本=%s；%s", ctx["sample"], notice)
    event(
        "样本提交",
        "结果",
        目标=result["path"],
        文件数=len(result["names"]),
        状态="已提交" if result["written"] else "预检通过，未写数据",
    )
    return result


def _atomic_json(path: Path, value: dict) -> None:
    """同级暂存后替换元数据；失败不破坏旧文件。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name("." + path.name + "." + uuid4().hex + ".tmp")
    try:
        temp.write_text(json.dumps(value, ensure_ascii=False, indent=2))
        temp.replace(path)
    finally:
        temp.unlink(missing_ok=True)


def publish_dataset(results: dict) -> dict:
    """准备本次清单；统计成功后才发布完整 manifest。"""
    dataset = results["dataset"]
    result = {
        **results,
        "manifest": {
            "version": 1,
            "state": "physical",
            "source_manifest": dataset.metadata["manifest_path"],
            "partitions": {k: list(v) for k, v in dataset.partitions.items()},
            "field_definitions": dataset.metadata["outputs"],
            "samples": results["results"],
            "statistics": None,
        },
    }
    return result


def compute_statistics(dataset: dict, spec) -> None:
    """只统计本次完整训练分片；发布清单与统计引用，不执行归一化。"""
    if dataset["failed"]:
        raise ValueError("样本处理部分失败；不发布完整数据清单或训练统计")
    source = dataset["dataset"]
    spec = OmegaConf.to_container(spec, resolve=True) if OmegaConf.is_config(spec) else dict(spec)
    mode = spec.get("mode", "fit")
    if mode not in ("fit", "reference", "none"):
        raise ValueError(f"未知统计模式: {mode}")
    target = Path(dataset["output"].get("train", dataset["output"]["root"])) / "statistics.yaml"
    reference = None
    if mode == "reference":
        reference = source.metadata["reference_statistics"]
    if mode != "none":
        train = list(source.partitions.get("train", ()))
        if mode == "fit" and not train:
            raise ValueError(
                "统计拟合需要非空 train 分片；仅处理 test 请显式选择 reference 或 none"
            )
        stats = {
            **spec,
            "recalculate": mode == "fit",
            "train_samples": train,
            "shipped": reference,
            "output": str(target),
            "missing": "error",
        }
        ctx = {
            "items": list(source.samples),
            "config": {"pre": {"output": {"dir": dataset["output"]["root"]}}},
            "batch": dataset,
            "dry_run": dataset["dry_run"],
            "overwrite": dataset["overwrite"],
        }
        details = (
            {"分片": "train", "样本数": len(train), "方法": mode}
            if mode == "fit"
            else {"方法": mode, "参数来源": reference}
        )
        with operation("统计", **details):
            resolve_statistics(ctx, stats=stats)
        dataset["manifest"]["statistics"] = {
            "mode": mode,
            "path": reference or str(target),
            "state": "physical",
            "samples": train if mode == "fit" else None,
        }
    if not dataset["dry_run"]:
        with operation("数据清单", 状态="physical", 归一化="未执行"):
            _atomic_json(Path(dataset["output"]["root"]) / "manifest.json", dataset["manifest"])


def _preflight(data, output, *, flags, settings):
    """提交前检查所有实际样本目标和元数据；禁止源数据与输出覆盖。"""
    from ai4e_core.abilities.data.validate import plan_output

    roots = {k: Path(output[k]).resolve() for k in data.partitions}
    source = data.root.resolve()
    import os

    for target in [Path(output["root"]).resolve(), *roots.values()]:
        parent = target
        while not parent.exists():
            parent = parent.parent
        if not parent.is_dir() or not os.access(parent, os.W_OK | os.X_OK):
            raise PermissionError(f"输出目标不可写: {target}")
    for name, path in roots.items():
        if path.is_relative_to(source) or source.is_relative_to(path):
            raise ValueError(f"分片输出与原始数据重叠: {name}={path}")
    entries = list(roots.items())
    for i, (name, path) in enumerate(entries):
        for other, target in entries[i + 1 :]:
            if path.is_relative_to(target) or target.is_relative_to(path):
                raise ValueError(f"分片输出重叠: {name}/{other}")
    root = Path(output["root"]).resolve()
    if root.is_relative_to(source) or source.is_relative_to(root):
        raise ValueError("数据清单目录与原始数据重叠")
    meta = [root / "manifest.json"]
    if settings.get("statistics", {}).get("mode", "fit") == "fit":
        if "train" not in roots:
            raise ValueError("统计拟合需要 train 分片")
        meta.append(roots["train"] / "statistics.yaml")
    for path in meta:
        if path.exists() and not flags["overwrite"]:
            raise FileExistsError(f"产物已存在: {path}")
    for partition, samples in data.partitions.items():
        for sample in samples:
            target = (roots[partition] / sample).resolve()
            if not target.is_relative_to(roots[partition]):
                raise ValueError(f"样本输出逃离分片根: {target}")
            if any(m == target or m.is_relative_to(target) for m in meta):
                raise ValueError(f"样本目录与元数据路径冲突: {target}")
            plan_output(
                target,
                list(data.options["output"]["filemap"]),
                data.options["output"]["filemap"],
                overwrite=flags["overwrite"],
            )
    event("输出预检", "目标", **{k: str(v) for k, v in roots.items()})


save_sample.preflight = _preflight


def _begin(data, output, *, flags):
    """覆盖开始即撤下旧的完整清单；部分提交后不能继续把旧清单标为有效。"""
    if flags["dry_run"]:
        return
    manifest = Path(output["root"]) / "manifest.json"
    if manifest.exists():
        backup = manifest.with_name(f".manifest.{uuid4().hex}.previous.json")
        manifest.replace(backup)
        event("数据清单", "旧版本撤下", 备份=str(backup))


save_sample.begin = _begin
