"""复制已安装公开依赖并构建独立 wheel；不 sync 或修改主环境。"""

import shutil
import subprocess
import sys
import sysconfig
import venv
from importlib import metadata
from pathlib import Path

from packaging.requirements import Requirement
from packaging.utils import canonicalize_name

from .io import digest, read_json, write_json
from .prepare import REPO


def dependency_closure(names):
    """按当前解释器分发元数据确定实际依赖闭包，拒绝不满足的已安装版本。"""
    found, pending = {}, list(names)
    while pending:
        requirement = Requirement(pending.pop())
        name = canonicalize_name(requirement.name)
        if name in found:
            if not requirement.specifier.contains(found[name].version, prereleases=True):
                raise ValueError(f"依赖版本冲突: {requirement}")
            continue
        distribution = metadata.distribution(requirement.name)
        if not requirement.specifier.contains(distribution.version, prereleases=True):
            raise ValueError(f"当前环境不满足: {requirement}")
        found[name] = distribution
        pending.extend(
            r
            for r in distribution.requires or []
            if not Requirement(r).marker or Requirement(r).marker.evaluate({"extra": ""})
        )
    return found


def install_environment(experiment, *, dojo=False):
    """生成不共享 site-packages 的本组环境；解释器系统库作为只读工具前提记录。"""
    experiment = Path(experiment)
    target = experiment / "environment"
    protocol_path = experiment / "protocol.json"
    if any(target.iterdir()) and read_json(protocol_path).get("environment_ready"):
        raise FileExistsError("已经验收的环境不能覆盖")
    venv.EnvBuilder(with_pip=False, symlinks=False).create(target)
    python = target / "bin/python"
    purelib = (
        target
        / "lib"
        / f"python{sys.version_info.major}.{sys.version_info.minor}"
        / "site-packages"
    )
    # 两组具有相同公共科学依赖；仅 Dojo 组另安装四个本地 wheel。
    dependencies = ["torch", "numpy", "PyYAML", "scipy", "omegaconf", "packaging"]
    if dojo:
        for package in ("spec", "core", "contrib", "task"):
            import tomllib

            project = tomllib.loads((REPO / f"packages/ai4e-{package}/pyproject.toml").read_text())
            dependencies.extend(
                r
                for r in project["project"]["dependencies"]
                if not Requirement(r).name.startswith("ai4e-")
            )
    installed = {}
    for name, distribution in dependency_closure(dependencies).items():
        files = []
        for relative in distribution.files or []:
            path = Path(relative)
            if path.is_absolute() or ".." in path.parts or "__pycache__" in path.parts:
                continue
            if name == "setuptools" and path.name == "distutils-precedence.pth":
                # 此注入仅替换 distutils 查找；实验直接使用本组标准库和公开包，不复制启动钩子。
                continue
            if path.suffix == ".pth":
                raise ValueError(f"拒绝复制隐式外部导入配置: {name}/{path}")
            source = Path(distribution.locate_file(relative))
            if not source.is_file():
                continue
            destination = purelib / path
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, destination)
            files.append({"path": str(path), "sha256": digest(destination)})
        installed[name] = {"version": distribution.version, "files": files}
    if dojo:
        wheelhouse = experiment / "dojo-resources/wheels"
        wheelhouse.mkdir()
        for package in ("spec", "core", "contrib", "task"):
            subprocess.run(
                [
                    "uv",
                    "build",
                    "--wheel",
                    "--no-sources",
                    "--out-dir",
                    str(wheelhouse),
                    "--cache-dir",
                    str(experiment / "cache/uv"),
                    str(REPO / f"packages/ai4e-{package}"),
                ],
                check=True,
            )
        subprocess.run(
            [
                "uv",
                "pip",
                "install",
                "--python",
                str(python),
                "--no-deps",
                "--link-mode",
                "copy",
                "--cache-dir",
                str(experiment / "cache/uv"),
                *map(str, sorted(wheelhouse.glob("*.whl"))),
            ],
            check=True,
        )
        # 为帮助中的 packages/... 源码引用提供同版本组内快照，而非开发仓库链接。
        for package in ("spec", "core", "contrib", "task"):
            shutil.copytree(
                REPO / f"packages/ai4e-{package}",
                experiment / f"dojo-resources/packages/ai4e-{package}",
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "dist"),
            )
    code = "import json,sys,torch,numpy; print(json.dumps({'prefix':sys.prefix,'torch':torch.__version__,'numpy':numpy.__version__}))"
    if dojo:
        code += "; import ai4e_task as t; print(json.dumps(t.help_info(),default=str))"
    result = subprocess.run(
        ["uv", "run", "--no-project", "--no-sync", "--python", str(python), "python", "-c", code],
        cwd=experiment,
        capture_output=True,
        text=True,
        check=True,
    )
    write_json(
        experiment / "evidence/environment.json",
        {
            "python": str(python),
            "base_runtime_readonly": sys.base_prefix,
            "stdlib_readonly": sysconfig.get_path("stdlib"),
            "packages": installed,
            "probe_stdout": result.stdout,
            "isolation_verified": False,
        },
    )
    protocol = read_json(protocol_path)
    protocol["environment_ready"] = True
    protocol["runtime_readonly_roots"] = [sys.base_prefix]
    write_json(protocol_path, protocol)
    return target
