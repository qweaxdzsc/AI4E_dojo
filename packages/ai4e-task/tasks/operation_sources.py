"""固定应用入口来源；安装代码变化明确失败，本地代码随执行副本重定位。"""

import contextlib
import hashlib
import importlib
import importlib.metadata
import json
import subprocess
import sys
from pathlib import Path

from ..storage.snapshots import digest
from .source_dependencies import collect_dependencies


def _python_files(root: Path) -> dict:
    return {
        str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(root.rglob("*.py"))
        if "__pycache__" not in p.parts
    }


def _source(target: str, recipe: Path) -> dict:
    """只在子进程解析模块位置；管理进程不导入用户或训练栈。"""
    module = importlib.import_module(target.rsplit(".", 1)[0])
    path = Path(module.__file__).resolve()
    recipe = recipe.resolve()
    dependencies = collect_dependencies(target, recipe)
    roots = []
    if path.is_relative_to(recipe):
        roots.append({"local": True, "files": _python_files(recipe)})
    else:
        package = importlib.import_module(target.split(".")[0])
        root = Path(package.__file__).resolve().parent
        roots.append({"local": False, "root": str(root), "files": _python_files(root)})
    packages = {name.split(".")[0] for name in dependencies["modules"]}
    for name in ("ai4e_core", "ai4e_spec", *sorted(packages & {"ai4e_contrib"})):
        root = Path(importlib.import_module(name).__file__).resolve().parent
        if not any(item.get("root") == str(root) for item in roots):
            roots.append({"local": False, "root": str(root), "files": _python_files(root)})
    distributions = {}
    package_distributions = importlib.metadata.packages_distributions()
    for name in packages | {"ai4e_core", "ai4e_spec"}:
        for distribution in package_distributions.get(name, []):
            distributions[distribution] = importlib.metadata.version(distribution)
    identity = {
        "version": 2,
        "target": target,
        "roots": roots,
        "distributions": distributions,
        "dependencies": dependencies,
    }
    return {**identity, "revision": digest(identity)}


def _verify_files(source: dict, recipe: str | Path) -> None:
    """执行前核对固定来源；不以当前任务的另一入口解释历史结果。"""
    if source.get("version") != 2 or "dependencies" not in source:
        raise ValueError("operation_unavailable: application_source_dependencies_missing")
    identity = {key: value for key, value in source.items() if key != "revision"}
    if digest(identity) != source.get("revision"):
        raise ValueError("application_source_record_changed")
    for item in source["roots"]:
        root = Path(recipe) if item["local"] else Path(item["root"])
        if not root.is_dir() or any(
            not (root / name).is_file()
            or hashlib.sha256((root / name).read_bytes()).hexdigest() != revision
            for name, revision in item["files"].items()
        ):
            raise ValueError("application_source_changed")
    for name, version in source["distributions"].items():
        if importlib.metadata.version(name) != version:
            raise ValueError("application_distribution_changed")
    for item in list(source["dependencies"]["resources"].values()) + [
        module["file"]
        for module in source["dependencies"]["modules"].values()
        if module and module["file"]
    ]:
        path = Path(recipe) / item["path"] if item["local"] else Path(item["path"])
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]:
            raise ValueError("application_source_changed")


def verify_source(source: dict, recipe: str | Path) -> None:
    """核验固定内容及当前导入解析；管理进程不加载应用模块。"""
    _verify_files(source, recipe)
    _process(Path(recipe).resolve(), {"verify": source})


def same_source(expected: dict, actual: dict) -> bool:
    """比较应用依赖身份，允许新增不参与应用解析的能力文件。"""
    if any(
        expected.get(key) != actual.get(key)
        for key in ("version", "target", "distributions", "dependencies")
    ):
        return False
    for root in expected["roots"]:
        matching = next(
            (
                r
                for r in actual["roots"]
                if (r["local"], r.get("root")) == (root["local"], root.get("root"))
            ),
            None,
        )
        if matching is None or any(matching["files"].get(k) != v for k, v in root["files"].items()):
            return False
    return True


def _process(recipe: Path, request: dict):
    import os

    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    # -m 会将 cwd 加入搜索路径，复制的用户 application 由该目录解析。
    result = subprocess.run(
        [sys.executable, "-m", "ai4e_task.tasks.operation_sources"],
        input=json.dumps(request, allow_nan=False),
        cwd=recipe,
        capture_output=True,
        text=True,
        env=env,
        timeout=300,
        check=False,
    )
    if result.returncode:
        from .inspections import inspection_failure_message

        raise ValueError(inspection_failure_message(result.stderr))
    return json.loads(result.stdout)


