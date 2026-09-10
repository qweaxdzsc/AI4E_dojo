"""外流案例的可见业务流程：声明步骤顺序和参数，不实现算法或样本循环。"""

from functools import partial

from ai4e_core.applications.aero_cfd import rawprep as pre
from ai4e_core.applications.base import Stage
from ai4e_core.run import for_each


def build_sample(cfg) -> Stage:
    """单样本业务流程；每一步均可独立替换或调用。"""
    return Stage(
        "pre.sample",
        [
            partial(pre.dataread, config=cfg),
            pre.extract_fields,
            partial(pre.derive_geometry, enabled=pre.configured_geometry_enabled(cfg)),
            partial(pre.select_fields, output=cfg["pre"]["output"]),
            pre.validate_fields,
            partial(pre.filter_points, filters=cfg["pre"].get("filters", {})),
            pre.tensorize,
            pre.write_tensors,
        ],
    )


def build(cfg) -> Stage:
    """作业流程：发现样本、通用执行、确定统计量。"""
    return Stage(
        "pre",
        [
            partial(pre.discover_samples, config=cfg),
            for_each(build_sample(cfg)),
            partial(pre.resolve_statistics, stats=cfg["pre"].get("stats", {})),
        ],
    )
