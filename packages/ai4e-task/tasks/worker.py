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
    try:
        from ai4e_core.run import managed_run
        from ai4e_spec.artifacts import RunContext

        code = Path(context["code_dir"])
        entry = payload["entry"]
        sys.path.insert(0, str(code))
        os.chdir(code)
        sys.argv = [str(code / entry["script"]), "--config", str(code / entry["config"])]
        with managed_run(RunContext.from_dict(context)):
            runpy.run_path(str(code / entry["script"]), run_name="__main__")
        summary = read_json(Path(context["run_dir"]) / "summary.json")
        status = "failed" if summary.get("failed", True) else "succeeded"
    except BaseException as exc:  # noqa: BLE001 - worker 必须记录用户退出和信号
        error = f"{type(exc).__name__}: {exc}"
    finally:
        if (folder / "stop.json").exists():
            status = "stopped"
        write_json(
            folder / "finished.json",
            {"run_id": context["run_id"], "status": status, "error": error},
        )
    return 0 if status == "succeeded" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
