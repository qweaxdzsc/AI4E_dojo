"""来源许可与可复制PCNO帮助资源的真实关联。"""

import json
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
