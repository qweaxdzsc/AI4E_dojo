"""平台算法交接：具名存储、采样迁移、数值边界与真实跟踪。"""

import json
from copy import deepcopy
from pathlib import Path

import pytest
import torch

from ai4e_core.abilities.data.save.store import load_named_tensors, write_named_tensors
from ai4e_core.abilities.data.source.manifest import ManifestIndex
from ai4e_core.abilities.postproc.difference import difference
from ai4e_core.abilities.transform.coordinate_normalization import CoordinateNormalization
from ai4e_core.abilities.transform.minmax import MinMax
from ai4e_core.abilities.transform.normalization import Normalization
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


def test_field_scale_applies_after_coordinate_minmax():
    record = {
        "version": 2,
        "fields": {
            "x": {
                "method": "coordinate",
                "parameters": {"minimum": [0.0], "maximum": [4.0]},
                "scale": 1000,
            }
        },
    }
    transform = Normalization(record).transforms["x"]
    value = torch.tensor([[0.0, 2.0, 4.0]])
    assert torch.equal(transform.apply(value), torch.tensor([[0.0, 500.0, 1000.0]]))
    torch.testing.assert_close(transform.inverse(transform.apply(value)), value)
    with pytest.raises(ValueError, match="scale"):
        Normalization(
            {
                "version": 2,
                "fields": {"x": {"method": "identity", "parameters": {}, "scale": 0}},
            }
        )


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


def test_fit_graph_viewport_uses_width_not_entire_graph():
    from ai4e_core.abilities.modeling.inspection import fit_graph_viewport

    html = (
        "const scale = Math.min(width / graphWidth, height / graphHeight) * 0.9;\n"
        "height / 2 - (minY + graphHeight / 2) * scale"
    )
    fitted = fit_graph_viewport(html)
    assert "height / graphHeight" not in fitted
    assert "24 - minY * scale" in fitted


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
    assert result["graph_view"] == "compressed_modules"
    assert result["graph_nodes"] < 40
    html = (tmp_path / "model.html").read_text()
    assert "html" in html.lower()
    assert "const show_modular_view = true;" in html
    assert "Math.min(1, (width * 0.92) / Math.max(graphWidth, 1))" in html


