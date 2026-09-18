"""固定推理结果的公开评价与交付接口；兼容子模块仍保持原入口。"""

from . import physical
from .result_evaluation import (
    describe_result_fields,
    evaluate_result,
    export_evaluation,
    metric_catalog,
    run_evaluation,
)

__all__ = [
    "describe_result_fields",
    "evaluate_result",
    "export_evaluation",
    "metric_catalog",
    "physical",
    "run_evaluation",
]

from .analysis import check_analysis, open_analysis, publish_analysis
from .analysis_export import save_sample
from .field_analysis import (
    clip_field,
    contour_field,
    profile_field,
    probe_field,
    region_statistics,
    slice_field,
    streamlines,
    vector_field,
)
from .field_binding import bind_mesh, read_fields
from .field_rendering import render_field, render_profile
from .result_evaluation import evaluate_fields

__all__ += [
    "check_analysis",
    "open_analysis",
    "publish_analysis",
    "save_sample",
    "clip_field",
    "contour_field",
    "profile_field",
    "probe_field",
    "region_statistics",
    "slice_field",
    "streamlines",
    "vector_field",
    "bind_mesh",
    "read_fields",
    "render_field",
    "render_profile",
    "evaluate_fields",
]
