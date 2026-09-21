"""同一案例目录交给 Task Python API 的入口和显式 smoke。"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import ai4e_task as task
import pytest
import yaml


def test_task_api_accepts_copied_case(tmp_path):
    source = Path(__file__).resolve().parents[2] / "examples/parametric_pde/neumann_diffusion"
    project = tmp_path / "project"
    task.create_project(project)
    record = task.new_task(project, "neumann", source=source)
    assert record["id"]
    assert (project / "tasks" / record["id"] / "recipe" / "pipeline.py").is_file()


@pytest.mark.skipif(not os.environ.get("DOJO_EXAMPLE_SMOKE"), reason="显式开启 Neumann Task smoke")
def test_neumann_task_smoke_and_resume(tmp_path):
    """固定 preparation 后经 Task 完成训练、恢复、推理和独立 post。"""
    source = Path(__file__).resolve().parents[2] / "examples/parametric_pde/neumann_diffusion"
    case = tmp_path / "neumann"
    shutil.copytree(source, case)
    data = tmp_path / "input-data"
    generate = yaml.safe_load((case / "generate.yaml").read_text())
    generate.update(train=2, test=1, nx=7, nt=7, output=str(data))
    (case / "generate.yaml").write_text(yaml.safe_dump(generate, sort_keys=False))
    produced = subprocess.run(
        [sys.executable, str(case / "generate.py"), "--config", str(case / "generate.yaml")],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert produced.returncode == 0, produced.stdout + produced.stderr

    manifest = str(data / "manifest.json")
    config = yaml.safe_load((case / "config.yaml").read_text())
    config["run_root"] = str(tmp_path / "case-runs")
    config["data_root"] = str(tmp_path / "case-data")
    config["pipeline"]["stages"] = ["rawprep", "trainprep"]
    config["train"]["max_epochs"] = 2
    # 极小正学习率让两轮评价严格相同，best.pt 稳定保留在第一轮，
    # 从而可用已成功运行的早期检查点验证 Task 恢复到第二轮。
    config["train"]["learning_rate"] = 1e-30
    config["train"]["evaluation"] = {"enabled": True, "interval": 1}
    for stage in ("rawprep", "trainprep", "train", "infer"):
        key = "manifest" if stage == "rawprep" else "dataset"
        config["inputs"][stage][key] = manifest
    (case / "config.yaml").write_text(yaml.safe_dump(config, sort_keys=False))

    project = tmp_path / "project"
    task.create_project(project)
    record = task.new_task(project, "neumann-smoke", source=case)

    prepared = task.submit_run(project, record["id"])
    prepared = task.wait_run(project, prepared["id"], timeout=120)
    assert prepared["status"] == "succeeded", task.read_log(project, prepared["id"])
    preparation = Path(prepared["summary"]["reports"]["trainprep"]["path"])
    assert preparation.is_file()

    current = task.read_configuration(project, record["id"])
    train_config = current["config"]
    train_config["pipeline"]["stages"] = ["train"]
    train_config["inputs"]["train"].update(
        dataset=manifest,
        preparation=str(preparation),
        resume=None,
    )
    task.replace_configuration(
        project,
        record["id"],
        train_config,
        revision=current["revision"],
    )
    trained = task.submit_run(project, record["id"])
    trained = task.wait_run(project, trained["id"], timeout=120)
    assert trained["status"] == "succeeded", task.read_log(project, trained["id"])
    assert trained["summary"]["failed"] is False
    assert set(trained["summary"]["reports"]) == {"train"}
    for name in ("latest.pt", "best.pt", "last.pt"):
        assert Path(trained["run_dir"], "checkpoints", name).is_file()

    resumed = task.resume_run(project, trained["id"], checkpoint="best.pt")
    resumed = task.wait_run(project, resumed["id"], timeout=120)
    assert resumed["status"] == "succeeded", task.read_log(project, resumed["id"])
    assert resumed["summary"]["failed"] is False
    assert resumed["lineage"]["resumed_from"] == trained["id"]
    assert set(resumed["summary"]["reports"]) == {"train"}
    resumed_config = yaml.safe_load(Path(resumed["run_dir"], "inputs/config.yaml").read_text())
    assert resumed_config["inputs"]["train"]["preparation"] == str(preparation)
    assert resumed_config["inputs"]["train"]["resume"] == str(
        Path(trained["run_dir"], "checkpoints/best.pt")
    )

    current = task.read_configuration(project, record["id"])
    infer_config = current["config"]
    infer_config["pipeline"]["stages"] = ["infer"]
    infer_config["inputs"]["infer"].update(
        dataset=manifest,
        preparation=str(preparation),
        checkpoint=str(Path(resumed["run_dir"], "checkpoints/last.pt")),
    )
    task.replace_configuration(
        project,
        record["id"],
        infer_config,
        revision=current["revision"],
    )
    inferred = task.submit_run(project, record["id"])
    inferred = task.wait_run(project, inferred["id"], timeout=120)
    assert inferred["status"] == "succeeded", task.read_log(project, inferred["id"])
    assert inferred["summary"]["reports"]["infer"]["status"] == "complete"
    results = Path(inferred["data_dir"], "infer/results/predictions.json")
    prediction_manifest = json.loads(results.read_text())
    assert prediction_manifest["status"] == "complete"
    assert len(prediction_manifest["samples"]) == 1
    assert (results.parent / f"{prediction_manifest['samples'][0]['id']}.pt").is_file()

    current = task.read_configuration(project, record["id"])
    post_config = current["config"]
    post_config["pipeline"]["stages"] = ["post"]
    post_config["inputs"]["post"]["results"] = str(results)
    task.replace_configuration(
        project,
        record["id"],
        post_config,
        revision=current["revision"],
    )
    posted = task.submit_run(project, record["id"])
    posted = task.wait_run(project, posted["id"], timeout=120)
    assert posted["status"] == "succeeded", task.read_log(project, posted["id"])
    metrics = Path(posted["data_dir"], "post/metrics.json")
    assert metrics.is_file()
    assert json.loads(metrics.read_text())["status"] == "complete"
