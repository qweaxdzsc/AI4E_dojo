"""脚本化提取、校验和保存用例。"""

from .domain import AutomationScript


def validate_script(script: AutomationScript) -> AutomationScript:
    """校验脚本基本不变量；目录重构阶段不执行任意用户代码。"""

    if not script.name.strip():
        raise ValueError("脚本名称不能为空")
    if not script.source.strip():
        raise ValueError("脚本内容不能为空")
    return script
