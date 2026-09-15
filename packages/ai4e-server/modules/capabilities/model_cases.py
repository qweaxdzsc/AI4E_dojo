"""官方起步预设与模型候选：只读 example，经 task 独立进程取得默认值和能力。"""

from uuid import uuid4

import ai4e_task as task
import yaml

MODELS = {
    "abupt": {
        "name": "AB-UPT",
        "component": "ai4e_contrib.ability.model.abupt.component",
    },
    "transolver3": {
        "name": "Transolver-3",
        "component": "ai4e_contrib.ability.model.transolver3.component",
    },
}

CASES = {
    "shapenet_car_abupt": {
        "name": "AB-UPT · ShapeNet-Car",
        "dataset_id": "shapenet_car",
        "model_id": "abupt",
        "variant": None,
        "binding_mode": "directory",
    },
    "shapenet_car_transolver3_surface": {
        "name": "Transolver-3 · ShapeNet-Car 表面",
        "dataset_id": "shapenet_car",
        "model_id": "transolver3",
        "variant": "surface",
        "binding_mode": "directory",
    },
    "shapenet_car_transolver3_volume": {
        "name": "Transolver-3 · ShapeNet-Car 体场",
        "dataset_id": "shapenet_car",
        "model_id": "transolver3",
        "variant": "volume",
        "binding_mode": "directory",
    },
    "nasa_crm_abupt": {
        "name": "AB-UPT · NASA CRM",
        "dataset_id": "nasa_crm",
        "model_id": "abupt",
        "variant": None,
        "binding_mode": "files",
    },
    "nasa_crm_transolver3": {
        "name": "Transolver-3 · NASA CRM",
        "dataset_id": "nasa_crm",
        "model_id": "transolver3",
        "variant": None,
        "binding_mode": "files",
    },
}

VARIANT_LABELS = {"surface": "表面", "volume": "体场"}
MODEL_COMPONENTS = {item["component"]: key for key, item in MODELS.items()}


def case_configuration(service, case_id: str) -> dict:
    """读取显式登记案例，不接受客户端提供组件或脚本路径。"""
    if case_id not in CASES:
        raise ValueError("unknown_registered_case")
    path = service.settings.template.parent.parent / "examples/aero_cfd" / case_id / "config.yaml"
    if not path.is_file():
        raise ValueError("registered_case_file_missing")
    return yaml.safe_load(path.read_text())


def dataset_id(config: dict) -> str:
    """优先按数据组件识别；旧五段外流任务沿用既有数据绑定兼容规则。"""
    component = (config.get("components") or {}).get("dataset")
    known = {
        "ai4e_contrib.application.datasets.shapenet_car": "shapenet_car",
        "ai4e_contrib.application.datasets.nasa_crm": "nasa_crm",
    }
    if component:
        if component not in known:
            raise ValueError("unsupported_dataset_binding")
        return known[component]
    if any(config.get("dataset", {}).get(key) for key in ("train_h5", "test_h5", "connectivity_h5")):
        return "nasa_crm"
    if {"rawprep", "trainprep", "model", "train", "post"} <= set(config):
        return "shapenet_car"
    raise ValueError("unsupported_dataset_binding")


def model_id(config: dict) -> str:
    """按模型组件识别官方模型；历史缺声明视为 AB-UPT。"""
    component = (config.get("components") or {}).get("model") or ""
    return MODEL_COMPONENTS.get(component, "abupt")


def current_variant(config: dict) -> str | None:
    """从准备域推断 Transolver 表面/体场；其它组合无变体。"""
    if model_id(config) != "transolver3" or dataset_id(config) != "shapenet_car":
        return None
    domains = set((config.get("trainprep") or {}).get("domains") or {})
    if domains == {"volume"}:
        return "volume"
    return "surface"


def resolve_case(dataset_key: str, model_key: str, variant: str | None = None) -> str | None:
    """按数据集、模型和变体选取官方起步预设；多变体时默认表面。"""
    matches = [
        (case_id, item)
        for case_id, item in CASES.items()
        if item["dataset_id"] == dataset_key and item["model_id"] == model_key
    ]
    if not matches:
        return None
    if variant:
        for case_id, item in matches:
            if item.get("variant") == variant:
                return case_id
    preferred = variant or ("surface" if dataset_key == "shapenet_car" and model_key == "transolver3" else None)
    if preferred:
        for case_id, item in matches:
            if item.get("variant") == preferred:
                return case_id
    return matches[0][0]


