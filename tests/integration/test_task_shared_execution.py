"""共享输出的真实子进程验收：目录、覆盖、取消、输入选择与发布。"""

import json
from pathlib import Path

import ai4e_task as task
import pytest
from omegaconf import OmegaConf

from tests.integration.test_task_management import recipe


def shared_recipe(tmp_path):
    source = recipe(tmp_path)
    cfg = OmegaConf.load(source / "config.yaml")
    cfg.dataset = {"processed_name": "sample_data"}
    cfg.components = {"application": "ai4e_contrib.application.aero_cfd.operations"}
    cfg.pipeline.stages = ["rawprep"]
    cfg.train = {"manifest": None, "snapshot": False}
    OmegaConf.save(cfg, source / "config.yaml")
    cfg.inputs = {"rawprep": {"source": cfg.inputs.test.dataset}, "trainprep": {"dataset": None}}
    cfg.pop("paths", None)
    cfg.data_root = "../data"
    OmegaConf.save(cfg, source / "config.yaml")
    (source / "pipeline.py").write_text("""from ai4e_core import run
from ai4e_core.base.config import load_config
from ai4e_core.run import TrainingRun
from pathlib import Path
import json,time

def rawprep(cfg):
    assert Path(cfg.inputs.rawprep.source).is_dir()
    time.sleep(float(cfg.delay))
    if cfg.fail: raise ValueError("requested failure")
    if TrainingRun().dry_run: return
    root = TrainingRun().output_dir("rawprep")
    root.mkdir(parents=True, exist_ok=True)
    (root / "field.bin").write_text(str(cfg.score))
    (root / "manifest.json").write_text(json.dumps({
        "version": 1, "state": "physical", "partitions": {"train": ["one"]},
        "samples": [{"partition": "train", "sample": "one", "written": True,
                     "path": str(root), "filemap": {"field": "field.bin"}}]}))
    cfg.inputs.trainprep.dataset = str(root / "manifest.json")

def prepare(cfg):
    m = json.loads(Path(cfg.inputs.trainprep.dataset).read_text())
    root = Path(m["samples"][0]["path"])
    if not root.is_absolute(): root = Path(cfg.inputs.trainprep.dataset).parent / root
    out = Path(cfg.data_root)
    out.mkdir(parents=True, exist_ok=True)
    (out / "prepared.txt").write_text((root / "field.bin").read_text())
    TrainingRun().report({"prepared": str(out / "prepared.txt")})

if __name__ == "__main__":
    raise SystemExit(run.launch({"rawprep": rawprep, "trainprep": prepare}, script=__file__, config_loader=load_config))
""")
    return source


def setup_shared(tmp_path):
    project = tmp_path / "project"
    task.create_project(project)
    source = shared_recipe(tmp_path)
    return project, task.new_task(project, "producer", source=source), source


def run_success(project, item, **kwargs):
    result = task.wait_run(project, task.submit_run(project, item["id"], **kwargs)["id"])
    assert result["status"] == "succeeded", result
    return result


def test_shared_output_and_private_preparation(tmp_path):
    project, item, _ = setup_shared(tmp_path)
    result = run_success(project, item, overrides=["pipeline.stages=[rawprep,trainprep]"])
    shared = task.get_shared_dataset(project, "sample_data")
    assert shared["status"] == "available"
    assert Path(shared["manifest_path"]).is_relative_to(project / "shared")
    assert (Path(result["data_dir"]) / "prepared.txt").read_text() == "2.0"
    assert not (Path(result["data_dir"]) / "manifest.json").exists()
    assert task.run_physical_manifest(project, result) == Path(shared["manifest_path"])


def test_second_task_prepares_without_raw_and_overwrite_refreshes(tmp_path):
    import shutil

    project, producer, source = setup_shared(tmp_path)
    consumer = task.new_task(project, "consumer", source=source)
    first = run_success(project, producer)
    current = task.read_configuration(project, consumer["id"])
    task.bind_shared_dataset(project, consumer["id"], "sample_data", revision=current["revision"])
    cfgpath = project / "tasks" / consumer["id"] / "recipe/config.yaml"
    previous = cfgpath.read_bytes()
    with pytest.raises(FileExistsError, match="shared_dataset_exists"):
        task.submit_run(project, producer["id"])
    run_success(project, producer, overwrite=True, overrides=["score=7"])
    assert cfgpath.read_bytes() == previous
    assert task.run_physical_manifest(project, first) is None
    shutil.rmtree(tmp_path / "raw")
    prepared = run_success(project, consumer, overrides=["pipeline.stages=[trainprep]"])
    assert (Path(prepared["data_dir"]) / "prepared.txt").read_text() == "7"


