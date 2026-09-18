"""推理检查子进程：只调用 core 公开门面，管理进程不导入训练栈。"""

import contextlib
import json
import sys


def main() -> None:
    """从受控父进程接收固定请求；不允许指定任意函数路径。"""
    request = json.load(sys.stdin)
    with contextlib.redirect_stdout(sys.stderr):
        from .operations import load_operation

        result = load_operation(request.pop("target"))(request)
    print(json.dumps(result, ensure_ascii=False, allow_nan=False))


if __name__ == "__main__":
    main()
