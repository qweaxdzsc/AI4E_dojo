"""案例公开检查门面；task 捕获配置后调用，不读取服务数据库或 recipe。"""

import json
from copy import deepcopy
from importlib import import_module
from pathlib import Path

from ai4e_core.abilities.data.validate.fingerprint import fingerprint
from ai4e_core.abilities.postproc.coordinate_space import coordinate_space


def normalize_config(config: dict) -> dict:
    """五段用户输入转换为既有业务树，旧采样单键兼容，双键拒绝。"""
    cfg = deepcopy(config)
    coordinate_space(cfg.get("dataset", {}).get("coordinate_space"))
    if "rawprep" in cfg:
        cfg.update(cfg.pop("rawprep"))
    prep = cfg.setdefault("trainprep", {})
    model = cfg.setdefault("model", {})
    sources = [mapping for mapping in (cfg, prep, model) if "sampling" in mapping]
    if len(sources) > 1:
        raise ValueError("model.sampling: 新旧采样声明不能同时存在")
    if sources:
        sampling = sources[0].pop("sampling")
        cfg["sampling"] = sampling
    if "normalization" in prep:
        if "normalization" in cfg:
            raise ValueError("trainprep.normalization: 重复归一化声明")
        cfg["normalization"] = prep.pop("normalization")
    return cfg


def public_configuration(config: dict) -> dict:
    """返回可保存的五段输入；不把内部展开树反馈为用户 YAML。"""
    cfg = deepcopy(config)
    raw_keys = (
        "sources",
        "fields",
        "geometry",
        "save_fields",
        "filters",
        "statistics",
        "vtkhdf",
        "extraction",
        "format",
    )
    cfg["rawprep"] = {name: cfg.pop(name) for name in raw_keys if name in cfg}
    if "sampling" in cfg:
        cfg.setdefault("model", {})["sampling"] = cfg.pop("sampling")
    if "normalization" in cfg:
        cfg.setdefault("trainprep", {})["normalization"] = cfg.pop("normalization")
    return cfg


def _components(cfg):
    """只加载捕获配置已声明的组件，算法包不硬编码贡献实现。"""
    names = cfg.get("components", {})
    if not names.get("model") or not names.get("dataset"):
        raise ValueError("components: 平台检查需要显式 model 和 dataset 组件声明")
    return import_module(names["dataset"]), import_module(names["model"])


def _preparation_path(reference):
    """准备引用可以是路径或含 preparation 的记录。"""
    if isinstance(reference, dict):
        return reference.get("preparation")
    return reference


def _preparation_version(reference) -> int:
    """识别现行 version=2 与旧物理 version=1 准备，未知记录拒绝。"""
    path = _preparation_path(reference)
    if not path:
        raise ValueError("train.preparation: 缺少准备记录路径")
    try:
        record = json.loads(Path(path).read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"train.preparation: 无法读取准备记录: {exc}") from exc
    if record.get("version") == 2:
        return 2
    if record.get("version") == 1 or "dataset" in record:
        return 1
    raise ValueError("train.preparation: 不支持的准备记录版本")


def _require_current_preparation(reference) -> None:
    """公开检查只认现行 version=2，旧物理准备必须重新生成。"""
    if _preparation_version(reference) != 2:
        raise ValueError(
            "preparation_requires_regeneration: 数据准备已改用现行配置方式，这份旧准备不能再训，请按现行数据准备重新生成。"
        )


def _consume_current_preparation(config, model, reference, dataset=None):
    """按训练同一条现行准备链恢复，不走旧物理 version=1 接口。"""
    from .trainprep import preparation as prep

    _require_current_preparation(reference)
    record = json.loads(Path(_preparation_path(reference)).read_text())
    if record.get("kind") == "physical_fields":
        from .trainprep.physical import consume

        if dataset is None:
            raise ValueError("物理场准备需要所选数据组件")
        return consume(config, dataset, model, reference)
    return prep.consume(
        config,
        reference,
        prepare=getattr(model, "prepare_inputs", None) or model.prepare_sample,
        collate=getattr(model, "collate", None) or (lambda items: items[0]),
    )


def _trace_batch(config, dataset, model, reference):
    """准备只提供可读清单与场；前向批次按当前模型页采样组织。"""
    from .trainprep.dataset import prepare_partition_sample

    _require_current_preparation(reference)
    data = _consume_current_preparation(config, model, reference, dataset)
    if data.record.get("kind") == "physical_fields":
        probe = next(
            (name for name in ("train", "test", "eval") if data.view.partitions.get(name)),
            None,
        )
        if probe is None:
            raise ValueError("准备切片全部为空")
        sample = data.view.read(probe, 0)
        batch = data.prepare(sample, data.config, data.normalization, evaluation=True)
        return batch, {"identity": sample["identity"], "preparation": data.record["digest"]}
    split = str((config.get("train") or {}).get("training_split") or "train")
    if split == "validation":
        split = "eval"
    for name in (split, "train", "test", "eval"):
        if data.index.partitions.get(name):
            split = name
            break
    else:
        raise ValueError("准备切片全部为空")
    item = prepare_partition_sample(
        data.index,
        split,
        0,
        prepare=data.prepare,
        normalization=data.normalization,
        physical_prepare=data.physical_prepare,
        normalized_input=data.index.manifest["state"] == "normalized",
        sampling=config["sampling"],
        config=config,
        evaluation=True,
    )
    batch = data.collate([item])
    return batch, {
        "identity": {"sample": data.index.partitions[split][0], "index": 0},
        "preparation": data.record["digest"],
    }


