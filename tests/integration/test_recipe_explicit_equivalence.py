"""五例与改动前训练/完整预测源码对照：同输入、权重、更新及恢复。"""

import json
import shutil
from pathlib import Path

import pytest
import torch
import yaml

from tests.integration.test_cross_model_recipe import NAMES
from tests.integration.test_dataset_recipe import setup_case
from tests.integration.test_recipe_extensions import ROOT, script
from tests.transolver_assets import write_connectivity, write_source


def case(tmp_path, name):
    folder = tmp_path / "case"
    if name.startswith("shapenet"):
        fixture, _ = setup_case(tmp_path / "fixture")
        source = yaml.safe_load((fixture / "config.yaml").read_text())["inputs"]["rawprep"]
    else:
        raw = tmp_path / "raw"
        raw.mkdir()
        write_source(raw / "train.h5", 5, 33, offset=0)
        # AB-UPT 绝对位置编码要求坐标在所声明的训练坐标范围内。
        write_source(raw / "test.h5", 2, 33, offset=0)
        write_connectivity(raw / "connectivity.h5", 33)
        source = {
            "connectivity_h5": str(raw / "connectivity.h5"),
            "root": str(raw),
            "train_h5": str(raw / "train.h5"),
            "test_h5": str(raw / "test.h5"),
        }
    shutil.copytree(ROOT / "examples/aero_cfd" / name, folder)
    cfg = yaml.safe_load((folder / "config.yaml").read_text())
    if name.startswith("shapenet"):
        cfg["dataset"]["partitions"] = {"train": ["a"], "test": ["b"]}
    cfg["inputs"]["rawprep"].update({("source" if k == "root" else k): v for k, v in source.items()})
    cfg["data_root"] = str(tmp_path / "data")
    cfg["run_root"] = str(tmp_path / "data-runs")
    cfg["pipeline"]["stages"] = ["rawprep"]
    cfg["train"].update(device="cpu", max_epochs=2, snapshot=False)
    if "abupt" in name:
        cfg["model"]["parameters"].update(
            dim=24,
            geometry_depth=1,
            num_heads=3,
            blocks="psc" if name.startswith("shapenet") else "ps",
            num_domain_decoder_blocks={key: 1 for key in cfg["trainprep"]["domains"]},
        )
        sample = cfg["model"]["sampling"]
        sample["geometry"]["max_points"] = 4
        sample["supernodes"]["num_points"] = 2
        for domain in sample["domains"].values():
            domain["anchor"]["num_points"] = 2
    else:
        cfg["model"]["parameters"].update(n_hidden=16, n_layers=2, n_head=4, slice_num=4)
        cfg["model"]["sampling"].update(chunk_count=1, stride=4)
    cfg["infer"].update(
        device="cpu",
        samples=["b"] if name.startswith("shapenet") else ["Sample001", "Sample002"],
        export_vtk=False,
    )
    (folder / "config.yaml").write_text(yaml.safe_dump(cfg, sort_keys=False))
    result = script(folder, "rawprep.py")
    assert result.returncode == 0, result.stdout + result.stderr
    summary = json.loads(max((tmp_path / "data-runs").glob("*/summary.json"), key=lambda p: p.stat().st_mtime_ns).read_text())
    cfg["inputs"]["trainprep"]["dataset"] = summary["reports"]["rawprep"]["manifest"]
    return folder, cfg


