"""固定结果评价子进程；数值计算和文件交付只调用core公开接口。"""

import json
import sys

from ..storage.files import read_json
from .post_metrics import _folder, update_post_metrics


def main():
    """执行受控评价或显式导出，不接受任意Python入口。"""
    from ai4e_core.applications.aero_cfd.post import export_evaluation, run_evaluation

    if sys.argv[1] == "--export":
        value = json.load(sys.stdin)
        export_evaluation(read_json(value.pop("record")), **value)
        return
    project, task, identity = sys.argv[1:]
    folder = _folder(project, task, identity)
    job = read_json(folder / "request.json")
    update_post_metrics(project, identity, {"status": "running"})
    try:
        result = run_evaluation(
            job,
            publish=lambda change: update_post_metrics(project, identity, change),
            canceled=lambda: (folder / "cancel.json").exists(),
        )
        update_post_metrics(project, identity, result)
    except Exception as exc:
        update_post_metrics(project, identity, {"status": "failed", "error": str(exc)})
        raise


if __name__ == "__main__":
    main()
