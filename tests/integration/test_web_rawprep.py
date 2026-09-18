"""页面不能静默提交超出现有 recipe 的配置。"""

import importlib
import json
from copy import deepcopy
from pathlib import Path

import ai4e_task as task

from ai4e_core.applications.aero_cfd.rawprep.catalog import sample_key
from tests.integration.test_web_dataset_binding import (
    binding_platform as binding_platform,  # noqa: PLC0414 - 复用绑定夹具。
)
from tests.integration.test_web_dataset_binding import create, sources
from tests.integration.test_web_project_task import (
    platform as platform,  # noqa: PLC0414 - 显式重导出共享 pytest fixture。
)

ROOT = Path(__file__).resolve().parents[2]

OFFICIAL_COUNT = 889
POISONED = {
    "train": ["param1/1dc58be25e1b6e5675cad724c63e222e"],
    "test": ["param1/1dc757e77f3cfad0253c03b7df20edd5"],
}
SELECTED = sample_key("train", POISONED["train"][0])


def _load_source(module_name, relative):
    module = importlib.import_module(module_name)
    path = ROOT / relative
    exec(compile(path.read_text(), str(path), "exec"), module.__dict__)  # noqa: S102 - 验收源码而非未重装副本
    return module


def _source_dataset_run_overrides():
    text = (ROOT / "packages/ai4e-server/modules/rawprep/application.py").read_text()
    start = text.index("def dataset_run_overrides")
    end = text.index("\ndef save_configuration")
    namespace = {"json": json}
    exec(text[start:end], namespace)  # noqa: S102 - 验收源码而非未重装副本
    return namespace["dataset_run_overrides"]


def _source_inspect_dataset():
    inspection = _load_source(
        "ai4e_contrib.application.datasets.shapenet_car.inspection",
        "packages/ai4e-contrib/application/datasets/shapenet_car/inspection.py",
    )
    package = importlib.import_module("ai4e_contrib.application.datasets.shapenet_car")
    package.inspect_dataset = inspection.inspect_dataset
    return inspection.inspect_dataset


def test_invalid_mapping_and_manual_count(platform):
    c, p, t, _root, _ = platform
    url = f"/api/v1/projects/{p}/tasks/{t['id']}/rawprep"
    original = c.get(url).json()
    mutations = [
        ("fields", {"surface": {"renamed": {"components": 1}}}),
        ("save_fields", ["custom_bundle"]),
        ("geometry", []),
        ("vtkhdf", "yes"),
    ]
    for key, value in mutations:
        cfg = deepcopy(original)
        cfg["rawprep"][key] = value
        rejected = c.put(url, json={k: v for k, v in cfg.items() if k != "processed_name_status"})
        assert rejected.status_code == 400 and "rawprep." in rejected.text
        assert c.get(url).json() == original
    selection = {
        "revision": original["revision"],
        "root": "data0",
        "files": [],
        "all_selected": False,
        "count": 1,
    }
    assert c.post(url + "/execute", json=selection).status_code == 400
    assert c.get(f"/api/v1/projects/{p}/runs").json() == []


def _use_source_rawprep(monkeypatch):
    """force-include 安装副本未重装时，仍按仓库源码验收输入/输出分离。"""
    app = _load_source(
        "ai4e_server.modules.rawprep.application",
        "packages/ai4e-server/modules/rawprep/application.py",
    )
    api = importlib.import_module("ai4e_server.modules.rawprep.api")
    api.preflight = app.preflight
    api.submit = app.submit
    inspect_dataset = _source_inspect_dataset()
    nasa = _load_source(
        "ai4e_contrib.application.datasets.nasa_crm.inspection",
        "packages/ai4e-contrib/application/datasets/nasa_crm/inspection.py",
    )
    importlib.import_module("ai4e_contrib.application.datasets.nasa_crm").inspect_dataset = (
        nasa.inspect_dataset
    )

    def inspect_task(project, task_id, operation, **kwargs):
        from ai4e_contrib.application.aero_cfd.operations import inspect as domain_inspect

        captured = task.read_configuration(project, task_id)
        if captured["revision"] != kwargs["revision"]:
            raise ValueError("configuration_revision_conflict")
        recipe = Path(task.get_task(project, task_id)["directory"]) / "recipe"
        return domain_inspect(
            {
                "operation": operation,
                "config": captured["config"],
                "config_dir": str(recipe),
                "selection": kwargs.get("selection") or {},
                "output_dir": kwargs.get("output_dir"),
            }
        )

    monkeypatch.setattr(app.task, "inspect_task", inspect_task)
    monkeypatch.setattr(task, "inspect_task", inspect_task)
    return inspect_dataset


