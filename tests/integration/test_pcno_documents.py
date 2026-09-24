"""来源许可与可复制PCNO帮助资源的真实关联。"""

import json
import tomllib
from pathlib import Path

from ai4e_task import check_example, read_help_topic

ROOT = Path(__file__).resolve().parents[2]


def test_source_license_and_help_entry():
    metadata = json.loads(
        (ROOT / "packages/ai4e-contrib/ability/model/pcno/source.json").read_text()
    )
    assert metadata["license"] == "GPL-3.0"
    assert (ROOT / "packages/ai4e-core/abilities/PCNO_LICENSE").read_bytes() == (
        ROOT / "packages/ai4e-contrib/ability/model/pcno/LICENSE"
    ).read_bytes()
    assert all((ROOT / item["file"]).is_file() for item in metadata["modules"])
    assert check_example("geothermal.pcno")["ok"]
    assert read_help_topic("case:geothermal.pcno")["title"]


def test_default_development_group_selects_pcno_dependencies():
    """默认开发环境必须兑现 PCNO 已声明的物性依赖，不能只在专用安装中可用。"""
    workspace = tomllib.loads((ROOT / "pyproject.toml").read_text())
    dev = workspace["dependency-groups"]["dev"]
    contrib = next(item for item in dev if item.startswith("ai4e-contrib["))
    extras = set(contrib.removeprefix("ai4e-contrib[").removesuffix("]").split(","))
    assert "pcno" in extras

    package = tomllib.loads((ROOT / "packages/ai4e-contrib/pyproject.toml").read_text())
    pcno = package["project"]["optional-dependencies"]["pcno"]
    assert "ai4e-core[geothermal]" in pcno
