"""MeshGraphNet Recipe 的直接完整小样本交接。"""

import json
import shutil
import subprocess
from pathlib import Path

import ai4e_task as task
import torch
import yaml
from ai4e_task.tasks.assets import validate_asset

ROOT = Path(__file__).resolve().parents[2]


def test_meshgraphnet_pipeline_direct_and_fixed_post(tmp_path):
    raw = tmp_path / "raw.pt"
    position = torch.tensor([[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]])
    cells = torch.tensor([[0, 1, 2], [0, 2, 3]])
    samples = []
    for offset in (0.0, 0.1):
        velocity = torch.full((4, 2), offset)
        samples.append(
            {
                "position": position,
                "cells": cells,
                "velocity": torch.stack([velocity + step * 0.05 for step in range(5)]),
                "node_type": torch.tensor([0, 1, 5, 2]),
            }
        )
    torch.save({"train": samples, "test": samples[:1]}, raw)
    config = yaml.safe_load((ROOT / "recipes/meshgraphnet/config.yaml").read_text())
    config.update(run_root=str(tmp_path / "runs"), data_root=str(tmp_path / "data"))
    config["inputs"]["rawprep"]["source"] = str(raw)
    config["model"].update(hidden_dim=16, processor_layers=1)
    config["train"].update(
        updates=1, batch_size=1, normalizer_warmup=0, noise_std=0.0, device="cpu"
    )
    config["infer"]["steps"] = 2
    path = tmp_path / "config.yaml"
    path.write_text(yaml.safe_dump(config, sort_keys=False))
    result = subprocess.run(
        [
            "uv",
            "run",
            "--no-sync",
            "python",
            str(ROOT / "recipes/meshgraphnet/pipeline.py"),
            "--config",
            str(path),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    summaries = list((tmp_path / "runs").glob("*/summary.json"))
    assert len(summaries) == 1
    summary = json.loads(summaries[0].read_text())
    assert summary["research_status"] == "completed"
    assert summary["reports"]["train"]["updates"] == 1
    assert summary["reports"]["post"]["samples"] == 1
    assert "mse_1_steps" in summary["reports"]["post"]["metrics"]
    infer_manifest = json.loads(Path(summary["reports"]["infer"]["manifest"]).read_text())
    fixed = torch.load(infer_manifest["bundle"], map_location="cpu", weights_only=True)
    assert fixed["samples"][0]["prediction"].shape == (3, 4, 2)
    assert torch.equal(fixed["samples"][0]["target"][0], samples[0]["velocity"][1])

    config["pipeline"]["stages"] = ["infer"]
    config["inputs"]["infer"]["preparation"] = summary["reports"]["trainprep"]["manifest"]
    config["inputs"]["infer"]["checkpoint"] = summary["reports"]["train"]["checkpoint"]
    path.write_text(yaml.safe_dump(config, sort_keys=False))
    inferred = subprocess.run(
        [
            "uv",
            "run",
            "--no-sync",
            "python",
            str(ROOT / "recipes/meshgraphnet/pipeline.py"),
            "--config",
            str(path),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    assert inferred.returncode == 0, inferred.stdout + inferred.stderr
    infer_summary_path = max(
        (tmp_path / "runs").glob("*/summary.json"), key=lambda item: item.stat().st_mtime_ns
    )
    infer_summary = json.loads(infer_summary_path.read_text())
    config["pipeline"]["stages"] = ["post"]
    config["inputs"]["post"]["results"] = infer_summary["reports"]["infer"]["manifest"]
    path.write_text(yaml.safe_dump(config, sort_keys=False))
    posted = subprocess.run(
        [
            "uv",
            "run",
            "--no-sync",
            "python",
            str(ROOT / "recipes/meshgraphnet/pipeline.py"),
            "--config",
            str(path),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    assert posted.returncode == 0, posted.stdout + posted.stderr
    post_summary_path = max(
        (tmp_path / "runs").glob("*/summary.json"), key=lambda item: item.stat().st_mtime_ns
    )
    assert "post" in json.loads(post_summary_path.read_text())["reports"]


def test_meshgraphnet_recipe_task_reuses_same_pipeline(tmp_path):
    source = tmp_path / "recipe"
    shutil.copytree(ROOT / "recipes/meshgraphnet", source)
    raw = tmp_path / "raw.pt"
    position = torch.tensor([[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]])
    sample = {
        "position": position,
        "cells": torch.tensor([[0, 1, 2], [0, 2, 3]]),
        "velocity": torch.zeros(4, 2),
        "target_velocity": torch.ones(4, 2) * 0.01,
        "node_type": torch.tensor([0, 1, 5, 2]),
        "target_trajectory": torch.zeros(2, 4, 2),
    }
    torch.save({"train": [sample], "test": [sample]}, raw)
    config = yaml.safe_load((source / "config.yaml").read_text())
    config["run_root"] = str(tmp_path / "runs")
    config["data_root"] = str(tmp_path / "data")
    config["inputs"]["rawprep"]["source"] = str(raw)
    config["model"].update(hidden_dim=8, processor_layers=1)
    config["train"].update(
        updates=1, batch_size=1, normalizer_warmup=0, noise_std=0.0, device="cpu"
    )
    config["infer"]["steps"] = 1
    (source / "config.yaml").write_text(yaml.safe_dump(config, sort_keys=False))
    project = tmp_path / "project"
    task.create_project(project)
    item = task.new_task(project, "meshgraphnet", source=source)
    run = task.wait_run(project, task.submit_run(project, item["id"])["id"], timeout=120)
    assert run["status"] == "succeeded", run
    assert run["summary"]["reports"]["post"]["samples"] == 1
    child = task.fork_task(project, item["id"], copy_checkpoints=True)
    checkpoints = [
        asset for asset in child["copied_outputs"].values() if asset["kind"] == "checkpoint"
    ]
    assert len(checkpoints) == 1 and not checkpoints[0]["external"]
    copied = validate_asset(project, checkpoints[0])
    original = Path(run["summary"]["reports"]["train"]["checkpoint"])
    assert copied.read_bytes() == original.read_bytes()


def test_meshgraphnet_training_resume_preserves_receipt(tmp_path):
    raw = tmp_path / "raw.pt"
    position = torch.tensor([[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]])
    velocity = torch.stack([torch.full((4, 2), step * 0.01) for step in range(4)])
    trajectory = {
        "position": position,
        "cells": torch.tensor([[0, 1, 2], [0, 2, 3]]),
        "velocity": velocity,
        "node_type": torch.tensor([0, 1, 5, 6]),
        "sample_id": "train/000000",
    }
    torch.save({"train": [trajectory], "test": [trajectory]}, raw)
    config = yaml.safe_load((ROOT / "recipes/meshgraphnet/config.yaml").read_text())
    config.update(run_root=str(tmp_path / "runs"), data_root=str(tmp_path / "data"))
    config["pipeline"]["stages"] = ["rawprep", "trainprep", "train"]
    config["inputs"]["rawprep"]["source"] = str(raw)
    config["model"].update(hidden_dim=8, processor_layers=1)
    config["train"].update(
        updates=1, batch_size=1, normalizer_warmup=0, noise_std=0.0, device="cpu"
    )
    path = tmp_path / "config.yaml"
    path.write_text(yaml.safe_dump(config, sort_keys=False))

    def execute():
        result = subprocess.run(
            [
                "uv",
                "run",
                "--no-sync",
                "python",
                str(ROOT / "recipes/meshgraphnet/pipeline.py"),
                "--config",
                str(path),
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        summaries = sorted((tmp_path / "runs").glob("*/summary.json"))
        return json.loads(summaries[-1].read_text())

    first = execute()
    checkpoint = first["reports"]["train"]["checkpoint"]
    assert "step-00000001/last.pt" in checkpoint
    config["pipeline"]["stages"] = ["train"]
    config["inputs"]["train"]["preparation"] = first["reports"]["trainprep"]["manifest"]
    config["train"]["updates"] = 2
    config["inputs"]["train"]["resume"] = checkpoint
    path.write_text(yaml.safe_dump(config, sort_keys=False))
    resumed = execute()
    assert resumed["reports"]["train"]["updates"] == 2
    assert resumed["reports"]["train"]["losses"][:1] == first["reports"]["train"]["losses"]
