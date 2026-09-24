"""外流固定结果的公共资产及样本等权指标交接。"""

from collections import defaultdict
from pathlib import Path

from ai4e_core.abilities.eval.catalog import metric_catalog


def register_results(session, path, report, *, stage="infer"):
    """保留完整预测文件依赖；单位不明或部分样本缺量时不登记可比标量。"""
    dependencies = sorted({str(Path(row["manifest"]).parent)
                           for row in report["results"] if row.get("manifest")})
    session.record_asset("results", path, kind="other", stage=stage,
                         dependencies=dependencies, semantics={"type": "aero.inference"})
    protocol = report["protocol"]
    groups = defaultdict(list)
    for sample in report["results"]:
        for row in sample.get("metric_records", []):
            for metric, value in row.get("values", {}).items():
                if value is not None:
                    groups[(row["field_id"], metric)].append((row, value))
    rules = {item["id"]: item["unit_rule"] for item in metric_catalog()}
    for (field, metric), rows in groups.items():
        if len(rows) != len(report["results"]):
            continue
        row = rows[0][0]
        rule = rules[metric]
        unit = row.get("unit") if rule == "field" else (
            f"({row['unit']})²" if row.get("unit") else None
        ) if rule == "field_squared" else rule
        if not unit:
            continue
        session.record_metric(
            f"{field}/{metric}", sum(value for _, value in rows) / len(rows),
            stage=stage, assets=[path, *dependencies], semantics={
                "field": field, "unit": unit, "split": protocol["split"],
                "statistic": {"metric": metric, "reduction": "sample_equal_mean",
                              "algorithm": row["algorithm"]},
                "data_identity": {"dataset": protocol["dataset"],
                                  "samples": protocol["samples"]},
            },
        )
