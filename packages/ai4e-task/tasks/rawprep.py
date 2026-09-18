"""原始处理描述公共门面；算法在既有独立检查进程中解析。"""

from copy import deepcopy
from functools import lru_cache
from pathlib import Path

from .configuration import read_configuration, save_configuration
from .inspections import inspect_task
from .records import get_task


def describe_rawprep(project, task_id):
    """固定当前修订后返回默认配置和处理描述，不修改任务。"""
    captured = read_configuration(project, task_id)
    value = deepcopy(_describe(str(project), task_id, captured["revision"]))
    name = (captured["config"].get("dataset") or {}).get("processed_name")
    from ..projects.datasets import describe_shared_name

    return {
        "revision": captured["revision"],
        **value,
        "processed_name": name or "",
        "processed_name_status": describe_shared_name(project, name or ""),
    }


@lru_cache(maxsize=128)
def _describe(project, task_id, revision):
    """同任务同修订复用纯描述，避免每个读取请求启动数值检查进程。"""
    import yaml

    initial = Path(get_task(project, task_id)["directory"]) / ".dojo/snapshots/creation/config.yaml"
    default_config = yaml.safe_load(initial.read_text()) if initial.is_file() else {}
    return inspect_task(
        project,
        task_id,
        "describe_rawprep",
        revision=revision,
        selection={"case_rawprep": default_config.get("rawprep", {})},
        output_dir=str(Path(get_task(project, task_id)["directory"]) / "inspections"),
    )


def initialize_rawprep(project, task_id):
    """新建平台任务时将实际默认值保存一次；普通读取不产生修订。"""
    value = describe_rawprep(project, task_id)
    current = read_configuration(project, task_id)
    if current["config"].get("rawprep") != value["rawprep"]:
        save_configuration(
            project, task_id, {"rawprep": value["rawprep"]}, revision=value["revision"]
        )


def validate_rawprep_configuration(project, task_id, rawprep, *, revision):
    """由相同数据组件校验待保存配置，不在服务中重写算法规则。"""
    return inspect_task(
        project,
        task_id,
        "validate_rawprep",
        revision=revision,
        output_dir=str(Path(get_task(project, task_id)["directory"]) / "inspections"),
        selection={"rawprep": rawprep},
    )


def expand_rawprep_defaults(recipe):
    """新建快照前由独立算法进程展开默认值，版本从创建起即反映实际配置。"""
    import json
    import subprocess
    import sys

    from omegaconf import OmegaConf

    from ..templates.materialize import read_entry

    recipe = Path(recipe)
    entry = read_entry(recipe)
    if not entry:
        return
    if not entry.get("components", {}).get("application"):
        return
    path = recipe / entry["config"]
    config = OmegaConf.to_container(OmegaConf.load(path), resolve=False)
    if not config.get("components", {}).get("dataset") or "rawprep" not in config:
        return
    request = {
        "operation": "describe_rawprep",
        "selection": {"preserve_expressions": True},
        "config": config,
        "config_dir": str(recipe),
        "output_dir": str(recipe.parent / "inspections"),
    }
    result = subprocess.run(
        [sys.executable, "-m", "ai4e_task.tasks.inspection_worker"],
        input=json.dumps(request),
        text=True,
        capture_output=True,
        cwd=recipe,
        check=False,
        timeout=300,
    )
    if result.returncode:
        raise ValueError("rawprep_defaults: " + result.stderr.strip().splitlines()[-1])
    config["rawprep"] = json.loads(result.stdout)["rawprep"]
    OmegaConf.save(OmegaConf.create(config), path)
