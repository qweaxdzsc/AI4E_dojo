"""五个独立 example 显式使用共享物理步骤，允许来源局部差异。"""

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
NAMES = (
    "shapenet_car_abupt",
    "nasa_crm_transolver3",
    "nasa_crm_abupt",
    "shapenet_car_transolver3_surface",
    "shapenet_car_transolver3_volume",
)


def test_five_independent_examples():
    for name in NAMES:
        folder = ROOT / "examples/aero_cfd" / name
        config = yaml.safe_load((folder / "config.yaml").read_text())
        assert "workflow" not in config["components"]
        assert config["train"]["max_epochs"] == 1 and not config["train"]["evaluation_enabled"]
        assert (
            len(config["infer"]["samples"]) == 5 and config["inputs"]["infer"]["checkpoint"] is None
        )
        assert "instances" not in config["model"]
        for filename in ("rawprep.py", "trainprep.py", "train.py", "infer.py"):
            source = (folder / filename).read_text()
            assert "selected.workflow" not in source
            assert "load_components" in source
        assert "open_results" in (folder / "post.py").read_text()
        assert "legacy_predict" not in (folder / "post.py").read_text()
        # 共享交接与配置保持一致；领域步骤允许明确的来源/模型差异。
        for filename in ("configuration.py", "pipeline.py"):
            assert (ROOT / "recipes/aero_cfd" / filename).read_bytes() == (
                folder / filename
            ).read_bytes()
    nasa = yaml.safe_load((ROOT / "examples/aero_cfd/nasa_crm_abupt/config.yaml").read_text())
    assert "c" not in nasa["model"]["parameters"]["blocks"]


def test_copied_generic_pipeline_and_independent_post(tmp_path):
    """NASA 物理 PT 的真实五阶段入口，独立 post 使用同一固定结果。"""
    import json
    import os
    import shutil
    import subprocess
    import sys

    from tests.transolver_assets import write_source

    folder = tmp_path / "copied"
    shutil.copytree(ROOT / "examples/aero_cfd/nasa_crm_transolver3", folder)
    raw = tmp_path / "raw"
    raw.mkdir()
    write_source(raw / "train.h5", 5, 80, offset=0)
    write_source(raw / "test.h5", 2, 80, offset=100)
    config = yaml.safe_load((folder / "config.yaml").read_text())
    config["inputs"]["rawprep"].update(
        source=str(raw), train_h5=str(raw / "train.h5"), test_h5=str(raw / "test.h5")
    )
    config["inputs"]["trainprep"]["dataset"] = None
    config["data_root"] = str(tmp_path / "data")
    config["run_root"] = str(tmp_path / "runs")
    config["pipeline"]["stages"] = ["rawprep", "trainprep", "train", "infer", "post"]
    config["model"]["parameters"].update(n_hidden=16, n_layers=2, n_head=4, slice_num=4)
    config["train"].update(device="cpu")
    config["infer"]["export_vtk"] = False  # 合成 HDF5 不提供真实拓扑。
    config["infer"]["samples"] = ["Sample001", "Sample002"]
    config["model"]["sampling"]["chunk_count"] = 4
    (folder / "config.yaml").write_text(yaml.safe_dump(config, sort_keys=False))
    result = subprocess.run(
        [sys.executable, str(folder / "pipeline.py")],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        env={**os.environ, "OMP_NUM_THREADS": "1"},
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    run = next((tmp_path / "runs").iterdir())
    report = json.loads((run / "artifacts/physical-predictions.json").read_text())
    assert report["metrics"]["surface.cp"]["count"] == 160
    assert len(report["results"]) == 2
    assert not list(tmp_path.rglob("*.vtp")) and not list(tmp_path.rglob("*.vtu"))
    # 固定结果已交付，即使权重不再存在，独立 post 仍应可读且不生成预测。
    (run / "checkpoints/last.pt").unlink()
    result = subprocess.run(
        [
            sys.executable,
            str(folder / "post.py"),
            "--set",
            "inputs.post.results=" + str(run / "artifacts/physical-predictions.json"),
            "--set",
            "data_root=" + str(tmp_path / "other_predictions"),
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        env={**os.environ, "OMP_NUM_THREADS": "1"},
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert not (tmp_path / "other_predictions").exists()
