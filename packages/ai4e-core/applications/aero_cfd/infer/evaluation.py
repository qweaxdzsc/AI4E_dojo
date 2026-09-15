"""具名物理场评价及跨样本统计；只交接真实来源与数值。"""

from collections import defaultdict

from ai4e_core.abilities.eval.aggregation import summarize
from ai4e_core.abilities.eval.catalog import DEFAULT_METRICS, METRICS, metric_catalog
from ai4e_core.abilities.eval.result_metrics import evaluate_arrays


def evaluate_sample(item, selections, metrics=None) -> list[dict]:
    """使用当前预测数组评价选中分量，结果不依赖是否保存张量。"""
    metrics = DEFAULT_METRICS if metrics is None else metrics
    valid_ids = {m["id"] for m in metric_catalog()}
    if not metrics or set(metrics) - valid_ids:
        raise ValueError("未知或空推理指标")
    chosen = [m for m in metrics if m in METRICS]
    rows = []
    for selection in selections:
        domain = item.domains[selection["domain"]]
        key = domain["targets"].get(selection["field"])
        value = (
            {
                "values": {m: None for m in chosen},
                "undefined": {m: selection.get("reason", "字段没有对应真值") for m in chosen},
                "valid_count": 0,
            }
            if key is None
            else (
                evaluate_arrays(
                    item.payloads[key + ".prediction"],
                    item.payloads[key + ".truth"],
                    component=selection["component"],
                    mask=item.payloads[domain["validity"]] if domain.get("validity") else None,
                    metrics=chosen,
                )
                if chosen
                else {"values": {}, "undefined": {}}
            )
        )
        rows.append(
            {
                **selection,
                **value,
                "field_id": selection["id"],
                "sample": item.name,
                "status": "succeeded",
                "selected_metrics": list(metrics),
                "algorithm": "physical-metrics-v2",
            }
        )
    return rows


def summarize_records(records: list[dict]) -> list[dict]:
    """按权重、分片和物理量分组；缺失结果不会被当作完整成功。"""
    groups = defaultdict(list)
    for row in records:
        groups[(row["checkpoint_id"], row["split"], row["field_id"])].append(row)
    output = []
    for (checkpoint, split, field), rows in groups.items():
        sample = rows[0]
        for metric in dict.fromkeys(
            m for r in rows for m in r.get("selected_metrics", r.get("values", {}))
        ):
            successful = [r for r in rows if r.get("status") == "succeeded"]

            def metric_value(row, metric=metric):
                seconds = row.get("timings", {}).get("prediction")
                if metric == "prediction_seconds":
                    return seconds
                if metric == "throughput":
                    return 1 / seconds if seconds and seconds > 0 else None
                return row["values"].get(metric)

            stat = summarize(
                [metric_value(r) for r in successful],
                expected=sample.get("expected", len(rows)),
                failed=len(rows) - len(successful),
            )
            rule = next(m["unit_rule"] for m in metric_catalog() if m["id"] == metric)
            unit = (
                sample.get("unit")
                if rule == "field"
                else (f"({sample['unit']})²" if sample.get("unit") else None)
                if rule == "field_squared"
                else rule
            )
            seconds = sum(r.get("timings", {}).get("prediction", 0) for r in successful)
            output.append(
                {
                    "checkpoint_id": checkpoint,
                    "checkpoint": sample["checkpoint"],
                    "split": split,
                    "field_id": field,
                    "field": sample.get("label", field),
                    "metric": metric,
                    "unit": unit,
                    **stat,
                    "algorithm": sample.get("algorithm", "physical-metrics-v2"),
                    "aggregation_algorithm": "sample-statistics-v1",
                    "checkpoint_revision": sample.get("checkpoint_revision"),
                    "source_runs": list(dict.fromkeys(r.get("run_id") for r in rows)),
                    "source_protocols": list(dict.fromkeys(r.get("protocol") for r in rows)),
                    "undefined_reasons": list(
                        dict.fromkeys(
                            r.get("undefined", {}).get(metric)
                            for r in rows
                            if r.get("undefined", {}).get(metric)
                        )
                    ),
                    "prediction_seconds": seconds,
                    "throughput": len(successful) / seconds if seconds else None,
                }
            )
    return output