@pytest.mark.parametrize("name", NAMES)
def test_five_examples_match_frozen_workflow_and_resume(tmp_path, name):
    folder, config = case(tmp_path, name)
    baseline = ROOT / "tests/fixtures/recipe_before_explicit"
    shutil.copyfile(baseline / "physical_workflow.py", folder / "baseline_workflow.py")
    shutil.copyfile(baseline / "physical_post.py", folder / "baseline_post.py")
    shutil.copyfile(ROOT / "tests/reference_preparation_adapter.py", folder / "reference_preparation_adapter.py")
    runner = """from configuration import load_configuration, application_parameters, load_components
from ai4e_core import run
from ai4e_core.run.training import TrainingRun
from omegaconf import OmegaConf
import baseline_workflow, baseline_post
from reference_preparation_adapter import execute_reference, reference_loader_state
import shutil
from pathlib import Path
save_loader_state = reference_loader_state(baseline_workflow, Path(__file__).parent.parent / "baseline-epoch1.pt")
original = TrainingRun.checkpoint
def checkpoint(self, label, payload):
    result = original(self, label, payload)
    if label == "latest" and payload["epoch"] == 1:
        shutil.copyfile(result, Path(__file__).parent.parent / "baseline-epoch1.pt")
        save_loader_state()
    return result
TrainingRun.checkpoint = checkpoint

def pipeline(cfg):
    component = load_components(cfg)
    values = OmegaConf.create(application_parameters(cfg))
    values.post.update(values.infer)
    session = TrainingRun()
    common = dict(dataset_component=component.dataset, model_component=component.model, session=session)
    prepared = run.stage("trainprep", lambda _: baseline_workflow.trainprep(values, **common), cfg)
    trained = run.stage("train", lambda _: baseline_workflow.train(values, prepared, **common), cfg)
    values.post.checkpoint = trained["checkpoints"]["last"]
    return run.stage("post", lambda _: execute_reference(baseline_post, OmegaConf.to_container(values, resolve=True), component.dataset, component.model, session, anchors="abupt" in component.model.__name__), cfg)
if __name__ == "__main__":
    raise SystemExit(run.launch(pipeline, script=__file__, config_loader=load_configuration))
"""
    (folder / "baseline.py").write_text(runner)
    config["pipeline"]["stages"] = ["trainprep", "train", "post"]
    explicit_runner = r'''from configuration import load_configuration
from pipeline import pipeline
from ai4e_core import run
from ai4e_core.run import TrainingRun
from ai4e_core.applications.aero_cfd.train import fitting
from ai4e_core.abilities.data.validate.fingerprint import fingerprint
from pathlib import Path
import shutil
checkpoint = TrainingRun.checkpoint
def capture(self, label, payload):
    result = checkpoint(self, label, payload)
    if label == "latest" and payload["epoch"] == 1:
        shutil.copyfile(result, Path(__file__).parent.parent / "explicit-epoch1.pt")
    return result
TrainingRun.checkpoint = capture
execute = fitting.execute_training
def traced(job):
    inputs = []
    original = job.execution["step"]
    def step(network, batch):
        inputs.append({"identity": [{k:v for k,v in item.items() if k in {"sample", "partition", "index", "chunk", "offset"}} for item in batch["metadata"]], "digest": fingerprint({"inputs": batch["inputs"], "targets": batch["targets"]})})
        return original(network, batch)
    job.execution["step"] = step
    result = execute(job)
    job.run.artifact("training-inputs-test.json", inputs)
    return result
fitting.execute_training = traced
raise SystemExit(run.launch(pipeline, script=__file__, config_loader=load_configuration))
'''
    (folder / "explicit.py").write_text(explicit_runner)
    directories = []
    for mode in ("baseline", "explicit"):
        config["pipeline"]["stages"] = (
            ["trainprep", "train", "post"]
            if mode == "baseline"
            else ["trainprep", "train", "infer", "post"]
        )
        config["infer"]["device"] = "cpu"
        config["run_root"] = str(tmp_path / (mode + "-runs"))
        config["data_root"] = str(tmp_path / (mode + "-data"))
        (folder / "config.yaml").write_text(yaml.safe_dump(config, sort_keys=False))
        result = script(folder, "baseline.py" if mode == "baseline" else "explicit.py")
        assert result.returncode == 0, result.stdout + result.stderr
        directories.append(next(Path(config["run_root"]).iterdir()))
    left, right = [
        torch.load(path / "checkpoints/last.pt", weights_only=False) for path in directories
    ]
    assert left["updates"] == right["updates"] and left["epoch"] == right["epoch"] == 2
    for key in left["model"]:
        torch.testing.assert_close(left["model"][key], right["model"][key], rtol=0, atol=0)
    protocols = [
        json.loads((path / "artifacts/training-protocol.json").read_text()) for path in directories
    ]
    actual_inputs = (json.loads((directories[1] / "artifacts/training-inputs-test.json").read_text())
                     if "abupt" in name else protocols[1]["inputs"])
    assert protocols[0]["inputs"] == actual_inputs
    assert protocols[0]["initialization"] == protocols[1]["initialization"]
    a, b = [
        json.loads((path / "artifacts/physical-predictions.json").read_text())
        for path in directories
    ]
    assert a["metrics"] == b["metrics"]
    for original, actual in zip(a["results"], b["results"], strict=True):
        p, q = Path(original["manifest"]), Path(actual["manifest"])
        pm, qm = json.loads(p.read_text()), json.loads(q.read_text())
        if "abupt" in name:
            for domain in qm["domains"].values():
                domain.setdefault("coordinate_space", None)
        assert pm["domains"] == qm["domains"]
        for key in pm["filemap"]:
            torch.testing.assert_close(
                torch.load(p.parent / pm["filemap"][key], weights_only=True),
                torch.load(q.parent / qm["filemap"][key], weights_only=True),
                rtol=0,
                atol=0,
            )
    # 分别保留两侧原契约。先证实中途权重相等，再用现行链自身的完整状态恢复。
    mid_reference = torch.load(tmp_path / "baseline-epoch1.pt", weights_only=False)
    mid_actual = torch.load(tmp_path / "explicit-epoch1.pt", weights_only=False)
    assert mid_reference["updates"] == mid_actual["updates"]
    for key in mid_reference["model"]:
        torch.testing.assert_close(mid_reference["model"][key], mid_actual["model"][key], rtol=0, atol=0)
    config["inputs"]["train"]["resume"] = str(tmp_path / "explicit-epoch1.pt")
    config["inputs"]["train"]["preparation"] = str(directories[1] / "artifacts/preparation.json")
    config["run_root"] = str(tmp_path / "resumed-runs")
    (folder / "config.yaml").write_text(yaml.safe_dump(config, sort_keys=False))
    result = script(folder, "train.py")
    assert result.returncode == 0, result.stdout + result.stderr
    resumed = torch.load(
        next(Path(config["run_root"]).glob("*/checkpoints/last.pt")), weights_only=False
    )
    for key in right["model"]:
        torch.testing.assert_close(right["model"][key], resumed["model"][key], rtol=0, atol=0)
    # 冻结参考也从自己的原始中途状态恢复，继续独立核验优化器和随机流。
    # 不把旧 physical contract 改写成当前 anchor contract。
    (folder / "baseline_resume.py").write_text('''from configuration import load_configuration, application_parameters, load_components
from ai4e_core import run
from ai4e_core.run import TrainingRun
from omegaconf import OmegaConf
import baseline_workflow
from reference_preparation_adapter import reference_loader_state
def resume(cfg):
    components = load_components(cfg)
    reference_loader_state(baseline_workflow, cfg.inputs.train.resume, restore=True)
    return baseline_workflow.train(OmegaConf.create(application_parameters(cfg)), dataset_component=components.dataset, model_component=components.model, session=TrainingRun())
raise SystemExit(run.launch({"train": resume}, script=__file__, config_loader=load_configuration))
''')
    config["pipeline"]["stages"] = ["train"]
    config["inputs"]["train"]["resume"] = str(tmp_path / "baseline-epoch1.pt")
    config["inputs"]["train"]["preparation"] = str(directories[0] / "artifacts/preparation.json")
    config["run_root"] = str(tmp_path / "reference-resumed-runs")
    (folder / "config.yaml").write_text(yaml.safe_dump(config, sort_keys=False))
    result = script(folder, "baseline_resume.py")
    assert result.returncode == 0, result.stdout + result.stderr
    reference_resumed = torch.load(
        next(Path(config["run_root"]).glob("*/checkpoints/last.pt")), weights_only=False
    )
    assert reference_resumed["updates"] == resumed["updates"]
    for key in resumed["model"]:
        torch.testing.assert_close(
            reference_resumed["model"][key], resumed["model"][key], rtol=0, atol=0
        )