def parameter_capabilities(config, model):
    """由实际工作流和模型提供者导出可编辑范围，含损失与采样能力，不让前端重写算法限制。"""
    constraints = deepcopy(getattr(model, "TRAINING_CONSTRAINTS", {}))
    if config.get("components", {}).get("workflow") == "ai4e_core.applications.aero_cfd.workflow":
        for key, value in {
            "batch_size": 1,
            "num_workers": 0,
            "precision": "fp32",
            "evaluation_enabled": False,
        }.items():
            constraints[key] = {
                "allowed": [value],
                "readOnly": True,
                "reason": "当前共享物理工作流固定值",
            }
    constraints.setdefault("optimizer", {"allowed": ["adam", "adamw", "lion"]})
    if "scheduler" in config.get("train", {}):
        constraints.setdefault(
            "scheduler", {"allowed": ["constant", "none", "warmup_cosine", "cosine"]}
        )
    from ai4e_core.abilities.eval.metrics import METRIC_NAMES

    descriptors = {}
    train = dict(config.get("train") or {})
    train.setdefault("export_predictions", False)
    train.setdefault("export_vtk", False)
    train.setdefault("export_split", "test")
    for key, value in train.items():
        item = {
            "type": "boolean"
            if isinstance(value, bool)
            else "number"
            if isinstance(value, (int, float))
            else "array"
            if isinstance(value, list)
            else "string"
            if isinstance(value, str)
            else "nullable",
            "readOnly": key in {"manifest", "preparation", "resume"},
        }
        item.update(constraints.get(key, {}))
        if key == "loss_x_axis":
            item.setdefault("allowed", ["epoch", "updates"])
        if key == "validation_unit":
            item.setdefault("allowed", ["epoch", "updates"])
        if key == "export_split":
            item.setdefault("allowed", ["train", "test", "eval", "validation"])
        descriptors[key] = item
    losses = deepcopy(getattr(model, "PLATFORM_LOSSES", {"configurable": False}))
    evaluation_fields = []
    for domain, binding in ((config.get("trainprep") or {}).get("domains") or {}).items():
        for name, field in (binding.get("targets") or {}).items():
            value = str(field)
            evaluation_fields.append({"value": value, "label": f"{domain}/{name}"})
    if not losses.get("configurable") and not (config.get("model") or {}).get("supervision"):
        terms = []
        for domain, binding in ((config.get("trainprep") or {}).get("domains") or {}).items():
            for name, field in (binding.get("targets") or {}).items():
                terms.append(
                    {
                        "name": f"{domain}/{name}",
                        "target": field,
                        "loss": losses.get("fixed", "mse"),
                        "weight": 1.0,
                    }
                )
        if terms:
            losses["terms"] = terms
    return {
        "evaluation_metrics": {
            "options": [
                {
                    "value": name,
                    "label": {"mse": "MSE", "mae": "MAE", "relative_l2": "相对 L2"}[name],
                }
                for name in METRIC_NAMES
            ],
            "default": list(METRIC_NAMES),
        },
        "evaluation_fields": {
            "options": evaluation_fields,
            "default": [item["value"] for item in evaluation_fields],
        },
        "training_constraints": constraints,
        "parameter_descriptors": descriptors,
        "losses": losses,
        "sampling": getattr(model, "PLATFORM_SAMPLING", {"configurable": False}),
    }


