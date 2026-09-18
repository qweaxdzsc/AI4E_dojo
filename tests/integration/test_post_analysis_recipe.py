"""固定结果只读分析和参数往返，不读取模型或修改输入来源。"""

import json
from pathlib import Path

import pytest
import torch

from ai4e_core.abilities.data.validate.fingerprint import fingerprint
from ai4e_core.applications.aero_cfd import post
from tests.integration.test_post_visualization_fields import field_sample


def saved_sample(root):
    """写独立冻结输入，便于实际脚本和安装进程读取。"""
    from ai4e_core.abilities.postproc.export.visualization import save_mesh

    root.mkdir(parents=True)
    original = field_sample()
    mesh = post.bind_mesh(post.read_fields(original), domain="volume")
    save_mesh(mesh, root / "volume.vtu")
    meta = original["metadata"]
    meta["filemap"] = {name: name + ".pt" for name in original["fields"]}
    meta["meshes"] = {"volume": {"path": "volume.vtu"}}
    for name, value in original["fields"].items():
        torch.save(torch.from_numpy(value), root / meta["filemap"][name])
    protocol = {"dataset": "analytic"}
    protocol["digest"] = fingerprint(protocol)
    meta["protocol"] = protocol["digest"]
    (root / "manifest.json").write_text(json.dumps(meta))
    report = {
        "version": 1,
        "status": "succeeded",
        "protocol": protocol,
        "results": [{"sample": "s", "manifest": str(root / "manifest.json")}],
        "metrics": {},
    }
    (root / "results.json").write_text(json.dumps(report))
    return root / "manifest.json", root / "results.json"


def test_metric_only_and_frozen_source(tmp_path, monkeypatch):
    manifest, result = saved_sample(tmp_path / "input")
    import ai4e_core.abilities.postproc.visualization.fields as visual

    def fail():
        raise AssertionError("指标不应加载 PyVista")

    monkeypatch.setattr(visual, "pyvista", fail)
    import ai4e_core.applications.aero_cfd.post.field_binding as binding

    original_hash = binding.file_fingerprint

    def hash_arrays_only(path):
        assert Path(path).suffix not in {".vtp", ".vtu"}, "纯指标不能读取网格内容"
        return original_hash(path)

    monkeypatch.setattr(binding, "file_fingerprint", hash_arrays_only)
    source = post.open_analysis(result)
    sample = post.read_fields(source.samples[0])
    rows = post.evaluate_fields(sample, selections=["volume:velocity:magnitude"])
    written = post.save_sample(sample, output=tmp_path / "output", metrics=rows)
    summary = post.publish_analysis([written], source=source, output=tmp_path / "output")
    assert summary["status"] == "succeeded"
    assert summary["metrics"]["volume:velocity:magnitude:mae"]["mean"] == pytest.approx(0.1)
    manifest.write_text(manifest.read_text() + " ")
    with pytest.raises(ValueError, match="来源发生变化"):
        post.save_sample(sample, output=tmp_path / "changed")


def test_analysis_configuration_external_directory(tmp_path, monkeypatch):
    from ai4e_contrib.application.aero_cfd.configuration import (
        application_parameters,
        load_configuration,
    )

    root = Path(__file__).resolve().parents[2]
    path = root / "examples/aero_cfd/shapenet_car_abupt/config.yaml"
    monkeypatch.chdir(tmp_path)
    cfg = load_configuration(
        path, {"post.analysis_enabled": True, "data_root": str(tmp_path / "data")}
    )
    assert cfg.paths.datasets.post == str(tmp_path / "data/post")
    assert application_parameters(cfg)["post"]["analysis_enabled"] is True
    with pytest.raises(ValueError, match="snapshot_sample"):
        load_configuration(path, {"post.snapshot_every": 1})


def test_check_reads_only_metadata_and_partial_batch_counts(tmp_path, monkeypatch):
    """检查不读物理数组；失败批次保留已提交样本与准确数量。"""
    from dataclasses import replace

    manifest, report = saved_sample(tmp_path / "input")
    source = post.open_analysis(report)
    import ai4e_core.applications.aero_cfd.post.field_binding as binding

    with monkeypatch.context() as patch:
        patch.setattr(binding, "read_fields", lambda *a: pytest.fail("检查不得读取数组"))
        assert (
            post.check_analysis(source, settings={"fields": ["volume:velocity:magnitude"]})["scope"]
            == "metadata_only"
        )
    sample = post.read_fields(manifest)
    rows = post.evaluate_fields(sample, selections=["volume:velocity:magnitude"])
    saved = post.save_sample(sample, metrics=rows, output=tmp_path / "output")
    source = replace(source, samples=(*source.samples, {"sample": "failed"}))
    summary = post.publish_analysis(
        [saved],
        source=source,
        output=tmp_path / "output",
        failures=[{"sample": "failed", "error": "test"}],
    )
    assert summary["status"] == "partial"
    values = summary["metrics"]["volume:velocity:magnitude:mae"]
    assert values["failed"] == 1 and values["expected"] == 2 and not values["complete"]