def test_trial_and_check_do_not_touch_formal(tmp_path):
    project, item, _ = setup_shared(tmp_path)
    run_success(project, item)
    before = task.get_shared_dataset(project, "sample_data")
    trial = run_success(project, item, operation_mode="trial")
    assert not trial["shared_outputs"]
    run_success(project, item, overrides=["execution.dry_run=true"])
    assert task.get_shared_dataset(project, "sample_data") == before


def test_failed_overwrite_unavailable_and_idempotency(tmp_path):
    project, item, _ = setup_shared(tmp_path)
    first = run_success(project, item, idempotency_key="same")
    assert task.submit_run(project, item["id"], idempotency_key="same")["id"] == first["id"]
    with pytest.raises(ValueError, match="idempotency_conflict"):
        task.submit_run(project, item["id"], idempotency_key="same", overwrite=True)
    failed = task.wait_run(
        project, task.submit_run(project, item["id"], overwrite=True, overrides=["fail=true"])["id"]
    )
    assert failed["status"] == "failed"
    assert task.get_shared_dataset(project, "sample_data")["status"] == "available"
    assert task.run_physical_manifest(project, first) is not None


def test_same_name_queued_producer_blocks_other(tmp_path):
    project, item, _ = setup_shared(tmp_path)
    queued = task.submit_run(project, item["id"], start=False)
    with pytest.raises(ValueError, match="shared_dataset_busy"):
        task.submit_run(project, item["id"], overwrite=True)
    task.stop_run(project, queued["id"])
    run_success(project, item)


@pytest.mark.parametrize(
    "override,exception",
    [("dataset.processed_name=null", ValueError), ("dataset.processed_name=../bad", ValueError)],
)
def test_invalid_name_rejected(tmp_path, override, exception):
    project, item, _ = setup_shared(tmp_path)
    with pytest.raises(exception):
        task.submit_run(project, item["id"], overrides=[override])


def test_submission_rechecks_name_and_launch_failure_releases_only_reservation(
    tmp_path, monkeypatch
):
    from ai4e_task.tasks import local

    project, item, _ = setup_shared(tmp_path)

    def fail(_):
        raise OSError("launch failed")

    original = local.start
    monkeypatch.setattr(local, "start", fail)
    failed = task.submit_run(project, item["id"])
    assert failed["status"] == "failed"
    assert task.get_run(project, failed["id"])["status"] == "failed"
    assert task.list_shared_datasets(project) == []
    monkeypatch.setattr(local, "start", original)
    run_success(project, item)


def test_stage_inputs_only_skip_earlier_producer():
    from ai4e_task.tasks.output_bindings import selected_inputs

    entry = {
        "stage_inputs": {
            "rawprep": [],
            "trainprep": [{"key": "train.manifest", "provided_by": "rawprep"}],
        }
    }
    assert selected_inputs(entry, ["rawprep", "trainprep"]) == []
    assert selected_inputs(entry, ["trainprep", "rawprep"]) == ["train.manifest"]


def test_unknown_placeholder_and_escape_rejected(tmp_path):
    from ai4e_task.tasks.output_bindings import allocate_outputs
    from ai4e_task.templates.materialize import read_entry

    project, item, _ = setup_shared(tmp_path)
    recipe = project / "tasks" / item["id"] / "recipe"
    entry = read_entry(recipe)
    cfg = OmegaConf.load(recipe / "config.yaml")
    for pattern, message in [
        ("{not_declared}", "unknown_output_placeholder"),
        ("{data_dir}/../../escape", "output_binding_escape"),
    ]:
        entry["outputs"]["paths.datasets.root"] = pattern
        with pytest.raises(ValueError, match=message):
            allocate_outputs(project, entry, cfg, project / "runs/r", project / "data/r",
                             operation_mode="trial", overwrite=False)
    assert task.list_runs(project) == []


def test_parallel_submissions_have_one_writer(tmp_path):
    from concurrent.futures import ThreadPoolExecutor

    project, item, _ = setup_shared(tmp_path)

    def submit(_):
        try:
            return task.submit_run(project, item["id"], start=False)
        except ValueError as exc:
            return str(exc)

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(submit, range(2)))
    assert sum(isinstance(v, dict) for v in results) == 1
    assert any(isinstance(v, str) and "shared_dataset_busy" in v for v in results)
    assert len(task.list_runs(project)) == 1
