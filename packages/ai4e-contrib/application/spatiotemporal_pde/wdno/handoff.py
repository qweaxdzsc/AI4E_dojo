"""WDNO阶段的输入冲突、数组资产与指标语义连接；不改变数值格式。"""

import json
from pathlib import Path

from ai4e_core.base.config.conventions import resolve_input

from .provenance import identity


def split_inputs(cfg: dict, stage: str, explicit: dict | None = None) -> dict:
    """逐分片选择本次返回值或显式输入，两者不同则报错。"""
    names = ("validation", "test") if stage == "post" else ("train", "validation", "test")
    first = "dataset" if stage == "trainprep" else "preparation"
    if explicit is not None and set(explicit) != set(names):
        raise ValueError(f"{stage} 上游分片不完整")
    return {
        split: resolve_input(
            explicit[split] if explicit is not None else None,
            cfg["inputs"][stage][first if split == "train" else split],
            name=f"{stage}.{split}",
        )
        for split in names
    }


def _array_sources(reference):
    """统一解析固定清单的全部数组来源；不重写科学文件和指标定义。"""
    path = Path(reference).resolve()
    record = json.loads(path.read_text())
    dependencies = [(path.parent / field["path"]).resolve() for field in record["fields"].values()]
    for dependency in dependencies:
        if not dependency.is_relative_to(path.parent):
            raise ValueError("数组依赖路径越界")
        if not dependency.is_file():
            raise FileNotFoundError(dependency)
    return path, record, dependencies


def record_arrays(session, references: dict, *, stage: str, kind: str) -> None:
    """登记已经保存的分片及真实数组依赖，供Task查询和引用。"""
    for split, reference in references.items():
        path, _, dependencies = _array_sources(reference)
        session.record_asset(
            split,
            path,
            kind=kind,
            stage=stage,
            dependencies=dependencies,
            bundle_root=path.parent,
        )


def record_metrics(session, results: dict, summary: dict, metrics) -> None:
    """MSE携带目标与样本身份、初帧排除和样本等权口径，拒绝跨定义冒比。"""
    for split, reference in results.items():
        if "mse" not in summary[split]:
            continue
        path, record, dependencies = _array_sources(reference)
        session.record_metric(
            f"{split}_mse",
            summary[split]["mse"],
            stage="post",
            semantics={
                "field": "u",
                "unit": "source_u^2",
                "split": split,
                "statistic": "mse_exclude_initial_frame_sample_mean",
                "data_identity": {
                    key: record["fields"][key]["sha256"] for key in ("ids", "target")
                },
                "definition": identity(metrics),
                "paper_protocol_matched": False,
            },
            assets=[path, *dependencies],
        )
