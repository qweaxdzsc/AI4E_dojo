"""能力直达导航、实际小例子、离线资源及查询可达性验收。"""

import json
import re
import subprocess
import sys
import sysconfig
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
HELP = ROOT / "docs/agent-help"
PAGES = sorted((HELP / "capabilities").glob("*.md"))


def metadata(path):
    """读取教程声明，不通过标题猜测 API。"""
    return json.loads(path.read_text().splitlines()[0][len("<!-- dojo-help: "):-len(" -->")])


def test_menu_links_and_symbols_are_reachable():
    from tools.docs.build_agent_help import navigation_outputs

    symbols = {json.loads(line)["symbol"] for line in
               (HELP / "indexes/symbols.jsonl").read_text().splitlines()}
    topics = {row["topic_id"] for row in json.loads((HELP / "indexes/topics.json").read_text())}
    assert len(PAGES) == 9
    for page in PAGES:
        meta = metadata(page)
        assert meta["topic_id"] in topics
        assert set(meta["symbols"]) <= symbols
        for href in re.findall(r"\]\(([^)]+)\)", page.read_text()):
            assert (page.parent / href).resolve().is_file(), href
    for name, expected in navigation_outputs().items():
        target = ROOT / name
        assert target.read_text() == expected
        for href in re.findall(r"\]\(([^)]+capabilities/[^)]+)\)", expected):
            assert (target.parent / href).resolve().is_file(), href


@pytest.mark.parametrize("page", PAGES, ids=lambda page: page.stem)
def test_documented_examples_execute(page, tmp_path):
    """执行文档正文，包含真实反传、恢复、预测、数值复算和图片读回。"""
    snippets = re.findall(r"```python\n(.*?)```", page.read_text(), re.DOTALL)
    assert len(snippets) == 1
    source = tmp_path / "source"
    source.mkdir()
    script = source / "demo.py"
    script.write_text(snippets[0])
    result = subprocess.run(
        ["uv", "run", "--no-sync", "--project", str(ROOT), "python", str(script)],
        cwd=tmp_path, capture_output=True, text=True, timeout=90, check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    if page.stem == "training":
        summaries = list((tmp_path / "records").rglob("summary.json"))
        assert len(summaries) == 1
        report = json.loads(summaries[0].read_text())["reports"]["train"]
        assert report["updates"] == 4
        assert Path(report["checkpoint"]).is_file()


def test_capability_search_and_offline_export(tmp_path, monkeypatch):
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "capability_resources", ROOT / "packages/ai4e-task/templates/resources.py"
    )
    resources = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(resources)

    # 当前服务安装可与源码不同；这里明确检验本轮文档资源，wheel 另验。
    monkeypatch.setattr(resources, "resource_root", lambda: ROOT)
    for query, topic in [
        ("已有 PyTorch 模型和 DataLoader 如何复用训练循环", "capability:training"),
        ("NumPy 预测计算相对 L2", "capability:evaluation"),
        ("归一化", "capability:data"),
    ]:
        assert topic in {hit["topic_id"] for hit in resources.search_help(query, limit=5)}
    symbol = "ai4e_core.applications.base.iteration_training.train_model"
    assert resources.search_help(symbol, limit=1)[0]["topic_id"] == "api:" + symbol
    exported = resources.export_guide(tmp_path / "offline")
    for page in PAGES:
        assert (Path(exported["help_root"]) / "capabilities" / page.name).read_bytes() == page.read_bytes()
    assert not (tmp_path / "offline/AGENTS.md").exists()


def test_capabilities_in_real_wheel_outside_checkout(tmp_path):
    """独立安装本轮 Task wheel，不重装用户正在使用的正式环境。"""
    wheels = tmp_path / "wheels"
    subprocess.run(
        ["uv", "build", "--package", "ai4e-task", "--wheel", "--out-dir", str(wheels)],
        cwd=ROOT, check=True, capture_output=True, text=True,
    )
    env = tmp_path / "environment"
    subprocess.run(["uv", "venv", "--python", sys.executable, str(env)], check=True,
                   capture_output=True)
    python = env / "bin/python"
    subprocess.run(["uv", "pip", "install", "--python", str(python), "--no-deps",
                    str(next(wheels.glob("ai4e_task-*.whl")))], check=True, capture_output=True)
    site = env / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "site-packages"
    (site / "third-party.pth").write_text(sysconfig.get_path("purelib") + "\n")
    script = '''import json, re
from pathlib import Path
import ai4e_task as task
assert Path(task.__file__).is_relative_to(Path("environment").resolve())
info = task.export_guide("offline")
root = Path("offline").resolve()
pages = list((root / "docs/agent-help/capabilities").glob("*.md"))
assert len(pages) == 9
for key in ("guide", "skill", "entry"):
    page = Path(info[key])
    links = re.findall(r"\\]\\(([^)]+)\\)", page.read_text())
    for link in links:
        assert (page.parent / link).resolve().is_file(), link
for query, topic in [("归一化", "capability:data"),
                     ("NumPy 预测计算相对 L2", "capability:evaluation"),
                     ("已有 PyTorch 模型和 DataLoader 如何复用训练循环", "capability:training")]:
    assert topic in {h["topic_id"] for h in task.search_help(query, limit=5)}
assert "train_model" in task.read_help_topic("capability:training")["content"]
print(json.dumps({"installed": task.__file__, "capabilities": len(pages), "exported": info}))
'''
    result = subprocess.run(
        ["uv", "run", "--no-project", "--no-sync", "--python", str(python), "python", "-c", script],
        cwd=tmp_path, capture_output=True, text=True, timeout=60, check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
