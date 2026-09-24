"""应用来源闭环：依赖变化、解析遮蔽、资源、搬移及旧来源。"""

import json
import shutil

import pytest
from ai4e_task.tasks.operation_sources import (
    capture_source,
    invoke_source,
    verify_source,
    with_operation,
)


def provider(tmp_path, monkeypatch, *, dynamic=False):
    """建立真实仓库外依赖与可复制入口，避免只测摘要函数。"""
    import os

    recipe = tmp_path / "recipe"
    external = tmp_path / "external"
    recipe.mkdir()
    external.mkdir()
    (external / "dependency.py").write_text("VALUE = 1\n")
    (recipe / "config.yaml").write_text("components:\n  application: custom\n")
    code = "from dependency import VALUE\ndef inspect(request):\n    return VALUE\n"
    if dynamic:
        code = (
            "import importlib\nSOURCE_DEPENDENCIES = {'modules': ['dependency'], 'files': ['resource.json']}\n"
            "def inspect(request):\n    return importlib.import_module(request['module']).VALUE\n"
        )
        (recipe / "resource.json").write_text('{"factor": 2}')
    (recipe / "custom.py").write_text(code)
    monkeypatch.setenv("PYTHONPATH", str(external) + os.pathsep + os.environ.get("PYTHONPATH", ""))
    return recipe, external, capture_source(recipe, "inspect")


def test_external_dependency_content_is_fixed(tmp_path, monkeypatch):
    recipe, external, source = provider(tmp_path, monkeypatch)
    assert invoke_source(source, recipe, {}) == 1
    (external / "dependency.py").write_text("VALUE = 2\n")
    with pytest.raises(ValueError, match="application_source_changed"):
        verify_source(source, recipe)


def test_same_name_shadows_external_dependency(tmp_path, monkeypatch):
    recipe, _, source = provider(tmp_path, monkeypatch)
    (recipe / "dependency.py").write_text("VALUE = 3\n")
    with pytest.raises(ValueError, match="application_source_resolution_changed"):
        invoke_source(source, recipe, {})


@pytest.mark.parametrize("changed", ["module", "resource"])
def test_declared_dynamic_dependency_is_fixed(tmp_path, monkeypatch, changed):
    recipe, external, source = provider(tmp_path, monkeypatch, dynamic=True)
    assert invoke_source(source, recipe, {"module": "dependency"}) == 1
    path = external / "dependency.py" if changed == "module" else recipe / "resource.json"
    path.write_text("VALUE = 4\n" if changed == "module" else '{"factor": 4}')
    with pytest.raises(ValueError, match="application_source_changed"):
        invoke_source(source, recipe, {"module": "dependency"})


def test_copy_and_unrelated_addition_preserve_source(tmp_path, monkeypatch):
    recipe, _, source = provider(tmp_path, monkeypatch, dynamic=True)
    copied = tmp_path / "copy"
    shutil.copytree(recipe, copied)
    (copied / "unused.py").write_text("VALUE = 10\n")
    assert invoke_source(source, copied, {"module": "dependency"}) == 1
    switched = with_operation(source, "infer")
    assert switched["dependencies"] == source["dependencies"]
    assert switched["version"] == source["version"] == 2


def test_old_source_is_unavailable_without_rewriting(tmp_path, monkeypatch):
    recipe, _, source = provider(tmp_path, monkeypatch)
    source.pop("dependencies")
    source.pop("version")
    before = json.dumps(source)
    with pytest.raises(ValueError, match="application_source_dependencies_missing"):
        verify_source(source, recipe)
    assert json.dumps(source) == before
