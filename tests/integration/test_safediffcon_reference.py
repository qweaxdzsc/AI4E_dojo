"""参考执行门禁：准入后数据或源码变化时不能启动昂贵的完整预训练。"""

import hashlib
import json

import pytest

from tools.verification.safediffcon.reference import verify_pretrain_inputs, verify_source


def fixture_inputs(root):
    source, data = root / "source", root / "data"
    source.mkdir()
    data.mkdir()
    (source / "reference.py").write_text("frozen reference")
    files = {"reference.py": hashlib.sha256(b"frozen reference").hexdigest()}
    manifest = {"files": files, "commit": "test", "patch_sha256": "test"}
    (source / "source.json").write_text(json.dumps(manifest))
    splits = {}
    for name, count in (("train", 39000), ("cal", 1000), ("test", 50)):
        path = data / f"burgers_{name}.h5"
        path.write_bytes(name.encode())
        splits[name] = {
            "source": str(path),
            "samples": count,
            "sha256": hashlib.sha256(name.encode()).hexdigest(),
        }
    report = {"source": manifest, "burgers": {"status": "passed", "splits": splits}}
    admission = root / "admission.json"
    admission.write_text(json.dumps(report))
    return source, data, admission


def test_frozen_inputs_can_be_consumed_and_data_drift_is_rejected(tmp_path):
    source, data, admission = fixture_inputs(tmp_path)
    verify_source(source)
    verify_pretrain_inputs(admission, source, data)
    (data / "burgers_train.h5").write_bytes(b"changed")
    with pytest.raises(ValueError, match="准入后数据变化"):
        verify_pretrain_inputs(admission, source, data)


def test_source_drift_and_different_admission_are_rejected(tmp_path):
    source, data, admission = fixture_inputs(tmp_path)
    (source / "reference.py").write_text("changed")
    with pytest.raises(ValueError, match="摘要变化"):
        verify_source(source)
    report = json.loads(admission.read_text())
    report["source"]["commit"] = "another"
    admission.write_text(json.dumps(report))
    with pytest.raises(ValueError, match="源码与准入"):
        verify_pretrain_inputs(admission, source, data)


def test_failed_admission_cannot_start_formal_run(tmp_path):
    source, data, admission = fixture_inputs(tmp_path)
    report = json.loads(admission.read_text())
    report["burgers"]["status"] = "failed"
    admission.write_text(json.dumps(report))
    with pytest.raises(ValueError, match="准入未通过"):
        verify_pretrain_inputs(admission, source, data)


def test_wrong_formal_counts_or_other_dataset_are_rejected(tmp_path):
    source, data, admission = fixture_inputs(tmp_path)
    report = json.loads(admission.read_text())
    report["burgers"]["splits"]["test"]["samples"] = 10
    admission.write_text(json.dumps(report))
    with pytest.raises(ValueError, match="正式样本数量"):
        verify_pretrain_inputs(admission, source, data)


@pytest.mark.parametrize("steps", [[], ["--steps", "200000"]])
def test_legacy_cli_cannot_default_or_start_long_training(tmp_path, steps):
    import subprocess
    import sys
    from pathlib import Path

    root = Path(__file__).resolve().parents[2]
    result = subprocess.run(
        [
            sys.executable,
            str(root / "tools/verification/safediffcon/reference.py"),
            "--snapshot",
            str(tmp_path / "source"),
            "--dataset",
            str(tmp_path / "data"),
            "--output",
            str(tmp_path / "output"),
            *steps,
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2
    assert not (tmp_path / "output").exists()


def test_source_definition_extraction_does_not_execute_top_level(tmp_path):
    from tools.verification.safediffcon.reference_stages import definitions

    source = tmp_path / "original.py"
    source.write_text(
        "raise RuntimeError('side effect')\ndef original_step(x):\n    return x * 3\n"
    )
    scope = {}
    definitions(source, {"original_step"}, scope)
    assert scope["original_step"](7) == 21
    with pytest.raises(ValueError, match="原定义缺失"):
        definitions(source, {"missing"}, {})


def test_independent_stages_do_not_import_dojo_control_orchestration():
    import ast
    from pathlib import Path

    path = (
        Path(__file__).resolve().parents[2] / "tools/verification/safediffcon/reference_stages.py"
    )
    tree = ast.parse(path.read_text())
    imports = [n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)]
    assert not any(
        x
        and x.endswith(
            (
                "safediffcon.training",
                "safediffcon.inference",
                "safediffcon.calibration",
                "inference.safediffcon.control",
                "pde_control.train",
            )
        )
        for x in imports
    )
