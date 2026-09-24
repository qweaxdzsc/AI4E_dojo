"""真实调用计数必须去重、排除未调用工具，并区分分支覆盖和实现体积。"""

import importlib.util

from tools.verification.dojo_validity.rmhd.recipe_probe.implementation_coverage import (
    ImplementationCoverage,
    code_lines,
)


def test_called_implementation_excludes_unused_and_deduplicates(tmp_path):
    source = '''"""模块说明。"""
def used(flag):
    """函数说明。"""
    if flag:
        return 1
    return 2

def unused():
    return 999
'''
    path = tmp_path / "library.py"
    path.write_text(source)
    spec = importlib.util.spec_from_file_location("fixture_library", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    collector = ImplementationCoverage({"fixture": tmp_path})
    declarations = tmp_path / "declarations.py"
    declarations.write_text(
        "class UnusedType:\n    field = 1\n    def unrelated(self):\n        return 999\n"
    )
    collector.start()
    try:
        assert module.used(True) == 1
        assert module.used(True) == 1
        lazy_spec = importlib.util.spec_from_file_location("unused_declarations", declarations)
        lazy_spec.loader.exec_module(importlib.util.module_from_spec(lazy_spec))
    finally:
        collector.stop()
    report = collector.save(tmp_path / "report.json")
    row = report["files"][0]
    assert len(report["files"]) == 1
    assert row["function_lines"] == [2, 4, 5, 6]
    assert row["executed_lines"] == [4, 5]
    assert row["functions"] == [{"name": "used", "start": 2, "end": 6}]
    assert 8 not in row["function_lines"] and 9 not in row["function_lines"]


def test_sloc_keeps_code_ignores_docs_comments_and_blank_lines():
    assert code_lines('"""doc\ntext"""\n# comment\nx = (\n 1\n)\n') == {4, 5, 6}
