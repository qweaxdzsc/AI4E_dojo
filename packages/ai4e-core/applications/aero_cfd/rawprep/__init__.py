"""外流前处理业务步骤；recipe 排列步骤，run 执行样本循环。"""

from .derive import (
    GeometryAbility,
    GeometryDomainInput,
    GeometryDomainResult,
    configured_geometry_enabled,
    derive_configured_geometry,
)
from .read import (
    DomainResult,
    FieldConfig,
    dataread,
    discover_samples,
    enumerate_sample_relatives,
    extract_configured_sample,
)
from .save import SampleResult, tensorize, write_tensors
from .stats import resolve_statistics

__all__ = [
    "DomainResult",
    "FieldConfig",
    "GeometryAbility",
    "GeometryDomainInput",
    "GeometryDomainResult",
    "SampleResult",
    "configured_geometry_enabled",
    "dataread",
    "derive_configured_geometry",
    "derive_geometry",
    "discover_samples",
    "enumerate_sample_relatives",
    "extract_configured_sample",
    "extract_fields",
    "filter_points",
    "resolve_statistics",
    "select_fields",
    "tensorize",
    "validate_fields",
    "write_tensors",
]

# Dataset 装配兼容独立单样本调用；公开入口不暴露 Stage/partial。
from .dataset import (
    compute_statistics,
    derive_geometry,
    encode,
    extract_fields,
    filter_points,
    open_source,
    publish_dataset,
    read,
    save_sample,
    select_fields,
    to_tensors,
    validate_fields,
)
from .mapping import FieldMapParameters, map_fields

__all__ += ["compute_statistics", "publish_dataset", "read", "save_sample", "to_tensors"]
__all__ += ["FieldMapParameters", "encode", "map_fields", "open_source"]
