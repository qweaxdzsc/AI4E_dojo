"""平台算法交接：具名存储、采样迁移、数值边界与真实跟踪。"""

import json
from copy import deepcopy

import pytest
import torch

from ai4e_core.abilities.data.save.store import load_named_tensors, write_named_tensors
from ai4e_core.abilities.data.source.manifest import ManifestIndex
from ai4e_core.abilities.postproc.difference import difference
from ai4e_core.abilities.transform.coordinate_normalization import CoordinateNormalization
from ai4e_core.abilities.transform.minmax import MinMax
from ai4e_core.applications.aero_cfd.inspection import normalize_config


@pytest.mark.parametrize("format", ["pt", "zarr"])
def test_named_storage_members_and_large_ids(tmp_path, format):
    values = {
        "bundle": {"p": torch.arange(6.0).reshape(2, 3), "ids": torch.tensor([2**60, 2**60 + 1])}
    }
    files = {"bundle": "out." + format}
    write_named_tensors(tmp_path / "sample", values, files)
    loaded = load_named_tensors(tmp_path / "sample", files)
    for member, value in values["bundle"].items():
        assert torch.equal(loaded["bundle"][member], value)
    manifest = {
        "version": 1,
        "state": "physical",
        "partitions": {"train": ["s"]},
        "samples": [
            {
                "partition": "train",
                "sample": "s",
                "written": True,
                "path": "sample",
                "filemap": files,
                "fields": {
                    "bundle": {
                        "state": "physical",
                        "members": {
                            name: {
                                "state": "physical",
                                "shape": list(v.shape),
                                "dtype": str(v.dtype),
                            }
                            for name, v in values["bundle"].items()
                        },
                    }
                },
            }
        ],
    }
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest))
    index = ManifestIndex(path)
    assert torch.equal(index.read("train")["bundle/ids"], values["bundle"]["ids"])
    before = index.content_digest()
    values["bundle"]["p"] += 1
    write_named_tensors(tmp_path / "sample", values, files, overwrite=True)
    assert before != index.content_digest()


def test_minmax_constant_and_coordinate_compatibility():
    transform = MinMax((2.0, 0.0), (2.0, 4.0))
    value = torch.tensor([[2.0, 0.0], [2.0, 4.0]])
    assert torch.equal(transform.apply(value), torch.tensor([[0.0, 0.0], [0.0, 1.0]]))
    assert torch.equal(transform.inverse(transform.apply(value)), value)
    old = CoordinateNormalization((0.0,), (4.0,), scale=1000.0)
    new = MinMax((0.0,), (4.0,), scale=1000.0)
    assert torch.equal(old.apply(value), new.apply(value))
    assert torch.equal(old.inverse(old.apply(value)), new.inverse(new.apply(value)))


def test_sampling_single_legacy_and_new_keys():
    old = {"trainprep": {"sampling": {"seed": 12}}}
    new = {"model": {"sampling": {"seed": 12}}}
    assert normalize_config(old)["sampling"] == normalize_config(new)["sampling"]
    with pytest.raises(ValueError, match="采样"):
        normalize_config({**old, **new})


def test_difference_rejects_equal_count_different_identity():
    left = {
        "entity_set": "mesh-revision",
        "association": "point",
        "unit": "Pa",
        "topology": "topo-hash",
        "ids": torch.tensor([0, 1]),
        "coordinates": torch.zeros(2, 3),
        "values": torch.tensor([[2.0], [3.0]]),
    }
    right = deepcopy(left)
    right["values"] -= 1
    assert torch.equal(difference(left, right), torch.ones(2, 1))
    for key, bad in [
        ("ids", torch.tensor([1, 0])),
        ("coordinates", torch.ones(2, 3)),
        ("unit", None),
        ("topology", "other"),
    ]:
        invalid = {**right, key: bad}
        with pytest.raises(ValueError):
            difference(left, invalid)


