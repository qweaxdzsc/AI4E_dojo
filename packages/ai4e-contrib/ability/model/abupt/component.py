"""AB-UPT 组件公开出口；保留原构造器身份与数值行为。"""

from ai4e_core.applications.aero_cfd.train.resolve import apply_resolved as resolve

from .batch import collate
from .inference import InferenceContext
from .model import SOURCE, construct, describe, predict
from .sampling import prepare_inputs

__all__ = [
    "SOURCE",
    "InferenceContext",
    "collate",
    "construct",
    "describe",
    "predict",
    "prepare_inputs",
    "resolve",
]