def test_trace_keeps_domain_blocks_as_medium_module_graph(tmp_path):
    from ai4e_core.abilities.modeling.inspection import trace

    class DomainLike(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.up = torch.nn.Linear(4, 8)
            self.down = torch.nn.Linear(8, 4)

        def forward(self, x, frequencies=None, kv=None, condition=None, *, kind=None):
            if isinstance(x, dict):
                return self.forward_domains(x, frequencies, kv, kind=kind)
            return self.down(torch.relu(self.up(x)))

        def forward_domains(self, values, frequencies, anchors, *, kind):
            tensor = torch.cat(list(values.values()), dim=0)
            for _ in range(6):
                tensor = torch.nn.functional.gelu(tensor + tensor.tanh())
            tensor = self.forward(tensor)
            return {name: tensor for name in values}, {}

    class Stack(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.blocks = torch.nn.ModuleList([DomainLike() for _ in range(4)])

        def forward(self, values):
            current = {"surface": values}
            for block in self.blocks:
                current, _ = block(current, {}, {}, kind="s")
            return current["surface"]

    result = trace(
        Stack(),
        torch.ones(2, 4),
        tmp_path,
        revision="r-domain",
        input_source={"sample": "domain-blocks"},
        predict=lambda model, values: model(values),
    )
    assert result["graph_view"] == "compressed_modules"
    assert result["graph_nodes"] < 80


def test_trace_official_abupt_stays_medium_module_graph(tmp_path):
    from ai4e_contrib.ability.model.abupt.model import predict
    from ai4e_core.abilities.modeling.inspection import trace
    from tests.integration.test_abupt_multidomain import inputs, make_model

    model = make_model()
    result = trace(
        model,
        inputs(),
        tmp_path,
        revision="r-abupt",
        input_source={"sample": "tiny-abupt"},
        predict=predict,
    )
    assert result["status"] == "succeeded"
    assert result["graph_view"] == "compressed_modules"
    assert result["graph_nodes"] < 250


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
        "sampling": {"seed": 1, "geometry": {"method": "uniform", "max_points": 64}},
        "trainprep": {"domains": {"surface": {"position": "pos", "targets": {"p": "p"}}}},
        "normalization": {"execute": True, "fields": {"pos": {"method": "identity"}}},
    }
    model = SimpleNamespace(SOURCE="test-component", prepare_sample=lambda *args, **kwargs: None)
    dataset = SimpleNamespace(open_physical=lambda _: view)
    _, _, record = open_preparation(config, dataset, model)
    path = tmp_path / "preparation.json"
    path.write_text(json.dumps(record))
    assert "max_points" not in record["declarations"]["sampling"].get("geometry", {})
    config["sampling"]["seed"] = 2
    config["sampling"]["geometry"]["max_points"] = 3586
    open_preparation(config, dataset, model, path)
    config["sampling"]["geometry"]["method"] = "fps"
    view, _, imported = open_preparation(config, dataset, model, path)
    assert imported["version"] == record["version"]
    assert view is not None


def test_failed_trace_does_not_publish_partial_asset(tmp_path):
    from ai4e_core.abilities.modeling.inspection import trace

    class Broken(torch.nn.Module):
        def forward(self, values):
            raise ValueError("intentional invalid input")

    with pytest.raises(ValueError, match="invalid input"):
        trace(Broken(), torch.ones(1, 3), tmp_path, revision="r", input_source={})
    assert not (tmp_path / "model.html").exists()
    assert not (tmp_path / "model-inspection.json").exists()


def test_case_inspect_trace_prepares_network_without_html(tmp_path, monkeypatch):
    """外流检查只取样组网，不写 HTML、不导入 TorchVista。"""
    from pathlib import Path
    from types import SimpleNamespace

    from ai4e_core.applications.aero_cfd.inspection import execute

    source = (
        Path(__file__).resolve().parents[2]
        / "packages/ai4e-core/applications/aero_cfd/inspection.py"
    )
    text = source.read_text(encoding="utf-8")
    assert "torchvista" not in text
    assert "model.html" not in text
    assert "from ai4e_core.abilities.modeling.inspection import trace" not in text

    network = torch.nn.Linear(3, 1)
    model = SimpleNamespace(
        resolve=lambda cfg, validate=False: cfg,
        SOURCE="abupt",
        construct=lambda **_kwargs: network,
        training_parameters=lambda cfg: {},
        predict=lambda inner, values: inner(values),
        prepare_inputs=lambda *args, **kwargs: None,
        prepare_sample=lambda *args, **kwargs: None,
        collate=lambda items: items[0],
    )
    monkeypatch.setattr(
        "ai4e_core.applications.aero_cfd.inspection._components",
        lambda _cfg: (SimpleNamespace(), model),
    )
    monkeypatch.setattr(
        "ai4e_core.applications.aero_cfd.rawprep.descriptor.dataset_component",
        lambda _source: SimpleNamespace(),
    )
    monkeypatch.setattr(
        "ai4e_core.applications.aero_cfd.rawprep.descriptor.resolve_rawprep",
        lambda value: value,
    )
    monkeypatch.setattr(
        "ai4e_core.applications.aero_cfd.inspection._trace_batch",
        lambda *_args, **_kwargs: ({"inputs": torch.ones(2, 3)}, {"sample": "prepared"}),
    )
    output = tmp_path / "trace"
    result = execute(
        {
            "operation": "trace_model",
            "config": {
                "components": {"model": "m", "dataset": "d"},
                "train": {"preparation": str(tmp_path / "prep.json")},
            },
            "output_dir": str(output),
        }
    )
    assert result["network"] is network
    assert torch.equal(result["inputs"], torch.ones(2, 3))
    assert result["input_source"] == {"sample": "prepared"}
    assert list(output.glob("*.html")) == []
    assert not (output / "model-inspection.json").exists()


def test_platform_views_export_both_html_or_neither(tmp_path, monkeypatch):
    from ai4e_contrib.application.aero_cfd.model_inspection import export_platform_views

    model = torch.nn.Sequential(torch.nn.Linear(3, 4), torch.nn.Tanh(), torch.nn.Linear(4, 1))
    result = export_platform_views(
        model,
        torch.ones(2, 3),
        tmp_path,
        revision="r-views",
        input_source={"sample": "platform-views"},
    )
    assert result["default_view"] == "stage_trunk"
    assert set(result["views"]) == {"stage_trunk", "stage_blocks"}
    assert (tmp_path / "model.stage-trunk.html").is_file()
    assert (tmp_path / "model.stage-blocks.html").is_file()
    assert (
        "Math.min(1, (width * 0.92) / Math.max(graphWidth, 1))"
        in (tmp_path / "model.stage-trunk.html").read_text()
    )

    def fail_second(*_args, **_kwargs):
        raise RuntimeError("second view failed")

    broken = tmp_path / "broken"
    monkeypatch.setattr("ai4e_core.abilities.modeling.inspection._export_one", fail_second)
    with pytest.raises(RuntimeError, match="second view failed"):
        export_platform_views(
            model,
            torch.ones(2, 3),
            broken,
            revision="r-fail",
            input_source={"sample": "fail"},
        )
    assert list(broken.glob("*.html")) == []
    assert not (broken / "model-inspection.json").exists()


def test_inspection_worker_only_accepts_serializable_application_results(tmp_path):
    from ai4e_task.tasks.inspection_worker import render_inspection

    from ai4e_contrib.application.aero_cfd.model_inspection import export_platform_views

    model = torch.nn.Linear(3, 1)
    result = render_inspection(
        {"operation": "trace_model"},
        lambda _: export_platform_views(
            model, torch.ones(2, 3), tmp_path, revision="fixed", input_source={"sample": "real"}
        ),
    )
    assert result["status"] == "succeeded"
    assert Path(result["path"]).is_file()
    with pytest.raises(TypeError):
        render_inspection({}, lambda _: {"network": model})


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
        (value - lo) * (1.0 / (hi - lo))
        if arithmetic == "shift_scale"
        else (value - lo) / (hi - lo) * 1.0
    )
    inverse = (
        old * (1.0 / (1.0 / (hi - lo))) + lo
        if arithmetic == "shift_scale"
        else old / 1.0 * (hi - lo) + lo
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
    _, _, imported = open_preparation(cfg, dataset, model, prep)
    assert imported["manifest"] == record["manifest"]


def test_physical_post_imports_generic_version2_record(tmp_path):
    """历史 post 门面只读导入现行 version=2 准备，不比较冻结业务声明。"""
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
    from ai4e_core.abilities.data.source.manifest import ManifestIndex
    from ai4e_core.abilities.transform.normalization import Normalization
    from ai4e_core.applications.aero_cfd.trainprep.preparation import dataset_digest, digest

    normalization = Normalization(
        {
            "version": 2,
            "fields": {"pos": {"method": "identity", "parameters": {}, "scale": 1}},
            "source": None,
            "training_samples": ["s"],
        }
    )
    record = {
        "version": 2,
        "manifest": view.describe()["reference"],
        "dataset_digest": dataset_digest(ManifestIndex(view.describe()["reference"])),
        "normalization": normalization.record,
        "normalization_digest": normalization.digest,
        "declarations": {},
        "partitions": view.partitions,
    }
    record["digest"] = digest(record)
    path.write_text(json.dumps(record))
    imported_view, imported_normalization, imported = open_preparation(config, dataset, model, path)
    assert imported_view.partitions == view.partitions
    assert imported_normalization.digest == normalization.digest
    assert imported == record


def test_trace_model_rejects_version1_preparation(tmp_path):
    """公开跟踪不再分流到旧物理接口，旧准备要求重新生成。"""
    from ai4e_core.applications.aero_cfd.inspection import _trace_batch

    prep = tmp_path / "preparation.json"
    prep.write_text(json.dumps({"version": 1, "dataset": "legacy"}))
    with pytest.raises(ValueError, match="preparation_requires_regeneration"):
        _trace_batch({"sampling": {}}, object(), object(), str(prep))


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


def test_trace_and_model_check_use_current_sampling_not_prep_counts(tmp_path, monkeypatch):
    """旧准备 64 点不能挡住当前模型页 3586 点的检查和结构跟踪。"""
    from pathlib import Path
    from types import SimpleNamespace

    from ai4e_core.applications.aero_cfd.inspection import (
        _consume_current_preparation,
        _trace_batch,
        execute,
    )
    from ai4e_core.applications.aero_cfd.trainprep.preparation import (
        declarations,
        digest,
        frozen_contract,
    )
    from tests.integration.test_trainprep_consume import _config, _declared

    frozen = _declared()
    payload = {
        "version": 2,
        "manifest": str(tmp_path / "manifest.json"),
        "dataset_digest": "unused",
        "normalization": {},
        "normalization_digest": "unused",
        "declarations": frozen,
        "external_inputs": {},
        "components": {
            "prepare": {"name": "prepare", "sha256": "a"},
            "collate": {"name": "collate", "sha256": "b"},
        },
        "split_counts": {"train": 1},
        "partitions": {"train": ["s"]},
        "split": {},
    }
    payload["digest"] = digest(payload)
    prep = tmp_path / "preparation.json"
    prep.write_text(json.dumps(payload))
    current = deepcopy(frozen)
    current["sampling"]["geometry"]["max_points"] = 3586
    current["sampling"]["supernodes"]["num_points"] = 512
    current["sampling"]["domains"]["surface"]["anchor"]["num_points"] = 256
    config = _config(current)
    config["sampling"] = current["sampling"]
    assert frozen_contract(frozen) == frozen_contract(declarations(config))

    seen = {}

    def consume(cfg, reference, *, prepare, collate):
        record = json.loads(Path(reference).read_text())
        assert frozen_contract(record["declarations"]) == frozen_contract(declarations(cfg))
        seen["max_points"] = cfg["sampling"]["geometry"]["max_points"]
        return SimpleNamespace(
            record={"digest": record["digest"]},
            prepare=prepare,
            collate=lambda items: {"inputs": items[0], "sampling": cfg["sampling"]},
            index=SimpleNamespace(partitions={"train": ["s"]}, manifest={"state": "physical"}),
            physical_prepare=None,
            normalization=None,
        )

    monkeypatch.setattr("ai4e_core.applications.aero_cfd.trainprep.preparation.consume", consume)
    monkeypatch.setattr(
        "ai4e_core.applications.aero_cfd.trainprep.dataset.prepare_partition_sample",
        lambda *_args, **kwargs: {"sampling": kwargs["sampling"]},
    )
    model = SimpleNamespace(
        prepare_inputs=lambda *args, **kwargs: None,
        prepare_sample=lambda *args, **kwargs: None,
        collate=lambda items: items[0],
        resolve=lambda cfg, validate=False: cfg,
        SOURCE="abupt",
        construct=lambda **_kwargs: SimpleNamespace(cpu=lambda: SimpleNamespace(eval=lambda: None)),
        training_parameters=lambda cfg: {},
        predict=None,
    )
    data = _consume_current_preparation(config, model, str(prep))
    assert data.record["digest"] == payload["digest"]
    assert seen["max_points"] == 3586
    batch, source = _trace_batch(config, object(), model, str(prep))
    assert batch["sampling"]["geometry"]["max_points"] == 3586
    assert source["preparation"] == payload["digest"]

    monkeypatch.setattr(
        "ai4e_core.applications.aero_cfd.inspection._components",
        lambda _cfg: (SimpleNamespace(), model),
    )
    monkeypatch.setattr(
        "ai4e_core.applications.aero_cfd.rawprep.descriptor.dataset_component",
        lambda _source: SimpleNamespace(),
    )
    monkeypatch.setattr(
        "ai4e_core.applications.aero_cfd.rawprep.descriptor.resolve_rawprep",
        lambda source: source,
    )
    checked = execute(
        {
            "operation": "validate_configuration",
            "config": {
                **config,
                "components": {"model": "m", "dataset": "d"},
                "train": {**config["train"], "preparation": str(prep)},
            },
            "selection": {"stage": "model"},
            "output_dir": str(tmp_path / "check"),
        }
    )
    assert checked["valid"] is True
    assert checked["readiness"]["digest"] == payload["digest"]


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


def test_contrib_inspect_requires_explicit_legacy_configuration_conversion():
    """旧配置键明确拒绝，不在检查时改写历史配置或猜输入位置。"""
    from pathlib import Path

    import yaml

    from ai4e_contrib.application.aero_cfd.operations import inspect

    config = yaml.safe_load(
        (Path(__file__).resolve().parents[2] / "recipes/aero_cfd/config.yaml").read_text()
    )
    config.setdefault("dataset", {})["root"] = "/tmp/legacy-dataset"
    import pytest

    with pytest.raises(ValueError, match="dataset.root"):
        inspect({"operation": "describe_case", "config": config})
    assert config["dataset"]["root"] == "/tmp/legacy-dataset"
    del config["dataset"]["root"]
    result = inspect({"operation": "describe_case", "config": config})
    assert result["capabilities"]["sampling"]["configurable"] is True


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
    assert caps["training_constraints"]["evaluation_split"]["allowed"] == ["eval"]
    assert caps["training_constraints"]["optimizer"]["allowed"] == ["adamw"]
    assert {k: caps["losses"][k] for k in ("configurable", "fixed", "reason")} == {
        "configurable": False,
        "fixed": "mse",
        "reason": "参考点场等权标准化逐元素均方误差",
    }
    assert [term["target"] for term in caps["losses"]["terms"]] == ["surface_cp", "surface_cf"]
    assert all(term["loss"] == "mse" and term["weight"] == 1 for term in caps["losses"]["terms"])
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
