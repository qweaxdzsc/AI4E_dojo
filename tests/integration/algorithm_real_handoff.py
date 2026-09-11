"""显式本机真实四组合验收入口；不缩小模型，输出在调用者提供的目录。"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
NAMES = (
    "shapenet_car_abupt",
    "shapenet_car_transolver3_surface",
    "nasa_crm_abupt",
    "nasa_crm_transolver3",
)


def run(name: str, target: Path):
    """从真实来源重新提取分组字段，直接准备、正式网络短训及全点后处理。"""
    previous = yaml.safe_load(
        Path("/private/tmp/dojo-cross-model/examples", name, "config.yaml").read_text()
    )
    cfg = yaml.safe_load((ROOT / "examples/aero_cfd" / name / "config.yaml").read_text())
    cfg["dataset"] = previous["dataset"]
    if name.startswith("nasa"):
        from ai4e_contrib.application.datasets.nasa_crm.adapter import RawDataset

        raw = RawDataset(cfg["dataset"])
        cfg["dataset"]["samples"] = {
            split: values[:8] if split == "train" else values[:1]
            for split, values in raw.partitions.items()
        }
        cfg["post"]["samples"] = cfg["dataset"]["samples"]["test"]
        fields = [
            "surface_position",
            "surface_normals",
            "surface_cp",
            "surface_cf",
            "surface_area",
            "surface_ids",
            "conditions",
            "global_targets",
        ]
        members = [
            {
                "source_field": "surface/"
                + ("global" if field in {"conditions", "global_targets"} else "point")
                + "/"
                + field,
                "output_member": field,
            }
            for field in fields
        ]
        fmt = "zarr"
    else:
        from ai4e_contrib.application.datasets.shapenet_car.adapter import open_dataset

        data = open_dataset(
            **{k: cfg["dataset"][k] for k in ("root", "manifest", "samples", "partition")}
        )
        cfg["dataset"]["partition"] = {
            split: list(values[:1]) for split, values in data.partitions.items()
        }
        cfg["dataset"]["samples"] = "all"
        cfg["post"]["samples"] = cfg["dataset"]["partition"]["test"]
        members = [
            {"source_field": field, "output_member": field}
            for field in cfg["rawprep"]["save_fields"]
        ]
        fmt = "pt"
    cfg["rawprep"]["format"] = fmt
    cfg["rawprep"]["extraction"] = {
        "entries": [
            {
                "id": "physical",
                "name": "物理字段",
                "outputs": [
                    {"id": "first", "name": "first", "members": members[::2]},
                    {"id": "second", "name": "second", "members": members[1::2]},
                ],
            }
        ]
    }
    cfg["pipeline"]["stages"] = ["rawprep", "trainprep", "train", "post"]
    cfg["data_root"] = str(target / name / "data")
    cfg["run_root"] = str(target / name / "runs")
    cfg["paths"]["datasets"]["predictions"] = str(target / name / "predictions")
    cfg["train"]["device"] = "mps"
    cfg["train"]["max_epochs"] = 1
    cfg["train"]["snapshot"] = False
    case = target / name / "case"
    case.mkdir(parents=True, exist_ok=True)
    for script in (ROOT / "recipes/aero_cfd").glob("*.py"):
        shutil.copyfile(script, case / script.name)
    (case / "config.yaml").write_text(yaml.safe_dump(cfg, sort_keys=False))
    with (case / "console.log").open("w") as stream:
        result = subprocess.run(
            [sys.executable, str(case / "pipeline.py")],
            cwd=case,
            check=False,
            env={**os.environ, "OMP_NUM_THREADS": "1"},
            stdout=stream,
            stderr=subprocess.STDOUT,
        )
    if result.returncode:
        raise RuntimeError((case / "console.log").read_text()[-8000:])
    manifest = json.loads((target / name / "data/manifest.json").read_text())
    for sample in manifest["samples"]:
        if sample.get("source"):
            assert sample["source"]["sample"] == sample["sample"], sample
    runs = sorted((target / name / "runs").iterdir())
    report = {
        "name": name,
        "format": fmt,
        "config": str(case / "config.yaml"),
        "run": str(runs[-1]),
        "model_parameters": cfg["model"]["parameters"],
        "source": cfg["dataset"],
        "prediction": json.loads((runs[-1] / "artifacts/physical-predictions.json").read_text()),
    }
    (target / name / "result.json").write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(json.dumps({"name": name, "run": report["run"], "status": "succeeded"}), flush=True)


if __name__ == "__main__":
    run(sys.argv[1], Path(sys.argv[2]))
