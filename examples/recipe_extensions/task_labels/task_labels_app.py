"""本地研究 application：在已有控制描述上增加明确生产名称条件。"""


def inspect(request):
    """只增加校准输入的名称条件；其他管理操作保持控制应用的可用边界。"""
    from ai4e_contrib.application.pde_control.safediffcon.operations import (
        inspect as control_inspect,
    )

    description = control_inspect(request)
    if request.get("operation") == "describe_task":
        description["inputs"]["inputs.posttrain.preparation_cal"]["name"] = "cal"
    return description
