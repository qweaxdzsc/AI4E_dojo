"""控制应用可选管理入口；未实现的专业操作明确不可用。"""


def inspect(request: dict) -> dict:
    """返回控制流程描述；普通脚本运行不依赖管理操作。"""
    if request.get("operation") == "describe_task":
        from .task_description import describe_task

        return describe_task(request["config"])
    raise ValueError(f"operation_unavailable: {request.get('operation')}")
