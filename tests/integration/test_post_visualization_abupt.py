"""显式真实 AB-UPT 结果与原拓扑，覆盖完整脚本出图链。"""

import importlib.util
import json
import os
from pathlib import Path

import numpy as np
import pytest
from omegaconf import OmegaConf

from ai4e_core.applications.aero_cfd import post


def test_real_abupt_all_physical_outputs(tmp_path, monkeypatch):
    value = os.environ.get("DOJO_POST_REAL_MANIFEST")
    raw = os.environ.get("DOJO_POST_RAW_ROOT")
    if not value or not raw:
        pytest.skip("需要 DOJO_POST_REAL_MANIFEST 与 DOJO_POST_RAW_ROOT；跳过不算真实验收")
    from ai4e_contrib.application.datasets import shapenet_car

    sample = post.read_fields(value)
    config = {"dataset": {"root": raw}}
    sample["source_meshes"] = {
        domain: shapenet_car.comparison_mesh(
            config,
            sample["metadata"]["identity"]["sample"],
            domain,
            sample["fields"][declaration["position"]],
        )
        for domain, declaration in sample["metadata"]["domains"].items()
    }
    volume = post.bind_mesh(sample, domain="volume")
    bounds = np.array(volume.bounds).reshape(3, 2)
    center = bounds.mean(axis=1)
    seeds = volume.cell_centers().points[:: max(1, volume.n_cells // 8)][:8]
    speed = np.linalg.norm(volume["volume.velocity.prediction"], axis=1)
    start, end = center.copy(), center.copy()
    start[2], end[2] = bounds[2]
    cfg = OmegaConf.create(
        {
            "post": {
                "figures": [
                    "surface",
                    "slice",
                    "clip",
                    "vectors",
                    "streamlines",
                    "contour",
                    "profile",
                ],
                "image_size": [640, 480],
                "slice_origin": center.tolist(),
                "slice_normal": [0, 1, 0],
                "vector_stride": 100,
                "vector_scale": 0.02,
                "streamline_seeds": {"kind": "points", "points": seeds.tolist()},
                "streamline_length": 1.0,
                "contour_values": [float(np.median(speed))],
                "profile_start": start.tolist(),
                "profile_end": end.tolist(),
            }
        }
    )
    root = Path(__file__).resolve().parents[2]
    folder = root / "examples/aero_cfd/shapenet_car_abupt"
    monkeypatch.syspath_prepend(str(folder))
    spec = importlib.util.spec_from_file_location("post_real_example", folder / "post.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    row = module.analyze_sample(sample, cfg=cfg, output=tmp_path / "output")
    manifest = json.loads(Path(row["manifest"]).read_text())
    assert len([f for f in manifest["files"] if f["kind"] == "image"]) == 7
    assert len([f for f in manifest["files"] if f["kind"] == "mesh"]) == 7
    assert manifest["status"] == "succeeded"


def test_real_abupt_training_snapshots_and_resume(tmp_path):
    """真实车体两轮：训练输入、损失、权重、恢复与检查点不可用的独立 post。"""
    import shutil
    import subprocess
    import sys
    from textwrap import dedent

    import torch
    import yaml

    raw = os.environ.get("DOJO_POST_RAW_ROOT")
    if not raw:
        pytest.skip("需要 DOJO_POST_RAW_ROOT；跳过不算真实训练验收")
    root = Path(__file__).resolve().parents[2]
    out = tmp_path / "training"
    out.mkdir(parents=True, exist_ok=True)
    folder = out / "recipe"
    if not folder.exists():
        shutil.copytree(root / "examples/aero_cfd/shapenet_car_abupt", folder)
    cfg = yaml.safe_load((root / "examples/aero_cfd/shapenet_car_abupt/config.yaml").read_text())
    a = "param0/1641efa5c92514d86c4f4dbcda5f2fc0"
    b = "param0/1abeca7159db7ed9f200a72c9245aee7"
    cfg["dataset"].update(
        root=raw, partition={"train": [a], "test": [b], "eval": []}, samples="all"
    )
    cfg["data_root"] = str(out / "data")
    cfg["run_root"] = str(out / "raw-runs")
    cfg["train"].update(device="cpu", max_epochs=2, snapshot=False, test_repeat=1)
    cfg["model"]["parameters"].update(
        dim=24,
        geometry_depth=1,
        num_heads=3,
        blocks="psc",
        num_domain_decoder_blocks={"surface": 1, "volume": 1},
    )
    s = cfg["model"]["sampling"]
    s["geometry"]["max_points"] = 32
    s["supernodes"]["num_points"] = 8
    for domain in s["domains"].values():
        domain["anchor"]["num_points"] = 8
    cfg["post"].update(
        samples=[b],
        snapshot_sample=b,
        snapshot_split="test",
        image_size=[640, 480],
        figures=["surface", "slice"],
        slice_origin=[0.0, 0.0, 0.0],
        slice_normal=[0, 1, 0],
    )
    cfg["infer"].update(samples=[b], checkpoint="last", query_chunk_size=4096)

    def execute(entry, label):
        (folder / "config.yaml").write_text(yaml.safe_dump(cfg, sort_keys=False))
        r = subprocess.run(
            [sys.executable, "-B", str(folder / entry)],
            cwd=folder,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=600,
            check=False,
        )
        (out / (label + ".log")).write_text(r.stdout)
        if r.returncode:
            raise RuntimeError(r.stdout[-10000:])
        return next(Path(cfg["run_root"]).glob("*/checkpoints/last.pt"), None)

    execute("rawprep.py", "rawprep")
    (folder / "observed_pipeline.py").write_text(
        dedent("""
    from pipeline import pipeline
    from configuration import load_configuration
    from ai4e_core import run
    from ai4e_core.run import TrainingRun
    from pathlib import Path
    import shutil
    original = TrainingRun.checkpoint
    def checkpoint(self, label, payload):
        result = original(self, label, payload)
        if label == 'latest' and payload['epoch'] == 1:
            shutil.copyfile(result, Path(__file__).parent / 'epoch1.pt')
        return result
    TrainingRun.checkpoint = checkpoint
    raise SystemExit(run.launch(pipeline, script=__file__, config_loader=load_configuration))
    """)
    )
    checkpoints = []
    protocols = []
    runs = []
    histories = []
    for enabled in (False, True):
        cfg["pipeline"]["stages"] = ["trainprep", "train", "infer"]
        cfg["run_root"] = str(out / f"runs-{enabled}")
        cfg["post"]["snapshot_every"] = 1 if enabled else 0
        cfg["paths"]["datasets"]["post"] = str(out / f"post-{enabled}")
        cfg["paths"]["datasets"]["predictions"] = str(out / f"predictions-{enabled}")
        path = execute("observed_pipeline.py", f"train-{enabled}")
        checkpoints.append(torch.load(path, weights_only=False))
        run = path.parent.parent
        runs.append(str(run))
        histories.append(json.loads((run / "artifacts/training.json").read_text())["history"])
        protocols.append(json.loads((run / "artifacts/training-protocol.json").read_text()))
        if enabled:
            report = json.loads((run / "artifacts/training.json").read_text())
            assert [r["epoch"] for r in report["observations"]] == [1, 2]
            for row in report["observations"]:
                manifest = json.loads(Path(row["result"]["manifest"]).read_text())
                assert manifest["origin"]["epoch"] == row["epoch"]
                assert len([f for f in manifest["files"] if f["kind"] == "image"]) == 2
    for key in checkpoints[0]["model"]:
        torch.testing.assert_close(
            checkpoints[0]["model"][key], checkpoints[1]["model"][key], atol=0, rtol=0
        )
    assert protocols[0]["inputs"] == protocols[1]["inputs"]
    assert [r["loss"] for r in histories[0]] == [r["loss"] for r in histories[1]]
    cfg["train"]["resume"] = str(folder / "epoch1.pt")
    cfg["run_root"] = str(out / "resumed-runs")
    cfg["paths"]["datasets"]["post"] = str(out / "resumed-post")
    resumed = execute("train.py", "resumed")
    restored = torch.load(resumed, weights_only=False)
    for key in checkpoints[1]["model"]:
        torch.testing.assert_close(
            checkpoints[1]["model"][key], restored["model"][key], atol=0, rtol=0
        )
    cfg["train"]["resume"] = None
    # 固定结果再后处理；令检查点指向不存在的位置，证明不进入模型入口。
    cfg["post"].update(
        analysis_enabled=True,
        snapshot_every=0,
        results=str(Path(runs[1]) / "artifacts/physical-predictions.json"),
    )
    cfg["infer"]["checkpoint"] = str(out / "nonexistent-checkpoint.pt")
    cfg["run_root"] = str(out / "independent-runs")
    cfg["paths"]["datasets"]["post"] = str(out / "independent-post")
    execute("post.py", "independent-post")
    (out / "verification.json").write_text(
        json.dumps(
            {
                "status": "passed",
                "device": "cpu",
                "epochs": 2,
                "train_samples": [a],
                "snapshot_samples": [b],
                "runs": runs,
                "weights_equal": True,
                "losses_equal": True,
                "resume_equal": True,
                "inputs_equal": True,
                "independent_post_without_checkpoint": True,
            },
            indent=2,
        )
    )
    print("REAL TRAINING PASSED", out)
