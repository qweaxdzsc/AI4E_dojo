"""脚本化模块的明确能力边界测试。"""

import pytest

from modules.automation import validate_script
from modules.automation.domain import AutomationScript
from modules.automation.repository import persistence_ready


def test_automation_validates_but_does_not_execute_source() -> None:
    """目录重构阶段只校验脚本，不执行用户代码或虚报持久化。"""

    script = AutomationScript(name="提取压力峰值", source="print('kept as text')")
    assert validate_script(script) is script
    assert persistence_ready() is False
    with pytest.raises(ValueError):
        validate_script(AutomationScript(name="", source="pass"))
