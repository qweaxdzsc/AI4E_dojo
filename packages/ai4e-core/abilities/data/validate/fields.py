"""同组数量、归属与行身份校验，返回可记录的报告。"""

from collections.abc import Mapping, Sequence
from typing import TypedDict

import numpy as np

from ai4e_core.abilities.data.extract.records import FieldRecord, GroupContract
from ai4e_core.base.events import traced


class ValidationIssue(TypedDict):
    """可定位到样本、组和字段的校验失败。"""

    sample: str
    group: str
    field: str
    expected: int | None
    actual: int | None
    reason: str


class ValidationReport(TypedDict):
    """成功和失败使用同一个报告契约。"""

    valid: bool
    sample: str
    checked: int
    issues: list[ValidationIssue]


class FieldValidationError(ValueError):
    """携带完整报告，供执行层序列化。"""

    def __init__(self, report: ValidationReport):
        self.report = report
        super().__init__(f"同组校验失败: {report['issues']}")


def validate_records(
    records: Sequence[FieldRecord], groups: Mapping[str, GroupContract], *, sample: str = ""
) -> ValidationReport:
    """即使没有筛选也检查每行身份；不使用名称后缀推断归属。"""
    issues: list[ValidationIssue] = []

    def issue(group, field, expected, actual, reason):
        issues.append(
            {
                "sample": sample,
                "group": group,
                "field": field,
                "expected": expected,
                "actual": actual,
                "reason": reason,
            }
        )

    for key, group in groups.items():
        ids = np.asarray(group["entity_ids"])
        if (
            group["association"] not in ("point", "cell")
            or not group["source"]
            or group["count"] < 0
            or ids.ndim != 1
            or ids.dtype.kind not in "iu"
            or len(ids) != group["count"]
            or np.any(ids < 0)
            or len(np.unique(ids)) != len(ids)
        ):
            issue(key, "", group["count"], ids.size, "组契约或实体身份无效")
    seen: set[str] = set()
    for record in records:
        name, key = record["name"], record["group"]
        values = np.asarray(record["values"])
        count = int(values.shape[0]) if values.ndim else None
        group = groups.get(key)
        expected = None if group is None else group["count"]
        if not name or name in seen:
            issue(key, name, expected, count, "逻辑名为空或重复")
        seen.add(name)
        if group is None:
            issue(key, name, None, count, "未声明对齐组")
            continue
        if count != expected:
            issue(key, name, expected, count, "首维与组实体数不一致")
        if record["association"] != group["association"]:
            issue(key, name, expected, count, "point/cell 归属不一致")
        if record.get("source") != group["source"]:
            issue(key, name, expected, count, "来源不一致")
        ids = np.asarray(record.get("entity_ids"))
        if ids.dtype.kind not in "iu" or not np.array_equal(ids, group["entity_ids"]):
            issue(key, name, expected, count, "行身份缺失或顺序不一致")
        if not (
            (record["kind"] == "scalar" and values.ndim == 1)
            or (record["kind"] == "vector" and values.ndim == 2 and values.shape[1] == 3)
        ):
            issue(key, name, expected, count, "分量形状与声明不一致")
        if values.dtype.kind not in "biuf" or not np.isfinite(values).all():
            issue(key, name, expected, count, "字段必须为有限实数")
    return {"valid": not issues, "sample": sample, "checked": len(records), "issues": issues}


@traced("字段身份校验")
def require_valid_records(
    records: Sequence[FieldRecord], groups: Mapping[str, GroupContract], *, sample: str = ""
) -> ValidationReport:
    """保留结构化结果；失败时抛出带报告的异常。"""
    report = validate_records(records, groups, sample=sample)
    if not report["valid"]:
        raise FieldValidationError(report)
    return report
