"""独立检查进程，算法日志不污染 JSON 结果。"""

import contextlib
import json
import sys


def render_inspection(request: dict, execute) -> dict:
    """调用声明入口并验证可序列化交接；不接触网络与预测对象。"""
    from ai4e_spec.artifacts.task_operations import json_record

    result = execute(request)
    return json_record(result)


def main():
    """执行固定公开门面，禁止客户端选择任意 Python 对象。"""
    request = json.load(sys.stdin)
    with contextlib.redirect_stdout(sys.stderr):
        from .operation_sources import load_verified_operation, verify_source

        verify_source(request["source"], request["config_dir"])
        execute = load_verified_operation(request["source"], request["config_dir"])
        result = render_inspection(request, execute)
        verify_source(request["source"], request["config_dir"])
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
