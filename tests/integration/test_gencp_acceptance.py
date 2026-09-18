"""六组真实缩小实验报告门禁；缺少计算结果必须明确跳过而非通过。"""

import json
import os
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = Path("/Users/zonghui/work/project_simulation/dojo_train/gencp")


@pytest.mark.parametrize("dataset", ["ntcouple", "double_cylinder", "turek_hron"])
@pytest.mark.parametrize("backbone", ["cno", "sit_fno"])
def test_six_real_comparisons(dataset, backbone):
    if os.environ.get("DOJO_GENCP_ACCEPTANCE") != "1":
        pytest.skip("需显式六组真实结果环境；skip 不算科学验收")
    folder = ARTIFACTS / f"{dataset}_{backbone}"
    report = json.loads((folder / "comparison.json").read_text())
    budget = json.loads((folder / "budget.json").read_text())
    learning = json.loads((folder / "learning.json").read_text())
    assert report["engineering_passed"]
    assert report["paper"]["eligible"] is False
    assert budget["seconds"] < 10800
    assert not any(entry["status"] == "running" for entry in budget["runs"])
    assert set(learning["fields"]) == set(report["fields"])
    assert all(value["updates"] == 1000 for value in report["fields"].values())
    assert all(value["metrics"]["passed"] for value in report["fields"].values())


def test_documents_and_copyable_recipe_entries():
    import importlib.util

    path = ROOT / "recipes/gencp/configuration.py"
    spec = importlib.util.spec_from_file_location("gencp_config_probe", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert callable(module.load_configuration) and callable(module.component)
    for name in ("rawprep", "trainprep", "train", "single", "infer", "post", "pipeline"):
        assert (ROOT / "recipes/gencp" / f"{name}.py").is_file()
    for name in ("ai4e-core", "ai4e-contrib", "recipes", "repository"):
        assert "GenCP" in (ROOT / f".context/modules/{name}.md").read_text()
    assert (ROOT / "docs/PRD/recipes/gencp/PRD.md").is_file()
