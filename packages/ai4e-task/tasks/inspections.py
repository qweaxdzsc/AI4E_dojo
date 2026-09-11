"""任务检查公开门面；固定配置后在独立算法进程执行。"""

import json
import subprocess
import sys
from pathlib import Path

from .configuration import read_configuration
from .query import get_task


def inspect_task(
    project,
    task_id: str,
    operation: str,
    *,
    revision: str,
    output_dir: str,
    selection: dict | None = None,
    on_process_started=None,
) -> dict:
    """使用任务配置快照检查；只调用受信任的领域公开入口。"""
    captured = read_configuration(project, task_id)
    if captured["revision"] != revision:
        raise ValueError("configuration_revision_conflict")
    recipe = Path(get_task(project, task_id)["directory"]) / "recipe"
    if selection and selection.get("bindings"):
        from omegaconf import OmegaConf

        cfg = OmegaConf.create(captured["config"])
        for key, value in selection["bindings"].items():
            if key not in {
                "train.manifest",
                "train.preparation",
                "post.checkpoint",
                "trainprep.normalization.statistics",
            }:
                raise ValueError("unsupported_inspection_binding")
            OmegaConf.update(cfg, key, value, force_add=True)
        captured["config"] = OmegaConf.to_container(cfg, resolve=False)
    request = {
        "operation": operation,
        "config": captured["config"],
        "output_dir": output_dir,
        "selection": selection or {},
        "config_dir": str(recipe),
        "revision": revision,
    }
    if operation == "compare_fields":
        request["inputs"] = (selection or {}).get("comparison_inputs", [])
    process = subprocess.Popen(
        [sys.executable, "-m", "ai4e_task.tasks.inspection_worker"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=recipe,
    )
    try:
        if on_process_started is not None:
            on_process_started(process)
        stdout, stderr = process.communicate(json.dumps(request), timeout=300)
    except BaseException:
        process.kill()
        process.communicate()
        raise
    if process.returncode:
        error_root = Path(output_dir)
        error_root.mkdir(parents=True, exist_ok=True)
        (error_root / "inspection-error.log").write_text(stderr, encoding="utf-8")
        lines = [line.strip() for line in stderr.splitlines() if line.strip()]
        message = lines[-1] if lines else "案例检查进程失败"
        for prefix in ["ValueError: ", "RuntimeError: ", "FileNotFoundError: ", "KeyError: "]:
            if message.startswith(prefix):
                message = message[len(prefix) :]
        raise ValueError(message[:600])
    return json.loads(stdout)
