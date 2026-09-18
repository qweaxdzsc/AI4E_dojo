"""训练结束写出设置：默认关闭，网格依赖预测，不解开评价锁。"""

import json
from types import SimpleNamespace

import pytest

from ai4e_core.applications.aero_cfd.inspection import parameter_capabilities
from ai4e_core.applications.aero_cfd.train import export as export_mod
from ai4e_core.applications.aero_cfd.train.export import export_training_fields
from ai4e_core.applications.aero_cfd.train.resolve import apply_resolved, validate_joint


def test_export_defaults_stay_off():
    config = apply_resolved(
        {"train": {"batch_size": 1, "num_workers": 0}, "model": {"supervision": [{"loss": "mse"}]}},
        validate=False,
    )
    assert config["train"]["export_predictions"] is False
    assert config["train"]["export_vtk"] is False
    assert config["train"]["export_split"] == "test"
    assert export_training_fields({}, trained={}, session=None, dataset_component=None, model_component=None) is None


def test_export_vtk_requires_predictions():
    with pytest.raises(ValueError, match="写出网格"):
        export_training_fields(
            {},
            trained={"checkpoints": {"last": "last.pt"}},
            session=None,
            dataset_component=None,
            model_component=None,
            predictions=False,
            meshes=True,
        )
    config = apply_resolved(
        {"train": {"batch_size": 1, "num_workers": 0}, "model": {"supervision": [{"loss": "mse"}]}},
        validate=False,
    )
    config["train"]["export_vtk"] = True
    with pytest.raises(ValueError, match="写出网格"):
        validate_joint(config)


def test_export_editable_while_evaluation_stays_locked():
    config = apply_resolved(
        {
            "components": {"workflow": "ai4e_core.applications.aero_cfd.workflow"},
            "train": {"batch_size": 1, "num_workers": 0},
            "model": {"supervision": [{"loss": "mse"}]},
        },
        validate=False,
    )
    model = type("Model", (), {"TRAINING_CONSTRAINTS": {}, "PLATFORM_LOSSES": {"configurable": False}})()
    caps = parameter_capabilities(config, model)
    assert caps["training_constraints"]["evaluation_enabled"]["readOnly"] is True
    assert caps["training_constraints"]["evaluation_enabled"]["allowed"] == [False]
    assert caps["parameter_descriptors"]["export_predictions"].get("readOnly") is not True
    assert caps["parameter_descriptors"]["export_vtk"].get("readOnly") is not True


def test_export_uses_current_preparation_not_physical(tmp_path, monkeypatch):
    """正式开训第 1 轮后写出必须消费现行 version=2，不能再进旧物理准备接口。"""
    from ai4e_core.applications.aero_cfd.trainprep.physical import consume as physical_consume

    prep = tmp_path / "preparation.json"
    prep.write_text(
        json.dumps(
            {
                "version": 2,
                "manifest": str(tmp_path / "manifest.json"),
                "dataset_digest": "unused",
                "partitions": {"test": ["param1/sample-a"]},
            }
        )
    )
    with pytest.raises(ValueError, match="trainprep.preparation"):
        physical_consume({}, None, None, prep)

    captured = {}

    def open_inference(config, **kwargs):
        captured["samples"] = list(config["infer"]["samples"])
        captured["preparation"] = config["train"]["preparation"]
        captured["evaluate"] = config["infer"]["evaluate"]
        captured["export_vtk"] = config["infer"]["export_vtk"]
        return SimpleNamespace()

    monkeypatch.setattr(export_mod.infer_stage, "open_inference", open_inference)
    for name in (
        "configure_restore",
        "configure_prediction",
        "configure_physical_output",
        "configure_selection",
        "configure_evaluation",
        "configure_save",
        "configure_mesh_export",
    ):
        monkeypatch.setattr(export_mod.infer_stage, name, lambda job, **kwargs: job)
    monkeypatch.setattr(
        export_mod.infer_stage,
        "execute",
        lambda job: {"mode": "export", "samples": captured["samples"]},
    )

    result = export_training_fields(
        {"train": {"device": "cpu"}, "infer": {}, "model": {}},
        trained={"checkpoints": {"last": str(tmp_path / "last.pt")}},
        session=SimpleNamespace(output_dir=lambda name: tmp_path / name, dry_run=False),
        dataset_component=object(),
        model_component=object(),
        predictions=True,
        preparation=str(prep),
    )
    assert result == {"mode": "export", "samples": ["param1/sample-a"]}
    assert captured["preparation"] == str(prep)
    assert captured["evaluate"] is False
    assert captured["export_vtk"] is False


def test_export_rejects_old_physical_preparation(tmp_path):
    """旧物理准备不能借训练结束写出绕过现行 version=2 契约。"""
    prep = tmp_path / "preparation.json"
    prep.write_text(json.dumps({"version": 1, "dataset": "legacy", "partitions": {"test": ["s0"]}}))
    with pytest.raises(ValueError, match="preparation_requires_regeneration"):
        export_training_fields(
            {"train": {"device": "cpu"}, "infer": {}},
            trained={"checkpoints": {"last": str(tmp_path / "last.pt")}},
            session=SimpleNamespace(output_dir=lambda name: tmp_path / name, dry_run=False),
            dataset_component=object(),
            model_component=object(),
            predictions=True,
            preparation=str(prep),
        )