def execute(request: dict) -> dict:
    """执行 describe_case/inspect_dataset/validate_configuration/trace_model/compare_fields。trace_model 只取样组网。"""
    operation = request["operation"]
    if operation == "compare_fields":
        from ai4e_core.abilities.postproc.difference import compare_files

        return compare_files(
            request["inputs"], Path(request["output_dir"]), request.get("options", {})
        )
    from omegaconf import OmegaConf

    from ai4e_core.applications.aero_cfd.configuration import resolve_paths

    source = OmegaConf.to_container(OmegaConf.create(request.get("config", {})), resolve=True)
    from .rawprep.descriptor import dataset_component, resolve_rawprep, validate_rawprep

    manifest = source.get("dataset", {}).get("manifest")
    if manifest and request.get("config_dir") and not Path(manifest).is_absolute():
        source["dataset"]["manifest"] = str((Path(request["config_dir"]) / manifest).resolve())
    component = dataset_component(source)
    if operation == "describe_rawprep":
        if not hasattr(component, "describe_rawprep"):
            return {"profile": None, "rawprep": source.get("rawprep", {})}
        profile = component.describe_rawprep(source)
        initial = request.get("selection", {}).get("case_rawprep")
        if initial is not None:
            from .rawprep.descriptor import merge_defaults

            profile["defaults"] = merge_defaults(profile["defaults"], initial)
        resolved = resolve_rawprep(source)["rawprep"]
        if request.get("selection", {}).get("preserve_expressions"):
            from .rawprep.descriptor import merge_defaults, reconcile_format_keys

            declared = request["config"].get("rawprep") or {}
            resolved = reconcile_format_keys(
                profile["defaults"], declared, merge_defaults(profile["defaults"], declared)
            )
        name = (source.get("dataset") or {}).get("processed_name")
        return {"profile": profile, "rawprep": resolved, "processed_name": name or ""}
    if operation == "validate_rawprep":
        candidate = request.get("selection", {}).get("rawprep", source.get("rawprep", {}))
        validate_rawprep(candidate, component.describe_rawprep(source))
        return {"valid": True}
    source = resolve_rawprep(source)
    config = normalize_config(source)
    if request.get("config_dir"):
        config = resolve_paths(config, Path(request["config_dir"]) / "config.yaml")
        for name in ("train_h5", "test_h5", "connectivity_h5"):
            value = config.get("dataset", {}).get(name)
            if value and not Path(value).is_absolute():
                config["dataset"][name] = str((Path(request["config_dir"]) / value).resolve())
    selection = request.get("selection", {})
    if selection.get("root"):
        config.setdefault("dataset", {})["root"] = selection["root"]
    if "samples" in selection:
        config.setdefault("dataset", {})["samples"] = selection["samples"]
    if request.get("component_provider") and not all(
        config.get("components", {}).get(key) for key in ("model", "dataset", "workflow")
    ):
        provider = import_module(request["component_provider"])
        selected = provider.load(config)
        config["components"] = {
            name: getattr(selected, name).__name__ for name in ("dataset", "model", "workflow")
        }
    if operation == "inspect_dataset":
        config["inspection_scope"] = selection.get("inspection_scope", "representatives")
        config["sample_scope"] = selection.get("sample_scope")
        return component.inspect_dataset(config)
    dataset, model = _components(config)
    config = model.resolve(config, validate=False)
    if operation == "describe_case":
        return {
            "schema_version": 1,
            "model": model.SOURCE,
            "dataset": dataset.__name__,
            "configuration": public_configuration(config),
            "resolved_configuration": config,
            "stages": ["rawprep", "trainprep", "train", "post"],
            "capabilities": {
                "formats": ["pt", "zarr"],
                "model_trace": True,
                "difference": "strict_identity",
                "parallel_threads": False,
                **parameter_capabilities(config, model),
            },
        }
    if operation == "inspect_dataset":
        return dataset.inspect_dataset(config)
    if operation == "validate_configuration":
        resolved = model.resolve(config, validate=True)
        result = {"valid": True, "revision": fingerprint(config), "readiness": {}}
        stage = selection.get("stage")
        requirements = {
            "trainprep": [("train", "manifest")],
            "post": [("train", "preparation"), ("post", "checkpoint")],
        }
        for section, key in requirements.get(stage, []):
            reference_path = resolved.get(section, {}).get(key)
            if not isinstance(reference_path, str) or not Path(reference_path).is_file():
                raise ValueError(f"{section}.{key}: 阶段 {stage} 需要已有固定产物")
        if stage == "rawprep":
            descriptor = dataset.inspect_dataset(resolved)
            result["readiness"] = {
                "dataset_revision": descriptor["revision"],
                "sample_count": len(descriptor["samples"]),
            }
            return result
        if stage == "trainprep":
            # 准备只验绑定清单等本步输入，不用当前模型页采样去比对旧准备。
            return result
        reference = (resolved.get("inputs") or {}).get("train", {}).get("preparation") or (
            resolved.get("train") or {}
        ).get("preparation")
        if reference:
            data = _consume_current_preparation(resolved, model, reference, dataset)
            result["readiness"] = {
                "preparation_compatible": True,
                "digest": data.record["digest"],
            }
        return result
    if operation == "trace_model":
        train = config.get("train") or {}
        reference = (config.get("inputs") or {}).get("train", {}).get("preparation") or train.get(
            "preparation"
        )
        manifest = (config.get("inputs") or {}).get("trainprep", {}).get("dataset") or train.get(
            "manifest"
        )
        if not reference and not manifest:
            raise ValueError("train.manifest: 模型跟踪需要已有物理数据清单或准备记录")
        if not reference:
            raise ValueError(
                "preparation_requires_regeneration: 结构跟踪需要现行数据准备记录，请按现行数据准备重新生成。"
            )
        batch, source = _trace_batch(config, dataset, model, reference)
        network = model.construct(**model.training_parameters(config)).cpu().eval()
        return {
            "network": network,
            "inputs": batch["inputs"],
            "revision": fingerprint(config),
            "input_source": source,
            "predict": model.predict,
        }
    raise ValueError(f"未知检查操作: {operation}")


inspect = execute