def capture_source(recipe: str | Path, name: str) -> dict:
    """捕获显式可选入口及其源码身份，返回可随运行持久化的记录。"""
    from .operations import operation_target

    recipe = Path(recipe).resolve()
    return _process(recipe, {"capture": operation_target(recipe, name)})


def configuration_context(config: dict, config_dir: str | Path, *, name="inspect") -> dict:
    """未属于任务的显式配置上下文；必须声明应用及配置来源目录。"""
    from .operations import _qualified

    module = config.get("components", {}).get("application")
    if not isinstance(module, str) or not module.strip():
        raise ValueError("operation_unavailable: application_not_declared")
    if name not in {"inspect", "infer", "evaluate", "export"}:
        raise ValueError("operation_unavailable: " + name)
    recipe = Path(config_dir).resolve()
    source = _process(recipe, {"capture": _qualified(module + "." + name, name)})
    return {"source": source, "recipe": str(recipe)}


def invoke_source(source: dict, recipe: str | Path, request: dict):
    """核对并调用固定来源；运行只交接引用，摘要由应用从 run_dir 读取。"""
    if isinstance(request.get("run"), dict):
        # get_run 附带的科学产物可能含未评价的非有限占位值；不跨管理边界
        # 复制或改写这些内容。应用按固定运行目录读取原始 summary/lineage。
        request = {
            **request,
            "run": {
                key: value
                for key, value in request["run"].items()
                if key not in {"summary", "lineage"}
            },
        }
    return _process(Path(recipe).resolve(), {"source": source, "request": request})


def with_operation(source: dict, name: str) -> dict:
    """同一已固定应用切换可选操作，不切换模块或重捕获当前源码。"""
    if name not in {"inspect", "infer", "evaluate", "export"}:
        raise ValueError("operation_unavailable: " + name)
    result = {key: value for key, value in source.items() if key != "revision"}
    result["target"] = result["target"].rsplit(".", 1)[0] + "." + name
    return {**result, "revision": digest(result)}


def load_verified_operation(source: dict, recipe: str | Path):
    """仅在隔离执行进程加载；核对文件、发行版本和实际模块解析位置。"""
    from .operations import load_operation

    _verify_files(source, recipe)
    dependencies = collect_dependencies(source["target"], Path(recipe))
    if dependencies != source["dependencies"]:
        raise ValueError("application_source_resolution_changed")
    operation = load_operation(source["target"])
    actual = _source(source["target"], Path(recipe))
    if not same_source(source, actual):
        raise ValueError("application_source_resolution_changed")
    return operation


def operation_context(project, task_id, *, name="infer", run=None, batch_id=None) -> dict:
    """解析明确当前任务或固定运行/批次；历史缺来源时不回填当前入口。"""
    from ..storage.files import read_json
    from ..storage.layout import task_dir

    folder = task_dir(project, task_id)
    if run is not None:
        if run["task_id"] != task_id:
            raise ValueError("operation_task_mismatch")
        source = run.get("task_description", {}).get("source")
        if not source or not run.get("code_path"):
            raise ValueError("operation_unavailable: captured_application_source_missing")
        recipe = Path(project) / run["code_path"]
    elif batch_id is not None:
        batch = folder / ".dojo/inference_batches" / batch_id
        from ..storage.layout import inside

        batch = inside(folder / ".dojo/inference_batches", batch_id)
        source = read_json(batch / "request.json").get("application_source")
        recipe = batch / "code"
        if not source:
            raise ValueError("operation_unavailable: captured_application_source_missing")
    else:
        recipe = folder / "recipe"
        source = capture_source(recipe, name)
    return {"source": with_operation(source, name), "recipe": str(recipe)}


def main():
    """内部子进程入口：捕获、核验及计算日志与 JSON 结果隔离。"""
    request = json.load(sys.stdin)
    with contextlib.redirect_stdout(sys.stderr):
        if "capture" in request:
            result = _source(request["capture"], Path.cwd())
        elif "verify" in request:
            source = request["verify"]
            _verify_files(source, Path.cwd())
            if collect_dependencies(source["target"], Path.cwd()) != source["dependencies"]:
                raise ValueError("application_source_resolution_changed")
            result = None
        else:
            operation = load_verified_operation(request["source"], Path.cwd())
            result = operation(request["request"])
            _verify_files(request["source"], Path.cwd())
            if (
                collect_dependencies(request["source"]["target"], Path.cwd())
                != request["source"]["dependencies"]
            ):
                raise ValueError("application_source_resolution_changed")
    print(json.dumps(result, ensure_ascii=False, allow_nan=False))


if __name__ == "__main__":
    main()
