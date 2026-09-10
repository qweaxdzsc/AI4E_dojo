"""F：新增目录与100项验收映射有真实导航，示例保持共享脚本。"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_all_items_have_real_implementation_paths():
    """一百项叶子都有路径与明确状态，未完成项保留 pending。"""
    rows = json.loads((ROOT / ".context/mvp/transolver3-results/coverage.json").read_text())
    assert len(rows) == 100 and {r["id"] for r in rows} == set(range(1, 101))
    for row in rows:
        assert row["leaf"] and row["status"]
        assert (ROOT / row["dojo"]).is_file()
        for evidence in row["evidence"]:
            assert (ROOT / evidence).is_file()
    assert (ROOT / ".context/mvp/transolver3-acceptance.md").is_file()


def test_examples_share_all_stage_scripts():
    """复制案例只在配置和说明上不同，阶段脚本保持同一实现。"""
    for example in ("shapenet_car_abupt", "nasa_crm_transolver3"):
        for script in (
            "configuration.py",
            "rawprep.py",
            "trainprep.py",
            "train.py",
            "post.py",
            "pipeline.py",
        ):
            assert (ROOT / "recipes/aero_cfd" / script).read_bytes() == (
                ROOT / "examples/aero_cfd" / example / script
            ).read_bytes()


def test_module_navigation_and_no_reference_runtime_dependency():
    """模块索引登记职责；正式包没有参考仓库的运行导入。"""
    for module in ("ai4e-core", "ai4e-contrib", "ai4e-spec", "recipes"):
        assert (
            "transolver3-acceptance.md" in (ROOT / ".context/modules" / f"{module}.md").read_text()
        )
    for path in (ROOT / "packages").rglob("*.py"):
        text = path.read_text()
        assert "from user_project" not in text and "import user_project" not in text
