"""固定结果评价子进程；数值计算和文件交付只调用core公开接口。"""

import json
import sys

from ..storage.files import read_json
from .operations import load_operation
from .post_metrics import _folder, update_post_metrics


def main():
    """执行受控评价或显式导出，不接受任意Python入口。"""
    from ai4e_core.run import execute_operation

    if sys.argv[1] == "--export":
        value = json.load(sys.stdin)
        export_evaluation = load_operation(value.pop("target"))
        export_evaluation(read_json(value.pop("record")), **value)
        return
    project, task, identity = sys.argv[1:]
    folder = _folder(project, task, identity)
    job = read_json(folder / "request.json")
    update_post_metrics(project, identity, {"status": "running"})
    try:
        result = execute_operation(
            job,
            load_operation(job["target"]),
            publish=lambda change: update_post_metrics(project, identity, change),
            canceled=lambda: (folder / "cancel.json").exists(),
        )
        update_post_metrics(project, identity, result)
    except Exception as exc:
        update_post_metrics(project, identity, {"status": "failed", "error": str(exc)})
        raise


if __name__ == "__main__":
    main()
