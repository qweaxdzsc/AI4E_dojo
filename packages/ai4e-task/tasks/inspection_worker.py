"""独立检查进程，算法日志不污染 JSON 结果。"""

import contextlib
import json
import sys
from pathlib import Path

from .operations import load_operation, operation_target


def render_inspection(request: dict, execute) -> dict:
    """案例检查取出网络后交给可视化出图；其他操作仍走原门面。"""
    result = execute(request)
    if request.get("operation") != "trace_model":
        return result
    if not isinstance(result, dict) or "network" not in result or "inputs" not in result:
        return result
    from ai4e_viz.inspect.model_graph import export_platform_views

    return export_platform_views(
        result["network"],
        result["inputs"],
        Path(request["output_dir"]),
        revision=result["revision"],
        input_source=result["input_source"],
        predict=result.get("predict"),
    )


def main():
    """执行固定公开门面，禁止客户端选择任意 Python 对象。"""
    request = json.load(sys.stdin)
    with contextlib.redirect_stdout(sys.stderr):
        execute = load_operation(
            request.get("target") or operation_target(request["config_dir"], "inspect")
        )
        result = render_inspection(request, execute)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
