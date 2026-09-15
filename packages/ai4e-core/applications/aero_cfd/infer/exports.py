"""固定推理结果表格导出，切换视图不触发模型预测。"""

from ai4e_core.abilities.eval.catalog import metric_catalog
from ai4e_core.abilities.report import export_tables


def export_results(value: dict, path: str, *, format: str, selection: dict | None = None) -> dict:
    """按同一展示选择导出统计与明细，保留完整来源。"""
    selection = selection or {}
    if set(selection) - {"field_id", "metric", "split", "table"}:
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
    export_tables(path, tables, format=format)
    return {"path": path, "rows": len(details), "format": format}
