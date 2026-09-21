"""GeoTransolver 外流公开模型连接；不表示平台页面已经登记。"""

from .binding import (
    SOURCE,
    collate,
    construct,
    describe,
    loss,
    optimizer_factory,
    predict,
    predict_sample,
    prepare_inputs,
    prepare_sample,
    scheduler_factory,
    training_parameters,
)
from .configuration import resolve

__all__ = [
    "SOURCE",
    "collate",
    "construct",
    "describe",
    "loss",
    "optimizer_factory",
    "predict",
    "predict_sample",
    "prepare_inputs",
    "prepare_sample",
    "resolve",
    "scheduler_factory",
    "training_parameters",
]

INFERENCE_CAPABILITIES = {"query_chunk_size": True, "physical_fields": True}