def test_real_torchvista_forward(tmp_path):
    from ai4e_core.abilities.modeling.inspection import trace

    model = torch.nn.Sequential(torch.nn.Linear(3, 4), torch.nn.Tanh(), torch.nn.Linear(4, 1))
    result = trace(
        model,
        torch.ones(2, 3),
        tmp_path,
        revision="r1",
        input_source={"sample": "actual-test-input"},
    )
    assert result["status"] == "succeeded"
    assert result["parameter_count"] == 21
    assert "html" in (tmp_path / "model.html").read_text().lower()


def test_extraction_keeps_point_and_cell_members_separate(tmp_path):
    import numpy as np
    import vtk

    from ai4e_core.applications.aero_cfd.rawprep.extraction import compile_extraction
    from ai4e_core.applications.aero_cfd.rawprep.save import tensorize
    from ai4e_core.applications.aero_cfd.rawprep.select import select_fields

    mesh = vtk.vtkPlaneSource()
    mesh.Update()
    mesh = mesh.GetOutput()
    plan = compile_extraction(
        {
            "entries": [
                {
                    "id": "entry",
                    "outputs": [
                        {
                            "name": "mixed",
                            "members": [
                                {
                                    "source_field": {"domain": "surface", "field": "fields.p"},
                                    "output_member": "point",
                                },
                                {
                                    "source_field": {"domain": "surface", "field": "fields.c"},
                                    "output_member": "cell",
                                },
                            ],
                        }
                    ],
                }
            ]
        },
        format="zarr",
    )
    context = {
        "data": {
            "surface": {
                "vtk": mesh,
                "fields": {"p": np.arange(4.0), "c": np.array([8.0])},
                "field_specs": {
                    "p": {"association": "point", "kind": "scalar"},
                    "c": {"association": "cell", "kind": "scalar"},
                },
            }
        }
    }
    selected = select_fields(context, output=plan)
    result = tensorize(selected)
    assert result["payloads"]["mixed"]["point"].numel() == 4
    assert result["payloads"]["mixed"]["cell"].numel() == 1
    assert selected["records"][0]["association"] == "point"
    assert selected["records"][1]["association"] == "cell"


def test_minmax_fit_uses_training_only():
    from types import SimpleNamespace

    from ai4e_core.abilities.data.stats.physical import freeze

    view = SimpleNamespace(
        partitions={"train": ["a"], "test": ["b"]},
        describe=dict,
        read=lambda split, index: {
            "fields": {
                "p": torch.tensor([[0.0], [2.0]]) if split == "train" else torch.tensor([[100.0]])
            }
        },
    )
    cfg = {"normalization": {"execute": True, "fields": {"p": {"method": "minmax"}}}}
    result = freeze(view, cfg)
    assert result.record["fields"]["p"]["parameters"]["maximum"] == [2.0]
    assert result.record["training_samples"] == ["a"]


def test_sampling_change_invalidates_frozen_preparation(tmp_path):
    from types import SimpleNamespace

    from ai4e_core.applications.aero_cfd.trainprep.physical import open_preparation
    from tests.integration.test_physical_dataset_contract import physical_fixture

    view = physical_fixture(tmp_path)
    config = {
        "model": {},
        "sampling": {"seed": 1},
        "trainprep": {"domains": {"surface": {"position": "pos", "targets": {"p": "p"}}}},
        "normalization": {"execute": True, "fields": {"pos": {"method": "identity"}}},
    }
    model = SimpleNamespace(SOURCE="test-component", prepare_sample=lambda *args, **kwargs: None)
    dataset = SimpleNamespace(open_physical=lambda _: view)
    _, _, record = open_preparation(config, dataset, model)
    path = tmp_path / "preparation.json"
    path.write_text(json.dumps(record))
    config["sampling"]["seed"] = 2
    with pytest.raises(ValueError, match="变化"):
        open_preparation(config, dataset, model, path)


def test_failed_trace_does_not_publish_partial_asset(tmp_path):
    from ai4e_core.abilities.modeling.inspection import trace

    class Broken(torch.nn.Module):
        def forward(self, values):
            raise ValueError("intentional invalid input")

    with pytest.raises(ValueError, match="invalid input"):
        trace(Broken(), torch.ones(1, 3), tmp_path, revision="r", input_source={})
    assert not (tmp_path / "model.html").exists()
    assert not (tmp_path / "model-inspection.json").exists()


