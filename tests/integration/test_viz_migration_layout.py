"""完整迁入清单及独立应用边界验证，不把目录存在当作功能验收。"""
import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VIZ = ROOT/'packages/ai4e-viz'


def test_complete_source_inventory():
    manifest = json.loads((VIZ/'docs/migration/source-manifest.json').read_text())
    assert manifest['tracked_count'] == 385
    assert manifest['extra_count'] == 8
    entries = manifest.get('files', manifest.get('entries', []))
    assert len(entries) == 393
    for item in entries:
        assert (VIZ/item['source_path']).is_file(), item
    assert not (VIZ/'.git').exists()
    assert not (VIZ/'.cursor/mcp.json').exists()
    for name in ('inspect','preview','pipeline','serialization','render','compose','runtime'):
        assert (VIZ/name/'__init__.py').exists()


def test_new_application_never_imports_research_packages():
    for path in (VIZ/'backend').rglob('*.py'):
        if 'tests' in path.parts: continue
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                roots = [a.name.split('.')[0] for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                roots = [(node.module or '').split('.')[0]]
            else: continue
            assert not set(roots) & {'ai4e_task','ai4e_core','ai4e_contrib','ai4e_server'}, path


def test_scoped_rules_and_active_architecture():
    for name in ('context','backend','frontend'):
        rule = (ROOT/f'.cursor/rules/ai4e-vis-{name}.mdc').read_text()
        assert 'packages/ai4e-viz/' in rule and 'alwaysApply: false' in rule
    assert '轻量 DDD' in (VIZ/'docs/architecture/architecture.md').read_text()
    assert '任务' in (VIZ/'AGENTS.md').read_text()
