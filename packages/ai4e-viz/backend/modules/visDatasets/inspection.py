"""数据集业务检测入口，与服务健康检查严格分离。"""

from __future__ import annotations

from typing import Any

from .domain import InspectionIssue


def inspect_profile(profile: dict[str, Any]) -> list[InspectionIssue]:
    """根据已有解析画像生成基础质量问题，不重新读取或猜测源文件内容。"""

    issues: list[InspectionIssue] = []
    if profile.get("failed"):
        issues.append(InspectionIssue(code="parse_failed", severity="error", scope="file", message="源文件解析失败", evidence={"error": profile.get("error")}, suggestion="检查文件格式与完整性后重新上传"))
    if profile.get("nan_count", 0):
        issues.append(InspectionIssue(code="contains_nan", severity="warning", scope="values", message="数据包含NaN", evidence={"nan_count": profile["nan_count"]}, suggestion="确认缺失值处理策略"))
    return issues
