"""新增案例范围、来源及依赖边界的集成检查。"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_cases_are_honest_and_sources_match():
    manifest = json.loads((ROOT / "examples/case-manifest.json").read_text())
    assert any(x["id"] == "pcno.double_cylinder" for x in manifest["cases"])
    assert not any(x["id"] == "pcno.cylinder_flow" for x in manifest["cases"])
    assert "未通过" in (ROOT / "examples/pcno/cylinder_flow/README.md").read_text()
    for path in (ROOT / "recipes/pcno_cylinder").glob("*.py"):
        assert (
            path.read_bytes() == (ROOT / "examples/pcno/double_cylinder" / path.name).read_bytes()
        )
    source = (ROOT / "packages/ai4e-core/abilities/modeling/models/fourier_unet3d.py").read_text()
    assert "ai4e_contrib" not in source
    assert (ROOT / "docs/PRD/recipes/pcno_cylinder/PRD.md").exists()
