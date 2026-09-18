"""AB-UPT 官方业务参数适配；不修改模型计算。"""

from ai4e_core.applications.aero_cfd.train import resolve_training

MODEL_DEFAULTS = {
    "dim": 192,
    "geometry_depth": 6,
    "num_heads": 3,
    "blocks": "pscscscscsc",
    "radius": 9.0,
}


def expand_defaults(config: dict) -> dict:
    """补齐模型、优化、调度、检查点与损失默认值；``gpu`` 映到 ``cuda``，设备默认 ``auto``。"""
    result = resolve_training(config, validate=False)
    model = result.setdefault("model", {})
    parameters = model.setdefault("parameters", {})
    for key, value in MODEL_DEFAULTS.items():
        parameters.setdefault(key, value)
    model.setdefault("initial_weights", None)
    model.setdefault("freeze", [])
    if model.get("data_specs"):
        parameters.setdefault(
            "num_domain_decoder_blocks", {d: 12 for d in model["data_specs"]["domains"]}
        )
    return result


def validate_joint(config: dict) -> None:
    """字段、输出、采样预算和批次限制任一不合则拒绝启动。"""
    resolve_training(config, validate=True)
    sampling = config.get("sampling") or {}
    geometry = int((sampling.get("geometry") or {}).get("max_points") or 0)
    supernodes = int((sampling.get("supernodes") or {}).get("num_points") or 0)
    if supernodes and geometry and supernodes > geometry:
        raise ValueError("超节点预算超过几何点数")
    heads = int((config.get("model") or {}).get("parameters", {}).get("num_heads") or 0)
    dim = int((config.get("model") or {}).get("parameters", {}).get("dim") or 0)
    if heads and dim and dim % heads != 0:
        raise ValueError("模型宽度必须能被头数整除")


def apply_resolved(config: dict, *, validate: bool = True) -> dict:
    """展开默认值，可选做联合校验，返回最终生效配置。"""
    resolved = expand_defaults(config)
    if validate:
        resolve_training(resolved, validate=True)
        validate_joint(resolved)
    return resolved
