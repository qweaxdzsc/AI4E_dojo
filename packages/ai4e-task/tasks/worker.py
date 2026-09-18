"""子进程使用 core 公共上下文执行用户脚本；控制记录留在执行区。"""

import os
import runpy
import signal
import sys
from pathlib import Path

from ..storage.files import read_json, write_json


def main(request_path: str) -> int:
    """执行已捕获入口，只有 core 完整摘要和正常退出才报告成功。"""
    request = Path(request_path).resolve()
    payload = read_json(request)
    context = payload["context"]
    folder = request.parent

    def interrupted(signum, frame):
        raise KeyboardInterrupt("stop requested")

    signal.signal(signal.SIGTERM, interrupted)
    write_json(folder / "started.json", {"pid": os.getpid(), "run_id": context["run_id"]})
    status, error = "failed", None
    project = payload.get("project")
    plans = payload.get("shared_outputs", [])
    try:
        if project:
            from ..storage.shared_datasets import resolve_reference
            from .assets import validate_asset

            for asset in context.get("assets", {}).values():
                if asset.get("shared_dataset"):
                    from .assets import asset_path

                    current = resolve_reference(project, asset_path(project, asset))
                    if (
                        not current
                        or current["status"] != "available"
                        or current["source"] != asset["source"]
                    ):
                        raise ValueError("shared_dataset_changed_before_execution")
                    validate_asset(project, asset)
        if plans:
            from ..storage.shared_datasets import begin

            begin(project, plans, context)
        from ai4e_core.run import managed_run
        from ai4e_spec.artifacts import RunContext

        code = Path(context["code_dir"])
        entry = payload["entry"]
        sys.path.insert(0, str(code))
        os.chdir(code)
        sys.argv = [str(code / entry["script"]), "--config", str(code / entry["config"])]
        if payload.get("overwrite"):
            sys.argv.append("--overwrite")
        with managed_run(RunContext.from_dict(context), allow_unmanaged=True):
            runpy.run_path(str(code / entry["script"]), run_name="__main__")
        summary = read_json(Path(context["run_dir"]) / "summary.json")
        status = "failed" if (
            summary.get("failed", True) or summary.get("research_status") == "incomplete"
        ) else "succeeded"
    except BaseException as exc:  # noqa: BLE001 - worker 必须记录用户退出和信号
        error = f"{type(exc).__name__}: {exc}"
    finally:
        if (folder / "stop.json").exists():
            status = "stopped"
        if plans:
            from ..storage.shared_datasets import finish

            try:
                finish(project, plans, context["run_id"], succeeded=status == "succeeded")
            except BaseException as exc:  # noqa: BLE001 - 发布中断也须留下失败收据
                status, error = "failed", f"shared_dataset_publish_failed: {exc}"
                finish(project, plans, context["run_id"], succeeded=False)
        write_json(
            folder / "finished.json",
            {"run_id": context["run_id"], "status": status, "error": error},
        )
    return 0 if status == "succeeded" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
