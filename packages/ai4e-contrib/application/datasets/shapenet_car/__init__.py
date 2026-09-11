"""可复用的数据集适配能力。"""

from .adapter import MANIFEST_PATH, open_dataset

__all__ = ["MANIFEST_PATH", "open_dataset"]

from .physical import open_physical

__all__ += ["open_physical"]


def prepare_physical(cfg, *, executor, session):
    """复用汽车原始处理装配，不改变既有物理张量。"""
    import sys

    from ai4e_core.applications.aero_cfd.anchor_workflow import datapre

    result = datapre(
        cfg,
        dataset_component=sys.modules[__name__],
        model_component=None,
        executor=executor,
        session=session,
    )
    from pathlib import Path

    report = {
        "manifest": str(Path(result["output"]["root"]) / "manifest.json"),
        "output": result["output"],
        "split_counts": {key: len(values) for key, values in result["dataset"].partitions.items()},
    }
    if not result["dry_run"]:
        session.report(report, stage="rawprep")
    return report


from .physical import comparison_mesh

__all__ += ["comparison_mesh", "prepare_physical"]

# 来源坐标中 Y 为竖直方向，显示使用其物理坐标约定。
VIEW_UP = [0, 1, 0]

from .inspection import inspect_dataset

__all__ += ["inspect_dataset"]

from .physical import comparison_metadata

__all__ += ["comparison_metadata"]
