"""数据格式、数据语义、画像与检测状态的领域定义。"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class InspectionIssue:
    """一条可定位、可解释、可给出修复建议的数据检测问题。"""

    code: str
    severity: str
    scope: str
    message: str
    evidence: dict[str, Any] = field(default_factory=dict)
    suggestion: str | None = None