def test_physical_grouped_output_preserves_sample_identity(tmp_path):
    from types import SimpleNamespace

    from ai4e_core.applications.aero_cfd.rawprep.physical import SavePhysical

    raw = SimpleNamespace(sources={"training": {"path": "/source/train.h5"}})
    component = SimpleNamespace(physical_fields=lambda arrays: {"p": torch.ones(2, 1)})
    config = {
        "extraction": {
            "entries": [
                {
                    "id": "e",
                    "outputs": [
                        {
                            "name": "second",
                            "members": [{"source_field": "surface/point/p", "output_member": "p"}],
                        }
                    ],
                }
            ]
        }
    }
    result = SavePhysical(raw, component, config)(
        {"partition": "train", "sample_id": "Sample001", "dry_run": False, "arrays": {}},
        output={"root": str(tmp_path)},
    )
    assert result["source"]["sample"] == result["sample"] == "Sample001"
    assert result["field_aliases"]["p"] == "second/p"


@pytest.mark.parametrize("arithmetic", ["divide", "shift_scale"])
@pytest.mark.parametrize("dtype", [torch.float32, torch.float64])
def test_coordinate_exact_legacy_arithmetic(arithmetic, dtype):
    value = torch.tensor([[-2.5, 0.125, 1.75], [2.0, -0.125, 3.0]], dtype=dtype)
    transform = CoordinateNormalization((-3.0,), (4.5,), arithmetic=arithmetic)
    lo, hi = value.new_tensor([-3.0]), value.new_tensor([4.5])
    old = (
        (value - lo) * (1000.0 / (hi - lo))
        if arithmetic == "shift_scale"
        else (value - lo) / (hi - lo) * 1000.0
    )
    inverse = (
        old * (1.0 / (1000.0 / (hi - lo))) + lo
        if arithmetic == "shift_scale"
        else old / 1000.0 * (hi - lo) + lo
    )
    assert torch.equal(transform.apply(value), old)
    assert torch.equal(transform.inverse(old), inverse)


def test_zarr_failure_preserves_previous_transaction(tmp_path, monkeypatch):
    import ai4e_core.abilities.data.save.zarr as codec

    target = tmp_path / "sample"
    files = {"p": "p.zarr"}
    original = torch.tensor([[1.0], [2.0]])
    write_named_tensors(target, {"p": original}, files)
    writer = codec.write_zarr

    def fail(path, payload):
        writer(path, payload)
        raise OSError("injected interrupted Zarr write")

    monkeypatch.setattr(codec, "write_zarr", fail)
    with pytest.raises(OSError, match="interrupted"):
        write_named_tensors(target, {"p": original + 100}, files, overwrite=True)
    assert torch.equal(load_named_tensors(target, files)["p"], original)
    assert not list(tmp_path.glob(".sample.*"))


def test_identity_sidecar_changes_digest_and_source_ids(tmp_path):
    from ai4e_core.abilities.data.source.physical import PhysicalView
    from tests.integration.test_physical_dataset_contract import physical_fixture

    physical_fixture(tmp_path)
    path = tmp_path / "manifest.json"
    manifest = json.loads(path.read_text())
    manifest["physical_layout"]["domains"]["surface"].pop("ids")
    manifest["samples"][0]["identity_assets"] = ["field-identities.json"]
    sidecar = tmp_path / "0/field-identities.json"
    sidecar.write_text(json.dumps({"pos": {"entity_ids": [10, 20, 30, 40]}}))
    path.write_text(json.dumps(manifest))
    view = PhysicalView(path)
    assert view.read("train")["domains"]["surface"]["ids"].tolist() == [10, 20, 30, 40]
    digest = view.content_digest()
    sidecar.write_text(json.dumps({"pos": {"entity_ids": [20, 10, 30, 40]}}))
    assert digest != view.content_digest()
    sidecar.write_text(json.dumps({"pos": {"entity_ids": [10, 10, 30, 40]}}))
    with pytest.raises(ValueError, match="身份"):
        view.read("train")