def _poison_partitions(client, base, identity, partitions):
    project = client.app.state.services.project(base.rsplit("/", 1)[-1])
    current = task.read_configuration(project, identity)
    task.save_configuration(
        project, identity, {"dataset": {"partitions": partitions}}, revision=current["revision"]
    )
    return project, task.read_configuration(project, identity)


def test_catalog_all_uses_official_partitions_not_task_subset(binding_platform, monkeypatch):
    _use_source_rawprep(monkeypatch)
    client, base, _, _ = binding_platform
    created = create(client, base, "shapenet_car_abupt")
    url = base + "/tasks/" + created["id"]
    initial = client.get(url + "/dataset").json()
    assert (
        client.put(
            url + "/dataset",
            json={
                "expected_revision": initial["revision"],
                "sources": sources("shapenet_car_abupt"),
            },
        ).status_code
        == 200
    )
    project, captured = _poison_partitions(client, base, created["id"], POISONED)
    cfg = client.get(url + "/rawprep").json()
    catalog = client.post(
        url + "/rawprep/catalog",
        json={"revision": cfg["revision"], "sample_scope": {"mode": "all", "values": []}},
    )
    assert catalog.status_code == 200, catalog.text
    value = catalog.json()
    assert value["sample_universe"] == "bound_dataset"
    assert len(value["samples"]) == OFFICIAL_COUNT
    specified = client.post(
        url + "/rawprep/catalog",
        json={
            "revision": cfg["revision"],
            "sample_scope": {"mode": "samples", "values": [SELECTED]},
        },
    )
    assert specified.status_code == 200, specified.text
    assert len(specified.json()["samples"]) == 1
    assert specified.json()["samples"][0]["sample_id"] == POISONED["train"][0]
    after = task.read_configuration(project, created["id"])
    assert after["config"]["dataset"]["partitions"] == POISONED
    assert after["revision"] == captured["revision"]


