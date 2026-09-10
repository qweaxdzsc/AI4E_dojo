"""正式组件的可安装资源、来源和依赖方向门禁。"""

import ast
from importlib import metadata, resources
from pathlib import Path

import torch

from ai4e_contrib.ability.model.abupt.model import SOURCE, construct

ROOT = Path(__file__).resolve().parents[2]


def test_installed_component_resources_and_real_model():
    package = resources.files("ai4e_contrib.ability.model.abupt")
    assert "2211068" in package.joinpath("README.md").read_text()
    assert package.joinpath("LICENSE").read_text().strip()
    assert SOURCE.startswith("abupt-domain-v2:noether-313e6c5")
    assert metadata.version("torch-geometric") == "2.6.1"
    model = construct(
        dim=24,
        geometry_depth=1,
        num_heads=3,
        blocks="psc",
        data_specs={
            "position_dim": 3,
            "domains": {
                "surface": {"output_dims": {"pressure": 1}},
                "volume": {"output_dims": {"velocity": 3}},
            },
        },
        num_domain_decoder_blocks={"surface": 1, "volume": 1},
    )
    assert isinstance(model, torch.nn.Module)
    assert type(model).__module__ == "ai4e_contrib.ability.model.abupt.network"


def test_core_spec_dependency_direction_and_no_old_paths():
    for package, forbidden in [
        ("ai4e-core", ("ai4e_contrib", "noether")),
        ("ai4e-spec", ("ai4e_core", "ai4e_contrib", "torch", "numpy", "noether")),
    ]:
        for path in (ROOT / "packages" / package).rglob("*.py"):
            tree = ast.parse(path.read_text())
            for node in ast.walk(tree):
                modules = (
                    [a.name for a in node.names]
                    if isinstance(node, ast.Import)
                    else [node.module or ""]
                    if isinstance(node, ast.ImportFrom)
                    else []
                )
                assert all(
                    not any(m == f or m.startswith(f + ".") for f in forbidden) for m in modules
                ), path
    assert not (ROOT / "packages/ai4e-core/applications/aero_cfd/pre").exists()
    assert not (ROOT / "packages/ai4e-core/applications/aero_cfd/train/standard.py").exists()


def test_acceptance_document_covers_all_plan_leaves():
    import re

    record = (ROOT / ".context/mvp/abupt-acceptance.md").read_text()
    expected = {
        f"{letter}{n}"
        for letter, count in zip("ABCDEFGHI", [3, 3, 5, 4, 4, 4, 4, 3, 4], strict=True)
        for n in range(1, count + 1)
    }
    assert set(re.findall(r"^- \*\*([A-I][1-5])\*\*", record, re.MULTILINE)) == expected
    for node in re.findall(r"`(tests/[^`]+::test_[^`]+)`", record):
        file, function = node.split("::", 1)
        assert (ROOT / file).is_file()
        assert f"def {function.split('[')[0]}(" in (ROOT / file).read_text()
    for file in [
        "AGENTS.md",
        ".context/index.md",
        ".context/modules/ai4e-core.md",
        "docs/PRD/ai4e-core/applications/PRD.md",
    ]:
        text = (ROOT / file).read_text()
        for directory in ["rawprep", "trainprep", "model", "train", "post"]:
            assert directory in text
        assert "配置构建与训练对象仍为占位" not in text


def test_multidomain_acceptance_nodes_exist():
    import re

    record = (ROOT / ".context/mvp/abupt-multidomain-acceptance.md").read_text()
    expected = {
        f"{letter}{i}"
        for letter, count in zip("ABCDEF", [3, 4, 3, 4, 3, 3], strict=True)
        for i in range(1, count + 1)
    }
    assert set(re.findall(r"^- \*\*([A-F][1-4])\*\*", record, re.MULTILINE)) == expected
    for node in re.findall(r"`(tests/[^`]+::test_[^`]+)`", record):
        file, function = node.split("::", 1)
        assert f"def {function}(" in (ROOT / file).read_text()
