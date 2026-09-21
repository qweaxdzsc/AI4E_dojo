"""新能力归属、许可及嵌套案例入口的源码门禁。"""

import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_core_has_no_reverse_import_and_bindings_have_no_loops():
    for path in (ROOT / "packages/ai4e-core").rglob("*.py"):
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                assert not (node.module or "").startswith("ai4e_contrib"), path
            elif isinstance(node, ast.Import):
                assert not any(n.name.startswith("ai4e_contrib") for n in node.names), path
    for domain in ("parametric_pde", "spatiotemporal_pde", "aero_cfd"):
        tree = ast.parse(
            (
                ROOT / f"packages/ai4e-contrib/application/{domain}/geotransolver/binding.py"
            ).read_text()
        )
        assert not any(isinstance(n, (ast.For, ast.While)) for n in ast.walk(tree))


def test_licenses_and_case_files():
    assert (ROOT / "packages/ai4e-core/Notice/physicsnemo/LICENSE").is_file()
    assert (ROOT / "packages/ai4e-contrib/ability/model/geotransolver/LICENSE").is_file()
    m = json.loads((ROOT / "examples/case-manifest.json").read_text())
    for case in [x for x in m["cases"] if "geotransolver" in x["id"] and x.get("recipe_source")]:
        assert "/" in case["recipe_source"]
        for name in case["required_files"]:
            assert (ROOT / "examples" / case["path"] / name).read_bytes() == (
                ROOT / "recipes" / case["recipe_source"] / name
            ).read_bytes()


def test_migrated_source_hashes_describe_delivered_files():
    import hashlib

    for name in (
        "packages/ai4e-core/Notice/physicsnemo/source.json",
        "packages/ai4e-contrib/ability/model/geotransolver/source.json",
    ):
        record = json.loads((ROOT / name).read_text())
        for item in record["records"]:
            assert (
                hashlib.sha256((ROOT / item["target"]).read_bytes()).hexdigest()
                == item["target_sha256"]
            )