def official_variants(dataset_key: str, model_key: str) -> list[dict]:
    """返回当前数据集下该模型的官方变体。"""
    return [
        {"id": item["variant"], "name": VARIANT_LABELS.get(item["variant"], item["variant"])}
        for item in CASES.values()
        if item["dataset_id"] == dataset_key
        and item["model_id"] == model_key
        and item.get("variant")
    ]


def describe_model_case(service, project: str, identity: str, case_id: str, captured: dict) -> dict:
    """描述同数据集的目标默认值；候选配置不写入任务或创建研究版本。"""
    raw = case_configuration(service, case_id)
    if CASES[case_id]["dataset_id"] != dataset_id(captured["config"]):
        raise ValueError("model_case_dataset_mismatch")
    described = task.inspect_task(
        service.project(project),
        identity,
        "describe_case",
        revision=captured["revision"],
        configuration=raw,
        output_dir=str(service.settings.root / "inspections" / uuid4().hex),
    )
    config = described["configuration"]
    return {
        "id": case_id,
        **CASES[case_id],
        "structure_version": {"id": "default", "name": "案例默认"},
        "component": raw["components"]["model"],
        "model": config["model"],
        "train": config["train"],
        "trainprep": config["trainprep"],
        "capabilities": described["capabilities"],
    }


def describe_official_model(
    service, project: str, identity: str, model_key: str, captured: dict, variant: str | None
) -> dict:
    """按官方模型身份描述当前数据集下的起步预设。"""
    kind = dataset_id(captured["config"])
    case_id = resolve_case(kind, model_key, variant)
    if case_id is None:
        raise ValueError("unknown_registered_model")
    described = describe_model_case(service, project, identity, case_id, captured)
    variants = official_variants(kind, model_key)
    variant_defaults = {}
    for item in variants:
        if item["id"] == described.get("variant"):
            variant_defaults[item["id"]] = {
                "id": model_key,
                "model_id": model_key,
                "model": described["model"],
                "train": described["train"],
                "trainprep": described["trainprep"],
                "capabilities": described["capabilities"],
                "component": described["component"],
            }
            continue
        extra = describe_model_case(
            service, project, identity, resolve_case(kind, model_key, item["id"]), captured
        )
        variant_defaults[item["id"]] = {
            "id": model_key,
            "model_id": model_key,
            "model": extra["model"],
            "train": extra["train"],
            "trainprep": extra["trainprep"],
            "capabilities": extra["capabilities"],
            "component": extra["component"],
        }
    return {
        **described,
        "id": model_key,
        "name": MODELS[model_key]["name"],
        "case_id": case_id,
        "variants": variants,
        "variant_defaults": variant_defaults,
    }


def model_options(service, project: str, identity: str) -> dict:
    """提供两个官方模型和同数据集用户预设；创建来源不代替当前模型。"""
    from .model_presets import describe_preset, list_presets, match_preset

    captured = task.read_configuration(service.project(project), identity)
    kind = dataset_id(captured["config"])
    current_model = model_id(captured["config"])
    variant = current_variant(captured["config"])
    options = []
    for key in MODELS:
        if resolve_case(kind, key) is None:
            continue
        if not (
            service.settings.template.parent.parent
            / "examples/aero_cfd"
            / resolve_case(kind, key, variant if key == current_model else None)
            / "config.yaml"
        ).is_file():
            continue
        options.append(
            describe_official_model(
                service,
                project,
                identity,
                key,
                captured,
                variant if key == current_model else None,
            )
        )
    presets = []
    for record in list_presets(service, project, kind):
        presets.append(describe_preset(service, project, identity, record, captured))
    current_preset = match_preset(captured["config"], presets)
    return {
        "revision": captured["revision"],
        "dataset_id": kind,
        "current_model_id": current_model,
        "current_variant": variant,
        "current_preset_id": current_preset,
        "options": options,
        "presets": presets,
        "trace_available": _trace_ready(service, project, identity),
    }


def _trace_ready(service, project: str, identity: str) -> bool:
    """结构跟踪只看是否已有正式物理来源，不改任务绑定。"""
    from .trace_source import latest_trace_source

    try:
        latest_trace_source(service, project, identity)
    except ValueError:
        return False
    return True
