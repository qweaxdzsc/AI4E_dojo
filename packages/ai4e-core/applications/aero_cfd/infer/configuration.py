"""独立推理参数边界；旧 post 配置只在兼容入口解释。"""

from copy import deepcopy

from ai4e_core.base.config import plain

DEFAULTS = {
    "checkpoint": None,
    "preparation": None,
    "split": "test",
    "samples": [],
    "device": "cpu",
    "query_chunk_size": 16384,
    "evaluate": True,
    "save_predictions": True,
    "export_vtk": True,
}
OPTIONAL = {
    "prediction",
    "metric",
    "sample_metric",
    "derived_fields",
    "overwrite",
    "random_stream",
    "query",
    "sample_indices",
    "results",
    "fields",
    "metrics",
}


def resolve_infer(config: dict) -> dict:
    """校验独立推理参数并补缺；不修改训练或冻结准备声明。"""
    cfg = plain(config)
    settings = cfg.get("infer")
    if not isinstance(settings, dict):
        raise TypeError("独立 infer 需要 infer 参数映射")
    unknown = set(settings) - set(DEFAULTS) - OPTIONAL
    if unknown:
        raise ValueError(f"未知 infer 参数: {sorted(unknown)}")
    settings = {**deepcopy(DEFAULTS), **settings}
    for key in ("fields", "metrics"):
        if key in settings and settings[key] is not None:
            values = settings[key]
            if (
                not isinstance(values, list)
                or not values
                or any(not isinstance(v, str) or not v for v in values)
                or len(values) != len(set(values))
            ):
                raise ValueError("infer." + key + " 必须是非空、不重复的名称列表")
    samples = settings["samples"]
    if not isinstance(samples, list) or any(not isinstance(s, str) or not s for s in samples):
        raise ValueError("infer.samples 必须为有序样本名称列表")
    if len(samples) != len(set(samples)):
        raise ValueError("infer.samples 包含重复样本")
    if not isinstance(settings["split"], str) or not settings["split"]:
        raise ValueError("infer.split 不能为空")
    size = settings["query_chunk_size"]
    if isinstance(size, bool) or not isinstance(size, int) or size < 1:
        raise ValueError("infer.query_chunk_size 必须为正整数")
    for key in ("evaluate", "save_predictions", "export_vtk"):
        if not isinstance(settings[key], bool):
            raise TypeError(f"infer.{key} 必须为布尔值")
    if settings["export_vtk"] and not settings["save_predictions"]:
        raise ValueError("导出网格需要保存预测")
    if not settings["evaluate"] and not settings["save_predictions"]:
        raise ValueError("推理至少需要评价或保存预测")
    if not isinstance(settings["device"], str) or not settings["device"]:
        raise ValueError("infer.device 必须为设备名称")
    cfg["infer"] = settings
    return cfg


def inference_parameters(config: dict) -> dict:
    """给既有模型交付等价内部参数；训练配置副本不会写回用户配置。"""
    cfg = resolve_infer(config)
    cfg["post"] = deepcopy(cfg["infer"])
    cfg.setdefault("train", {})["device"] = cfg["infer"]["device"]
    if cfg["infer"]["preparation"]:
        cfg["train"]["preparation"] = cfg["infer"]["preparation"]
    return cfg


def public_to_business(config: dict) -> dict:
    """将已展开的 checkpoint 用户配置还原为业务声明，供只读检查使用。"""
    cfg = plain(config)
    if "rawprep" in cfg:
        cfg.update(cfg.pop("rawprep"))
        prep = cfg.setdefault("trainprep", {})
        if "normalization" in prep:
            cfg["normalization"] = prep.pop("normalization")
        if "sampling" in cfg.get("model", {}):
            cfg["sampling"] = cfg["model"].pop("sampling")
        elif "sampling" in prep:
            cfg["sampling"] = prep.pop("sampling")
    return cfg
