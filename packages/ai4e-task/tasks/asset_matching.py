"""数据候选按生产者标签精确匹配；不从文件名、路径或模型名补标签。"""

from ai4e_spec.artifacts.task_operations import exact_json_equal


def match_asset(asset: dict, requirement: dict, *, status: str) -> dict:
    """返回全部缺失和冲突条件；可选择不等于科学内容已适用。"""
    missing, conflicts = [], []
    if status not in requirement.get("statuses", ["succeeded"]):
        conflicts.append("status")
    for key in ("kind", "stage", "name"):
        if key in requirement:
            if key not in asset:
                missing.append(key)
            elif not exact_json_equal(asset[key], requirement[key]):
                conflicts.append(key)
    semantics = asset.get("semantics", {})
    for key, expected in requirement.get("semantics", {}).items():
        if key not in semantics:
            missing.append("semantics." + key)
        elif not exact_json_equal(semantics[key], expected):
            conflicts.append("semantics." + key)
    return {
        "matches": not missing and not conflicts,
        "missing": missing,
        "conflicts": conflicts,
        "reason": "缺少类型／用途信息" if missing else ("标签或状态不符合" if conflicts else None),
    }
