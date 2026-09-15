"""固定推理结果的公开评价与交付接口；兼容子模块仍保持原入口。"""

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
    "run_evaluation",
]
