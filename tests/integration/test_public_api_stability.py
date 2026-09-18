"""固定外部用户代码只更新框架安装包，验证自由连接和公开入口。"""

import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
BASELINE = ROOT / "tests/fixtures/public_api_baseline"


def test_fixed_user_code_against_installed_framework(tmp_path):
    """固定用户文件原文，在实际 wheel 中运行，自定义对象不被框架转换。"""
    wheels = tmp_path / "wheels"
    for package in ("ai4e-spec", "ai4e-core"):
        subprocess.run(
            ["uv", "build", "--package", package, "--wheel", "--out-dir", str(wheels)],
            cwd=ROOT,
            check=True,
            capture_output=True,
        )
    installed = tmp_path / "installed"
    subprocess.run(
        [
            "uv",
            "pip",
            "install",
            "--no-deps",
            "--target",
            str(installed),
            *map(str, wheels.glob("*.whl")),
        ],
        check=True,
        capture_output=True,
    )
    copied = tmp_path / "user"
    shutil.copytree(BASELINE, copied)
    expected = json.loads((copied / "sha256.json").read_text())
    env = {**os.environ, "PYTHONPATH": str(installed), "PYTHONDONTWRITEBYTECODE": "1"}
    probe = subprocess.run(
        [sys.executable, "-B", "-c", "import ai4e_core; print(ai4e_core.__file__)"],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    assert Path(probe.stdout.strip()).is_relative_to(installed)
    result = subprocess.run(
        [sys.executable, "-B", str(copied / "pipeline.py"), "--set", "radius=1"],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        timeout=90,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads((tmp_path / "data/features.json").read_text()) == [5, 2]
    assert {
        name: hashlib.sha256((copied / name).read_bytes()).hexdigest() for name in expected
    } == expected
    summary = json.loads(next((tmp_path / "runs").glob("*/summary.json")).read_text())
    assert summary["reports"]["features"]["count"] == 2


def test_local_adapter_and_failure_context(tmp_path):
    """不匹配由局部连接解决；框架原样交接对象，不承诺自动转换。"""
    from ai4e_core import run

    class Payload:
        def __init__(self):
            self.values = (3, 4)

    original = Payload()
    observed = []

    def pipeline(cfg):
        value = run.stage("read", lambda: original)
        assert value is original
        with pytest.raises(TypeError):
            run.stage("unmatched", sum, value)
        observed.append(run.stage("adapted", sum, value.values))

    assert (
        run.run_recipe(
            {"run_root": str(tmp_path / "runs"), "pipeline": {"stages": ["custom"]}},
            stages=pipeline,
            script=str(tmp_path / "user/pipeline.py"),
        )
        == 0
    )
    assert observed == [7]


def test_configuration_adapter_is_explicit_and_scoped():
    """通用加载器完整接收自定义参数；局部兼容适配不会泄漏到下一次调用。"""
    from ai4e_core import run

    calls = []
    original = {"rawprep": {"workers": "a user-defined value"}}

    def loader(path, overrides):
        calls.append((path, overrides))
        return original

    def adapter(load, path, overrides):
        return {"adapted": load(path, overrides)}

    assert run.load_user_configuration(loader, "not-a-yaml-file", {"x": 1}) is original
    with run.configuration_adapter(adapter):
        assert run.load_user_configuration(loader, "custom", None) == {"adapted": original}
    assert run.load_user_configuration(loader, "after", None) is original
    assert calls == [("not-a-yaml-file", {"x": 1}), ("custom", None), ("after", None)]


def test_progress_publishes_one_snapshot_without_double_copy(tmp_path):
    """两千样本的进度只由会话做一次隔离复制，保持已发布快照不可变。"""
    from ai4e_core import run
    from ai4e_core.applications.aero_cfd.post.progress import PostProgress

    copies = []

    class Ledger(dict):
        def __deepcopy__(self, memo):
            from copy import deepcopy

            copies.append(1)
            return deepcopy(dict(self), memo)

    def pipeline(cfg):
        progress = PostProgress(run.TrainingRun(), {"prediction": True})
        progress.report = Ledger(progress.report)
        progress.report["samples"] = list(range(2000))
        progress.publish()
        progress.report["samples"].clear()

    assert (
        run.run_recipe(
            {"run_root": str(tmp_path / "runs"), "pipeline": {"stages": ["custom"]}},
            stages=pipeline,
            script=tmp_path / "user/pipeline.py",
        )
        == 0
    )
    summary = json.loads(next((tmp_path / "runs").glob("*/summary.json")).read_text())
    assert summary["reports"]["post"]["samples"] == list(range(2000))
    assert len(copies) == 1


def test_current_templates_use_public_session_facade():
    """新版模板不导入会话实现模块；历史用户基线维持原文。"""
    for directory in (ROOT / "recipes", ROOT / "examples"):
        for source in directory.rglob("*.py"):
            text = source.read_text()
            assert "from ai4e_core.run.training import" not in text, source
            assert "from ai4e_core.run.session import" not in text, source