def test_save_execute_publish_do_not_write_output_list_back(binding_platform, monkeypatch):
    _use_source_rawprep(monkeypatch)
    client, base, _, _ = binding_platform
    created = create(client, base, "shapenet_car_abupt")
    url = base + "/tasks/" + created["id"]
    initial = client.get(url + "/dataset").json()
    bound = client.put(
        url + "/dataset",
        json={"expected_revision": initial["revision"], "sources": sources("shapenet_car_abupt")},
    )
    assert bound.status_code == 200, bound.text
    project, _ = _poison_partitions(client, base, created["id"], POISONED)
    cfg = client.get(url + "/rawprep").json()
    saved = client.put(
        url + "/rawprep",
        json={
            "revision": cfg["revision"],
            "rawprep": cfg["rawprep"],
            "processed_name": "shapenet_car2",
        },
    )
    assert saved.status_code == 200, saved.text
    stored = task.read_configuration(project, created["id"])
    assert stored["config"]["dataset"]["partitions"] == POISONED
    assert stored["config"]["dataset"]["processed_name"] == "shapenet_car2"
    assert "partition" not in stored["config"]["dataset"]

    captured = {}

    def fake_submit(*_args, **kwargs):
        captured.update(kwargs)
        return {"id": "rawprep-run", "status": "pending"}

    monkeypatch.setattr("ai4e_server.modules.rawprep.application.task.submit_run", fake_submit)
    monkeypatch.setattr(
        "ai4e_server.modules.rawprep.application.preflight",
        lambda *_args, **_kwargs: {
            "revision": stored["revision"],
            "root": str(project),
            "dataset_id": "shapenet_car",
            "samples": POISONED["train"],
            "sample_selection": POISONED["train"],
            "digests": {},
        },
    )
    started = client.post(
        url + "/rawprep/execute",
        json={"revision": stored["revision"], "sample_scope": {"mode": "all", "values": []}},
    )
    assert started.status_code == 200, started.text
    overrides = captured["overrides"]
    assert "dataset.partitions=" + json.dumps("unsplit") in overrides
    assert "dataset.samples=" + json.dumps("all") in overrides
    assert "dataset.partitions=" + json.dumps("official") not in overrides
    assert not any(item.startswith("dataset.partitions={") for item in overrides)
    assert "inputs.rawprep.source=" in "\n".join(overrides)
    after_execute = task.read_configuration(project, created["id"])
    assert after_execute["config"]["dataset"]["partitions"] == POISONED
    assert after_execute["config"]["inputs"]["rawprep"]["source"] == stored["config"]["inputs"][
        "rawprep"
    ]["source"]

    captured.clear()
    selected = client.post(
        url + "/rawprep/execute",
        json={
            "revision": stored["revision"],
            "sample_scope": {"mode": "samples", "values": [SELECTED]},
        },
    )
    assert selected.status_code == 200, selected.text
    selected_overrides = captured["overrides"]
    assert "dataset.partitions=" + json.dumps("unsplit") in selected_overrides
    assert "dataset.partitions=" + json.dumps("official") not in selected_overrides
    assert "dataset.samples=" + json.dumps(POISONED["train"]) in selected_overrides
    assert task.read_configuration(project, created["id"])["config"]["dataset"]["partitions"] == (
        POISONED
    )
    published = task.publish_processed_from_run(
        project,
        project,
        created["id"],
        {
            "id": "rawprep-run",
            "status": "succeeded",
            "operation_mode": "execute",
            "stages": ["rawprep"],
            "data_dir": str(project / "missing-rawprep-output"),
        },
        config=after_execute["config"],
    )
    assert published is None
    assert task.read_configuration(project, created["id"])["config"]["dataset"]["partitions"] == (
        POISONED
    )


def test_inspect_dataset_ignores_task_partition_when_scoped(tmp_path):
    inspect_dataset = _source_inspect_dataset()
    root = tmp_path / "root"
    root.mkdir()
    result = inspect_dataset(
        {
            "dataset": {"root": str(root), "partition": POISONED, "samples": "all"},
            "sample_scope": {"mode": "all", "values": []},
        }
    )
    assert result["sample_universe"] == "bound_dataset"
    assert len(result["samples"]) == OFFICIAL_COUNT


def test_dataset_run_overrides_keep_official_universe():
    info = {"samples": ["a"], "sample_selection": ["a"]}
    task_dataset = {"processed_name": "out", "partitions": POISONED, "samples": ["hidden"]}
    dataset_run_overrides = _source_dataset_run_overrides()
    all_run = dataset_run_overrides(
        "shapenet_car", {"mode": "all", "values": []}, info, task_dataset
    )
    assert "dataset.partitions=" + json.dumps("unsplit") in all_run
    assert "dataset.partitions=" + json.dumps("official") not in all_run
    assert "dataset.samples=" + json.dumps("all") in all_run
    assert "dataset.processed_name=" + json.dumps("out") in all_run
    assert not any("hidden" in item or "1dc58be2" in item for item in all_run)
    one = dataset_run_overrides(
        "shapenet_car", {"mode": "samples", "values": [SELECTED]}, info, task_dataset
    )
    assert "dataset.samples=" + json.dumps(["a"]) in one
    nasa = dataset_run_overrides(
        "nasa_crm",
        {"mode": "samples", "values": []},
        {"samples": ["n"], "sample_selection": {"train": ["n"]}},
        {"samples": {"train": ["old"]}},
    )
    assert not any(item.startswith("dataset.partitions=") for item in nasa)
    assert "dataset.samples=" + json.dumps({"train": ["n"]}) in nasa
