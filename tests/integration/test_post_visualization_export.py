"""图片、网格和长表读回，整样本事务失败不覆盖原成品。"""

import csv
import json

import numpy as np
import pytest
import pyvista as pv
from PIL import Image

from ai4e_core.applications.aero_cfd import post
from tests.integration.test_post_visualization_fields import field_sample


def test_export_roundtrip_and_transaction(tmp_path, monkeypatch):
    sample = post.read_fields(field_sample())
    mesh = post.bind_mesh(sample, domain="volume")
    section = post.slice_field(mesh, origin=[0.5] * 3, normal=[1, 0, 0])
    image = post.render_field(
        section, field="volume:velocity:prediction", component="magnitude", size=(320, 240)
    )
    profile = post.profile_field(
        mesh,
        fields=["volume:velocity:prediction"],
        start=[-0.5, 0.5, 0.5],
        end=[1.5, 0.5, 0.5],
        count=21,
    )
    metrics = post.evaluate_fields(sample, selections=["volume:velocity:magnitude"])
    row = post.save_sample(
        sample,
        output=tmp_path,
        meshes={"volume": mesh, "slice": section},
        images={"slice": image},
        profiles={"velocity": profile},
        metrics=metrics,
    )
    from pathlib import Path

    manifest = Path(row["manifest"])
    root = manifest.parent
    assert Image.open(root / "figures/slice.png").size == (320, 240)
    restored = pv.read(root / "fields/volume.vtu")
    np.testing.assert_array_equal(
        restored["volume.velocity.prediction"], mesh["volume.velocity.prediction"]
    )
    assert pv.read(root / "analysis/slice.vtp").n_points == section.n_points
    rows = list(csv.DictReader((root / "profiles/velocity.csv").open()))
    assert rows[0]["valid"] == "False" and rows[0]["volume.velocity.prediction.0"] == ""
    assert json.loads((root / "metrics.json").read_text())["rows"] == metrics
    original = manifest.read_bytes()
    with pytest.raises(FileExistsError):
        post.save_sample(sample, output=tmp_path)
    import ai4e_core.applications.aero_cfd.post.analysis_export as exporter

    def fail(*args, **kwargs):
        raise OSError("测试写入失败")

    monkeypatch.setattr(exporter, "save_image", fail)
    with pytest.raises(OSError):
        post.save_sample(sample, output=tmp_path, images={"slice": image}, overwrite=True)
    assert manifest.read_bytes() == original
    assert not list(root.parent.glob(".*"))


def test_source_change_and_unsafe_name_rejected(tmp_path):
    sample = post.read_fields(field_sample())
    sample["metadata"]["identity"]["sample"] = "../bad"
    with pytest.raises(ValueError):
        post.save_sample(sample, output=tmp_path)


def test_statistics_and_missing_truth_survive_json_csv(tmp_path):
    """无真值仍交付统计；误差空值与原因及区域统计在两种格式一致。"""
    sample = post.read_fields(field_sample())
    del sample["fields"]["volume.velocity.truth"]
    metrics = post.evaluate_fields(sample, selections=["volume:velocity:magnitude"])
    row = post.save_sample(sample, output=tmp_path, metrics=metrics)
    from pathlib import Path

    root = Path(row["manifest"]).parent
    data = json.loads((root / "metrics.json").read_text())
    rows = list(csv.DictReader((root / "metrics.csv").open()))
    assert rows[0]["value"] == "" and rows[0]["reason"] == "没有真值"
    mean = next(r for r in rows if r["metric"] == "mean")
    assert float(mean["value"]) == data["statistics"]["volume:velocity:magnitude"]["mean"]
    assert int(mean["count"]) == len(sample["fields"]["volume.velocity.prediction"])