def test_minmax_manual_statistics_rejected():
    from types import SimpleNamespace

    from ai4e_core.abilities.data.stats.physical import freeze

    with pytest.raises(ValueError, match="训练数据"):
        freeze(
            SimpleNamespace(),
            {
                "normalization": {
                    "execute": True,
                    "fields": {
                        "p": {
                            "method": "minmax",
                            "parameters": {"minimum": [0.0], "maximum": [1.0]},
                        }
                    },
                }
            },
        )


def test_difference_rejects_foreign_same_filename(tmp_path):
    from ai4e_core.abilities.postproc.difference import compare_files

    original = tmp_path / "original"
    original.mkdir()
    foreign = tmp_path / "foreign"
    foreign.mkdir()
    filename = "surface.cp.prediction.pt"
    torch.save(torch.ones(2, 1), foreign / filename)
    metadata = original / "manifest.json"
    metadata.write_text(
        json.dumps({"filemap": {"surface.cp.prediction": filename}, "domains": {"surface": {}}})
    )
    record = {"path": str(foreign / filename), "metadata_path": str(metadata)}
    with pytest.raises(ValueError, match="引用路径"):
        compare_files([record, record], tmp_path / "difference", {})


def test_preparation_rejects_selected_different_manifest(tmp_path):
    from types import SimpleNamespace

    from ai4e_core.applications.aero_cfd.trainprep.physical import open_preparation
    from tests.integration.test_physical_dataset_contract import physical_fixture

    view = physical_fixture(tmp_path)
    cfg = {
        "model": {},
        "sampling": {},
        "trainprep": {"domains": {"surface": {"position": "pos", "targets": {"p": "p"}}}},
        "normalization": {"execute": True, "fields": {"pos": {"method": "identity"}}},
    }
    dataset = SimpleNamespace(open_physical=lambda _: view)
    model = SimpleNamespace(SOURCE="test", prepare_sample=lambda *a, **k: None)
    _, _, record = open_preparation(cfg, dataset, model)
    prep = tmp_path / "preparation.json"
    prep.write_text(json.dumps(record))
    alternate = tmp_path / "other-manifest.json"
    alternate.write_text("{}")
    cfg["train"] = {"manifest": str(alternate)}
    with pytest.raises(ValueError, match="清单与冻结准备"):
        open_preparation(cfg, dataset, model, prep)


def test_physical_prepare_rejects_version2_record(tmp_path):
    """旧物理准备接口遇到现行 version=2 记录时给出定位，不再抛 KeyError('dataset')。"""
    from types import SimpleNamespace

    from ai4e_core.applications.aero_cfd.trainprep.physical import open_preparation
    from tests.integration.test_physical_dataset_contract import physical_fixture

    view = physical_fixture(tmp_path)
    config = {
        "model": {},
        "sampling": {"seed": 1},
        "trainprep": {"domains": {"surface": {"position": "pos", "targets": {"p": "p"}}}},
        "normalization": {"execute": True, "fields": {"pos": {"method": "identity"}}},
        "train": {},
    }
    model = SimpleNamespace(SOURCE="test-component", prepare_sample=lambda *args, **kwargs: None)
    dataset = SimpleNamespace(open_physical=lambda _: view)
    path = tmp_path / "preparation.json"
    path.write_text(
        json.dumps(
            {
                "version": 2,
                "manifest": str(tmp_path / "manifest.json"),
                "dataset_digest": "unused",
                "declarations": {},
            }
        )
    )
    with pytest.raises(ValueError, match="trainprep.preparation"):
        open_preparation(config, dataset, model, path)


def test_trace_model_uses_version2_preparation(tmp_path, monkeypatch):
    """结构跟踪对现行准备走训练同一条 consume，不再打开旧物理接口。"""
    from types import SimpleNamespace

    from ai4e_core.applications.aero_cfd.inspection import _trace_batch

    prep = tmp_path / "preparation.json"
    prep.write_text(json.dumps({"version": 2, "digest": "d1", "declarations": {}}))
    called = {}

    def consume(config, reference, *, prepare, collate):
        called["reference"] = reference
        called["prepare"] = prepare
        raise RuntimeError("version2-consume-reached")

    monkeypatch.setattr("ai4e_core.applications.aero_cfd.trainprep.preparation.consume", consume)
    model = SimpleNamespace(
        prepare_inputs=object(),
        prepare_sample=object(),
        collate=object(),
    )
    with pytest.raises(RuntimeError, match="version2-consume-reached"):
        _trace_batch({"sampling": {}}, object(), model, str(prep))
    assert called["reference"] == str(prep)


