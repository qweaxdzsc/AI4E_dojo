"""案例公开检查门面；task 捕获配置后调用，不读取服务数据库或 recipe。"""

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


def parameter_capabilities(config, model):
    """由实际工作流和模型提供者导出可编辑范围，不让前端重写算法限制。"""
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
    descriptors = {}
    for key, value in config.get("train", {}).items():
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
        descriptors[key] = item
    return {
        "training_constraints": constraints,
        "parameter_descriptors": descriptors,
        "losses": getattr(model, "PLATFORM_LOSSES", {"configurable": False}),
    }


def execute(request: dict) -> dict:
    """执行 describe_case/inspect_dataset/validate_configuration/trace_model/compare_fields。"""
    operation = request["operation"]
    if operation == "compare_fields":
        from ai4e_core.abilities.postproc.difference import compare_files

        return compare_files(
            request["inputs"], Path(request["output_dir"]), request.get("options", {})
        )
    from omegaconf import OmegaConf

    from ai4e_core.applications.aero_cfd.configuration import resolve_paths

    source = OmegaConf.to_container(OmegaConf.create(request.get("config", {})), resolve=True)
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
    if selection.get("samples"):
        config.setdefault("dataset", {})["samples"] = selection["samples"]
    if request.get("component_provider") and not all(
        config.get("components", {}).get(key) for key in ("model", "dataset", "workflow")
    ):
        provider = import_module(request["component_provider"])
        selected = provider.load(config)
        config["components"] = {
            name: getattr(selected, name).__name__ for name in ("dataset", "model", "workflow")
        }
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
            "train": [("train", "preparation")],
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
        reference = resolved.get("train", {}).get("preparation")
        if reference or resolved.get("train", {}).get("manifest"):
            from .trainprep.physical import open_preparation

            _, _, record = open_preparation(resolved, dataset, model, reference)
            result["readiness"] = {"preparation_compatible": True, "digest": record["digest"]}
        return result
    if operation == "trace_model":
        from ai4e_core.abilities.modeling.inspection import trace

        from .trainprep.physical import open_preparation

        train = config.get("train") or {}
        if not train.get("preparation") and not train.get("manifest"):
            raise ValueError("train.manifest: 模型跟踪需要已有物理数据清单或准备记录")
        view, normalization, record = open_preparation(
            config, dataset, model, train.get("preparation")
        )
        sample = view.read("train", 0)
        batch = model.prepare_sample(sample, config, normalization, evaluation=True)
        network = model.construct(**model.training_parameters(config)).cpu().eval()
        return trace(
            network,
            batch["inputs"],
            Path(request["output_dir"]),
            revision=fingerprint(config),
            predict=model.predict,
            input_source={"identity": sample["identity"], "preparation": record["digest"]},
        )
    raise ValueError(f"未知检查操作: {operation}")


inspect = execute
