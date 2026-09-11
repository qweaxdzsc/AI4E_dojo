"""独立检查进程，算法日志不污染 JSON 结果。"""

import contextlib
import json
import sys


def main():
    """执行固定公开门面，禁止客户端选择任意 Python 对象。"""
    request = json.load(sys.stdin)
    config = request.get("config", {})
    if "components" not in config and {"rawprep", "trainprep", "model", "train", "post"} <= set(
        config
    ):
        request["component_provider"] = "ai4e_contrib.application.aero_cfd"
    with contextlib.redirect_stdout(sys.stderr):
        from ai4e_core.applications.aero_cfd.inspection import execute

        result = execute(request)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