def test_trace_model_requires_physical_manifest():
    from pathlib import Path

    import yaml

    from ai4e_core.applications.aero_cfd.inspection import execute

    config = yaml.safe_load(
        (Path(__file__).resolve().parents[2] / "recipes/aero_cfd/config.yaml").read_text()
    )
    config.pop("components", None)
    (config.get("train") or {}).pop("manifest", None)
    (config.get("train") or {}).pop("preparation", None)
    with pytest.raises(ValueError, match="train.manifest"):
        execute(
            {
                "operation": "trace_model",
                "config": config,
                "output_dir": str(Path("unused")),
                "component_provider": "ai4e_contrib.application.aero_cfd",
            }
        )


def test_declared_legacy_provider_and_actual_training_capabilities():
    from pathlib import Path

    import yaml

    from ai4e_core.applications.aero_cfd.inspection import execute

    root = Path(__file__).resolve().parents[2]
    legacy = yaml.safe_load((root / "recipes/aero_cfd/config.yaml").read_text())
    legacy.pop("components")
    legacy["trainprep"]["sampling"] = legacy["model"].pop("sampling")
    result = execute(
        {
            "operation": "describe_case",
            "config": legacy,
            "component_provider": "ai4e_contrib.application.aero_cfd",
        }
    )
    assert "sampling" in result["configuration"]["model"]
    assert "sampling" not in result["configuration"]["trainprep"]
    assert result["capabilities"]["losses"]["configurable"] is True
    config = yaml.safe_load(
        (root / "examples/aero_cfd/nasa_crm_transolver3/config.yaml").read_text()
    )
    result = execute({"operation": "describe_case", "config": config})
    caps = result["capabilities"]
    assert caps["training_constraints"]["evaluation_enabled"]["allowed"] == [False]
    assert caps["training_constraints"]["optimizer"]["allowed"] == ["adamw"]
    assert caps["losses"] == {
        "configurable": False,
        "fixed": "mse",
        "reason": "参考点场等权标准化逐元素均方误差",
    }
    assert "scheduler_unit" in caps["parameter_descriptors"]
    assert "min_lr_ratio" in caps["parameter_descriptors"]


def test_model_sampling_capability_follows_component():
    """采样与固定损失行由模型组件和准备域声明，不把 Transolver 抽稀当成没有采样。"""
    from pathlib import Path

    import yaml

    from ai4e_core.applications.aero_cfd.inspection import execute

    root = Path(__file__).resolve().parents[2]
    abupt = execute(
        {
            "operation": "describe_case",
            "config": yaml.safe_load(
                (root / "examples/aero_cfd/shapenet_car_abupt/config.yaml").read_text()
            ),
        }
    )
    transolver = execute(
        {
            "operation": "describe_case",
            "config": yaml.safe_load(
                (root / "examples/aero_cfd/nasa_crm_transolver3/config.yaml").read_text()
            ),
        }
    )
    assert abupt["capabilities"]["sampling"] == {"configurable": True}
    assert "supernodes" in abupt["configuration"]["model"]["sampling"]
    sampling = transolver["capabilities"]["sampling"]
    assert sampling["configurable"] is True
    assert sampling["constraints"]["stride"]["readOnly"] is True
    assert transolver["configuration"]["model"]["parameters"]["slice_num"] == 64
    assert transolver["configuration"]["model"]["sampling"]["stride"] == 4
    assert transolver["configuration"]["model"]["sampling"]["chunk_count"] == 20
    assert "supernodes" not in transolver["configuration"]["model"]["sampling"]
    assert transolver["capabilities"]["losses"]["configurable"] is False
    assert {item["target"] for item in transolver["capabilities"]["losses"]["terms"]} == {
        "surface_cp",
        "surface_cf",
    }
