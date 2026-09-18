"""固定推理结果表格导出，切换视图不触发模型预测。"""

from ai4e_core.abilities.eval.catalog import metric_catalog
from ai4e_core.abilities.report import export_tables

from .evaluation import record_metric


def export_results(value: dict, path: str, *, format: str, selection: dict | None = None) -> dict:
    """按同一展示选择导出统计与明细，保留完整来源。"""
    selection = selection or {}
    if set(selection) - {"field_id", "metric", "split", "table", "view"}:
        raise ValueError("未知导出选择")

    def include(row):
        return all(
            not selection.get(k) or row.get(k) == selection[k] for k in ("field_id", "split")
        )

    stats = [
        r
        for r in value["statistics"]
        if include(r) and (not selection.get("metric") or r["metric"] == selection["metric"])
    ]
    details = []
    for row in value["records"]:
        if include(row):
            details.append(
                {
                    **{k: v for k, v in row.items() if k != "values"},
                    **{
                        k: v
                        for k, v in row["values"].items()
                        if not selection.get("metric") or k == selection["metric"]
                    },
                }
            )
    tables = {
        "统计": stats,
        "逐样本指标": details,
        "指标说明": metric_catalog(),
        "来源": [value.get("batch", {})],
    }
    if selection.get("table") == "details":
        tables = {"逐样本指标": details, "统计": stats, "指标说明": metric_catalog()}
    if "view" in selection:
        tables = {"当前表格": comparison_table(value, selection["view"]), **tables}
    export_tables(path, tables, format=format)
    return {"path": path, "rows": len(details), "format": format}


def comparison_table(value: dict, config: dict) -> list[dict]:
    """按页面字段配置展开固定值；Checkpoint全样本聚合由统一评价装配提供。"""
    if set(config) - {"mode", "checkpoint_id", "pairs", "aggregations"}:
        raise ValueError("未知表格配置")
    mode = config.get("mode")
    if mode not in {"checkpoint", "sample"}:
        raise ValueError("未知对比模式")
    pairs, aggregates = config.get("pairs", []), config.get("aggregations", [])
    if not pairs or (
        mode == "checkpoint"
        and (not aggregates or set(aggregates) - {"mean", "median", "p90", "max"})
    ):
        raise ValueError("表格需要选择指标和有效聚合方式")
    stats, records = value["statistics"], value["records"]
    columns = []
    for pair in pairs:
        options = [
            r
            for r in stats
            if r["field_id"] == pair.get("field_id") and r["metric"] == pair.get("metric")
        ]
        if not options:
            raise ValueError("物理量与指标组合未交付")
        description = options[0]
        for aggregate in aggregates if mode == "checkpoint" else [""]:
            field_label = description["field"]
            if any(
                r["field"] == field_label and r["field_id"] != description["field_id"]
                for r in stats
            ):
                field_label += " [" + description["field_id"] + "]"
            label = f"{field_label} · {description['metric']}"
            if aggregate:
                label += (
                    " · "
                    + {"mean": "Mean", "median": "Median", "p90": "P90", "max": "Max"}[aggregate]
                )
            if description.get("unit"):
                label += f" ({description['unit']})"
            columns.append((pair, aggregate, label))
    rows = {}
    if mode == "checkpoint":
        for record in stats:
            if record["split"] != "__all__":
                continue
            for pair, aggregate, label in columns:
                if record["field_id"] == pair["field_id"] and record["metric"] == pair["metric"]:
                    row = rows.setdefault(
                        record["checkpoint_id"],
                        {
                            "Checkpoint": record["checkpoint"],
                            "样本数": record["expected"],
                            **{c[2]: None for c in columns},
                        },
                    )
                    row[label] = record[aggregate]
    else:
        selected = [r for r in records if r["checkpoint_id"] == config.get("checkpoint_id")]
        if not selected:
            raise ValueError("样本对比需要选择已有Checkpoint")
        for record in selected:
            row = rows.setdefault(
                (record["split"], record["sample"]),
                {
                    "样本": record["sample"],
                    "分片": {
                        "train": "训练集",
                        "eval": "验证集",
                        "validation": "验证集",
                        "test": "测试集",
                    }.get(record["split"], record["split"]),
                    **{c[2]: None for c in columns},
                },
            )
            for pair, _, label in columns:
                if record["field_id"] == pair["field_id"]:
                    row[label] = record_metric(record, pair["metric"])
    return list(rows.values())
