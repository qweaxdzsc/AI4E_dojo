"""脚本化领域对象。"""

from dataclasses import dataclass


@dataclass(frozen=True)
class AutomationScript:
    """用户保存的可视化自动化脚本。"""

    name: str
    source: str
    language: str = "python"
