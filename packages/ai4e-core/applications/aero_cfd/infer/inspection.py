"""推理候选的只读检查；供 task 的隔离检查进程调用，不返回权重。"""

import json
import pickle
from pathlib import Path

import torch

from ai4e_core.abilities.data.source.manifest import ManifestIndex
from ai4e_core.abilities.data.validate.fingerprint import fingerprint
from ai4e_core.abilities.inference.randomness import preserve_randomness

from .configuration import public_to_business


def _inspect_inputs(path, *, preparation=None, config=None) -> dict:
    """返回 JSON 元信息及兼容性；来源缺失和语义冲突显式标记 invalid。

    config 接受已展开的用户配置或业务配置，不导入 recipe。无 config 时以
    effective_config 为依据；本检查不执行模型，实际运行继续校验模型描述和数据内容。
    """
    result = {
        "path": str(Path(path).resolve()),
        "epoch": None,
        "updates": None,
        "contract": {},
        "preparation": None,
        "compatibility": {"status": "invalid", "reason": "尚未检查"},
    }
    try:
        with preserve_randomness():
            state = torch.load(path, map_location="cpu", weights_only=False)
        if (
            not isinstance(state, dict)
            or state.get("version") != 2
            or not isinstance(state.get("model"), dict)
        ):
            raise ValueError("需要完整 version=2 模型检查点")
        contract = state["contract"]
        # JSON 门禁防止模型权重或其他张量误入管理进程。
        result.update(
            epoch=state.get("epoch"),
            updates=state.get("updates"),
            contract=json.loads(json.dumps(contract)),
        )
        effective = state.get("effective_config")
        cfg = public_to_business(config if config is not None else effective or {})
        frozen = public_to_business(effective) if effective else None
        reference = (
            preparation
            or (cfg.get("infer") or {}).get("preparation")
            or cfg.get("train", {}).get("preparation")
        )
        reference = (
            Path(reference)
            if reference
            else Path(path).parent.parent / "artifacts/preparation.json"
        )
        record = json.loads(reference.read_text())
        digest = record.get("digest")
        payload = {k: v for k, v in record.items() if k != "digest"}
        if record.get("version") == 1:
            actual = fingerprint(payload)
        else:
            from ai4e_core.applications.aero_cfd.trainprep.preparation import (
                digest as legacy_digest,
            )

            actual = legacy_digest(payload)
        if not digest or actual != digest:
            raise ValueError("准备记录摘要不匹配")
        manifest = Path(record["manifest"])
        index = ManifestIndex(manifest)
        result["preparation"] = {
            "path": str(reference.resolve()),
            "digest": digest,
            "manifest": str(manifest),
            "partitions": index.partitions,
        }
        if contract.get("preparation") and contract["preparation"] != digest:
            raise ValueError("检查点与准备摘要不一致")
        if record.get("version") == 1 and cfg:
            declarations = {
                key: cfg[key] for key in ("model", "trainprep", "sampling", "normalization")
            }
            declarations["component"] = record["declarations"]["component"]
            if declarations != record["declarations"]:
                raise ValueError("当前模型或准备声明与检查点不兼容")
        if frozen and config is not None:
            for key in ("model", "trainprep", "sampling", "normalization"):
                if cfg.get(key) != frozen.get(key):
                    raise ValueError(f"当前 {key} 与检查点 effective_config 不兼容")
            if cfg.get("components", {}).get("model") != frozen.get("components", {}).get("model"):
                raise ValueError("当前模型组件与检查点 effective_config 不兼容")
        result["compatibility"] = {"status": "compatible", "reason": None}
    except (
        OSError,
        ValueError,
        TypeError,
        KeyError,
        RuntimeError,
        EOFError,
        pickle.UnpicklingError,
    ) as exc:
        result["compatibility"] = {"status": "invalid", "reason": str(exc)}
    return result


