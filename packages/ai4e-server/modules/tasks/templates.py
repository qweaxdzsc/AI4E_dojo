"""登记科研案例的原始脚本与任务入口适配；不生成算法脚本。"""

import hashlib
import json
import shutil
from pathlib import Path
from tempfile import mkdtemp
from threading import RLock

import ai4e_task as task

_REGISTRATION_LOCK = RLock()

from ..capabilities import CASES

CASE_IDS = set(CASES)


def case_files(service, case_id: str) -> dict[str, bytes]:
    """读取受信任案例原文件，附加现有任务入口的案例数据绑定。"""
    if case_id not in CASE_IDS:
        raise ValueError("unknown_registered_case")
    source = service.settings.template.parent.parent / "examples/aero_cfd" / case_id
    files = {
        str(path.relative_to(source)): path.read_bytes()
        for path in source.rglob("*")
        if path.is_file()
        and "__pycache__" not in path.parts
        and not any(part.startswith(".") for part in path.relative_to(source).parts)
    }
    for name in (
        "configuration.py",
        "pipeline.py",
        "rawprep.py",
        "trainprep.py",
        "train.py",
        "infer.py",
        "post.py",
        "config.yaml",
    ):
        if name not in files:
            raise ValueError("registered_case_file_missing: " + name)
    import yaml

    config = yaml.safe_load(files["config.yaml"])
    entry = json.loads((service.settings.template / "task-entry.json").read_text())
    entry["platform_case"] = case_id
    entry["components"] = config.get("components", {})
    if case_id.startswith("nasa_crm_"):
        for key in ("train_h5", "test_h5", "connectivity_h5"):
            entry["inputs"]["dataset." + key] = "dataset"
    files["task-entry.json"] = json.dumps(entry, ensure_ascii=False, sort_keys=True).encode()
    return files


def register_case_template(service, project: str, case_id: str) -> str:
    """将原案例脚本按内容摘要缓存，再经 task 公开门面登记模板。"""
    files = case_files(service, case_id)
    digest = hashlib.sha256()
    for name, content in sorted(files.items()):
        digest.update(name.encode() + b"\0" + content)
    identity = case_id + "-" + digest.hexdigest()
    cache = service.settings.root / "case-templates"
    cache.mkdir(parents=True, exist_ok=True)
    target = cache / identity
    if not target.exists():
        temporary = Path(mkdtemp(dir=cache))
        try:
            for name, content in files.items():
                path = temporary / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(content)
            try:
                temporary.rename(target)
            except OSError:
                if not target.is_dir():
                    raise
        finally:
            if temporary.exists():
                shutil.rmtree(temporary)
    with _REGISTRATION_LOCK:
        if not any(
            value["id"] == identity for value in task.list_templates(service.project(project))
        ):
            task.register_template(service.project(project), identity, target)
    return identity
