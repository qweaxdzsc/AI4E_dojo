"""任务检查公开门面；固定配置后在独立算法进程执行。"""

import json
import subprocess
import sys
from pathlib import Path

from .configuration import read_configuration
from .records import get_task


def inspect_task(
    project,
    task_id: str,
    operation: str,
    *,
    revision: str,
    output_dir: str,
    selection: dict | None = None,
    configuration: dict | None = None,
    on_process_started=None,
) -> dict:
    """检查固定修订；describe_case 可描述调用者提供的候选配置而不保存任务。"""
    captured = read_configuration(project, task_id)
    if captured["revision"] != revision:
        raise ValueError("configuration_revision_conflict")
    if configuration is not None:
        if operation not in {"describe_case", "describe_rawprep"}:
            raise ValueError("candidate_configuration_requires_description")
        captured["config"] = configuration
    recipe = Path(get_task(project, task_id)["directory"]) / "recipe"
    if selection and selection.get("bindings"):
        from omegaconf import OmegaConf

        from .descriptions import describe_recipe

        cfg = OmegaConf.create(captured["config"])
        description = describe_recipe(recipe, config=captured["config"])["description"] or {}
        for key, value in selection["bindings"].items():
            if key not in description.get("inputs", {}):
                raise ValueError("unsupported_inspection_binding")
            OmegaConf.update(cfg, key, value, force_add=True)
        captured["config"] = OmegaConf.to_container(cfg, resolve=False)
    from .operation_sources import capture_source

    request = {
        "source": capture_source(recipe, "inspect"),
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
        raise ValueError(inspection_failure_message(stderr))
    return json.loads(stdout)


def inspection_failure_message(stderr: str) -> str:
    """整理检查子进程最后一行；键错误保留字段名，不把单独的引号键抛给页面。"""
    lines = [line.strip() for line in stderr.splitlines() if line.strip()]
    message = lines[-1] if lines else "案例检查进程失败"
    if message.startswith("KeyError: "):
        return ("检查缺少必要字段 " + message.removeprefix("KeyError: ").strip())[:600]
    for prefix in ["ValueError: ", "RuntimeError: ", "FileNotFoundError: "]:
        message = message.removeprefix(prefix)
    return message[:600]
