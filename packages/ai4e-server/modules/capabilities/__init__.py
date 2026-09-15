"""能力上下文公开门面：登记案例、官方模型与用户预设。"""

from .model_cases import CASES, describe_model_case, describe_official_model, model_options, resolve_case
from .model_presets import export_preset, load_preset

__all__ = [
    "CASES",
    "describe_model_case",
    "describe_official_model",
    "export_preset",
    "load_preset",
    "model_options",
    "resolve_case",
]
