"""案例说明发现、旧清单兼容、物化双层正文和离线帮助读回。"""

import hashlib
import json
from pathlib import Path

import pytest
from ai4e_task.templates import resources


def test_maintained_catalog_explains_every_case():
    for case in resources.list_examples():
        description = case["research"]
        assert all(
            description[k]
            for k in ("summary", "data_form", "training_pattern", "extension_points", "limitations")
        )
        source = resources.resource_root() / "examples" / case["path"] / "README.md"
        content = source.read_text()
        assert "改写" in content
        assert len(description["summary"]) > 12


def test_query_tags_intersection_and_original_order():
    all_cases = resources.list_examples()
    filtered = resources.list_examples(data_form="regular_grid", training_pattern="iteration")
    assert filtered and filtered == [
        c
        for c in all_cases
        if "regular_grid" in c["research"]["data_form"]
        and "iteration" in c["research"]["training_pattern"]
    ]
    assert any(c["id"] == "wdno.burgers_base" for c in resources.list_examples(query="BURGERS"))
    assert resources.list_examples(query="  ") == all_cases
    assert resources.list_examples(query="impossible-zzzz") == []
    assert resources.list_examples(data_form="unknown-shape") == []
    with pytest.raises(TypeError):
        resources.list_examples(query=[])


def test_old_manifest_does_not_invent_tags(monkeypatch):
    old = {"id": "old", "type": "standalone", "purpose": "old purpose"}
    monkeypatch.setattr(resources, "read_case_manifest", lambda: {"cases": [old]})
    assert resources.list_examples(query="PURPOSE") == [old]
    assert resources.list_examples(data_form="regular_grid") == []
    assert resources.list_examples() == [old]


@pytest.mark.parametrize(
    "case_id", ["recipe_extensions.wdno", "extension.pcno", "geotransolver.darcy"]
)
def test_copy_preserves_originals_and_delivers_readmes(tmp_path, case_id):
    cases = {c["id"]: c for c in resources.list_examples()}
    case = cases[case_id]
    target = tmp_path / "copy"
    receipt = resources.copy_example(case_id, target)
    docs = receipt["documentation"]
    assert (target / docs["entry"]).is_file()
    assert json.loads((target / ".dojo-provenance.json").read_text())["documentation"] == docs
    if case["type"] == "extension":
        source_cases = {"base": cases[case["base_case"]], "extension": case}
        root_readme_case = (
            case if "README.md" in case["override_files"] else cases[case["base_case"]]
        )
    else:
        source_cases = {"case": case}
        root_readme_case = case
    expected = resources.resource_root() / "examples" / root_readme_case["path"] / "README.md"
    assert (target / "README.md").read_bytes() == expected.read_bytes()
    for role, source_case in source_cases.items():
        original = resources.resource_root() / "examples" / source_case["path"] / "README.md"
        entry = docs["sources"][role]
        assert entry["source_sha256"] == hashlib.sha256(original.read_bytes()).hexdigest()
        assert entry["sha256"] == hashlib.sha256((target / entry["path"]).read_bytes()).hexdigest()
        assert "改写" in (target / entry["path"]).read_text()


def test_reserved_document_directory_is_preflighted(tmp_path, monkeypatch):
    source = tmp_path / "source"
    source.mkdir()
    (source / ".dojo-docs").mkdir()
    monkeypatch.setattr(resources, "_case_path", lambda c: source)
    target = tmp_path / "destination"
    with pytest.raises(ValueError, match="保留目录"):
        resources.copy_example("wdno.burgers_base", target)
    assert not target.exists()


def test_copied_document_link_targets_and_missing_reference(tmp_path):
    from ai4e_task.templates.example_docs import write_example_documents

    source, target = tmp_path / "source", tmp_path / "target"
    source.mkdir()
    target.mkdir()
    (source / "README.md").write_text(
        "[train](train.py) [outside](../../private.txt) [web](https://example.com)"
    )
    (target / "train.py").write_text("pass")
    result = write_example_documents(target, {"case": source})
    content = (target / result["sources"]["case"]["path"]).read_text()
    assert "(<../train.py>)" in content
    assert "未随此说明交付" in content
    assert "[outside]" not in content
    assert "[web](https://example.com)" in content


def test_exported_help_contains_real_case_body(tmp_path):
    result = resources.export_help(tmp_path)
    entry = resources.read_help_topic("case:recipe_extensions.wdno")
    assert "案例详细说明" in entry["content"]
    assert "能量审计" in entry["content"]
    assert "SHA256" in entry["content"]
    exported = Path(result["root"] if "root" in result else result["help_root"])
    content = (exported / "examples/cases/recipe_extensions/wdno.md").read_text()
    assert "案例详细说明" in content and "基案例完整说明" in content
