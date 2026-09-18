"""固定结果的分析入口与批次汇总，不执行样本循环。"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ai4e_core.abilities.data.save.arrays import save_json
from ai4e_core.abilities.eval.aggregation import summarize
from ai4e_core.applications.aero_cfd.infer.results import open_results


@dataclass(frozen=True)
class AnalysisSource:
    """仅持有样本引用和固定来源，不持有批量数组或网格。"""

    samples: tuple
    origin: dict
    results: dict


def open_analysis(reference: Any, *, samples: Any = None) -> AnalysisSource:
    """打开已提交推理清单并选择样本；不加载模型与网格。"""
    results = open_results(reference)
    origin = {"id": results["protocol"]["digest"], "protocol": results["protocol"]}
    selected = list(samples or [])
    available = [row["sample"] for row in results["results"]]
    if len(selected) != len(set(selected)) or set(selected) - set(available):
        raise ValueError("后处理样本重复或不属于固定结果")
    refs = tuple(
        {**row, "origin": origin}
        for row in results["results"]
        if not selected or row["sample"] in selected
    )
    if not refs or any(not row.get("manifest") for row in refs):
        raise ValueError("后处理需要已保存的物理场结果")
    return AnalysisSource(refs, origin, results)


def check_analysis(source: AnalysisSource, *, settings: dict) -> dict:
    """检查已声明字段和输出能力参数，不发布产物。"""
    # 清单检查不加载数组；实体、分量和数值门禁在单样本执行时完成。
    for ref in source.samples:
        metadata = json.loads(Path(ref["manifest"]).read_text())
        for selection in settings.get("fields") or []:
            parts = selection.split(":")
            if len(parts) != 3:
                raise ValueError("字段选择必须为 域:字段:类型")
            domain, field, _ = parts
            if field not in metadata.get("domains", {}).get(domain, {}).get("targets", {}):
                raise ValueError("清单缺少选择的物理场: " + selection)
    return {
        "mode": "post_check",
        "samples": len(source.samples),
        "status": "checked",
        "scope": "metadata_only",
    }


def publish_analysis(
    rows: list[dict], *, source: AnalysisSource, output: str | Path, failures: Any = ()
) -> dict:
    """汇总已提交样本的等权指标，保留原推理结果引用以兼容消费者。"""
    groups = {}
    for row in rows:
        for field in row["metrics"]:
            for metric, value in field.get("values", {}).items():
                groups.setdefault(field["id"] + ":" + metric, []).append(value)
    complete = (
        not failures
        and len(rows) == len(source.samples)
        and all(row["status"] == "succeeded" for row in rows)
    )
    result = {
        "version": 1,
        "status": "succeeded" if complete else "partial",
        "origin": source.origin,
        "results": source.results["results"],
        "analysis": rows,
        "failures": list(failures),
        "expected": len(source.samples),
        "completed": len(rows),
        "metrics": {
            key: summarize(values, expected=len(source.samples), failed=len(failures))
            for key, values in groups.items()
        },
    }
    target = Path(output) / source.origin["id"] / "summary.json"
    save_json(target, result)
    return result