def inspect_checkpoint(path, *, preparation=None, config=None) -> dict:
    """读取轻量权重元信息；提供 preparation/config 时同时进行来源检查。"""
    if preparation is not None or config is not None:
        return _inspect_inputs(path, preparation=preparation, config=config)
    with preserve_randomness():
        state = torch.load(path, map_location="cpu", weights_only=False)
    if (
        not isinstance(state, dict)
        or state.get("version") != 2
        or not isinstance(state.get("model"), dict)
    ):
        raise ValueError("需要完整 version=2 模型检查点")
    return json.loads(
        json.dumps(
            {
                "epoch": state.get("epoch"),
                "updates": state.get("updates"),
                "contract": state.get("contract", {}),
                "effective_config": state.get("effective_config"),
                "evaluation": _checkpoint_evaluation(state),
            }
        )
    )


def inspect_inputs(checkpoint, preparation, config, config_dir) -> dict:
    """检查当前任务配置与固定输入；只通过配置指定的公开组件加载能力。"""
    from importlib import import_module

    from ai4e_core.applications.aero_cfd.configuration import resolve_paths

    try:
        from omegaconf import OmegaConf

        cfg = public_to_business(OmegaConf.to_container(OmegaConf.create(config), resolve=True))
        selected = cfg.get("components", {})
        component = import_module(selected["model"]) if selected.get("model") else None
        if component is None:
            # 原公开锚点配置没有组件选择；使用同一 core 默认展开，无 contrib 依赖。
            from ai4e_core.applications.aero_cfd.train.resolve import apply_resolved

            cfg = apply_resolved(cfg, validate=False)
        else:
            cfg = component.resolve(cfg, validate=False)
        cfg = resolve_paths(cfg, Path(config_dir) / "config.yaml")
        value = _inspect_inputs(checkpoint, preparation=preparation, config=cfg)
        value["partitions"] = (value.get("preparation") or {}).get("partitions", {})
        if value["compatibility"]["status"] == "compatible":
            dataset = import_module(selected["dataset"]) if selected.get("dataset") else None
            record = json.loads(Path(value["preparation"]["path"]).read_text())
            cfg["train"]["manifest"] = record["manifest"]
            if record["version"] == 1 and (dataset is None or component is None):
                raise ValueError("物理准备需要明确的数据和模型组件")
            if record["version"] == 1:
                from ai4e_core.applications.aero_cfd.trainprep.physical import consume

                consume(cfg, dataset, component, value["preparation"]["path"])
            elif component is not None:
                from ai4e_core.applications.aero_cfd.trainprep.preparation import consume

                consume(
                    cfg,
                    value["preparation"]["path"],
                    prepare=component.prepare_inputs,
                    collate=component.collate,
                )
            else:
                from ai4e_core.applications.aero_cfd.trainprep.preparation import (
                    dataset_digest,
                    declarations,
                )

                if (
                    declarations(cfg) != record["declarations"]
                    or dataset_digest(ManifestIndex(record["manifest"])) != record["dataset_digest"]
                ):
                    raise ValueError("旧锚点配置或数据与准备记录不一致")
        if value["compatibility"]["status"] == "compatible":
            from .catalog import describe_catalog

            value.update(describe_catalog(cfg, dataset_component=dataset))
        return value
    except (OSError, ValueError, KeyError, TypeError, RuntimeError) as exc:
        return {
            "preparation": None,
            "partitions": {},
            "compatibility": {"status": "invalid", "reason": str(exc)},
        }


def available_devices() -> list[str]:
    """仅列实际可用设备，任务层另行决定占用和排队。"""
    devices = ["cpu"]
    if torch.backends.mps.is_available():
        devices.append("mps")
    if torch.cuda.is_available():
        devices.extend(f"cuda:{index}" for index in range(torch.cuda.device_count()))
    return devices


def _checkpoint_evaluation(state):
    """仅采用与本权重轮次和更新数吻合的评价，不借用历史best。"""
    for row in reversed(state.get("history", [])):
        if row.get("epoch") != state.get("epoch") or row.get("updates") != state.get("updates"):
            continue
        evaluation = row.get("evaluation") or {}
        loss = evaluation.get("loss")
        import math

        if isinstance(loss, (int, float)) and math.isfinite(loss):
            cfg = state.get("effective_config", {})
            split = cfg.get("train", {}).get("evaluation_split", "validation")
            return {
                "value": loss,
                "metric": "loss",
                "direction": "min",
                "split": split,
                "protocol": fingerprint({"contract": state.get("contract"), "split": split}),
            }
    return None
