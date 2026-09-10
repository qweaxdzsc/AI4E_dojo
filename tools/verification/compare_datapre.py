"""运行 datapre recipe 并逐样本对照官方实际处理器的七个训练字段。"""

import argparse
import hashlib
import importlib.util
import inspect
import json
import sys
from pathlib import Path

import torch
import yaml
from noether.data.datasets.cfd.shapenet_car.preprocessing import load_simulation_data
from omegaconf import OmegaConf
from recipe_config import configuration_module

from ai4e_contrib.application.datasets.shapenet_car import MANIFEST_PATH
from ai4e_core import run
from ai4e_core.abilities.data.source.manifest import ManifestIndex


def compare(raw_root: Path, output: Path, limit: int | None, manifest: Path | None = None):
    """默认完整官方分片；limit 仅用于差异定位，报告明确记录实际规模。"""
    output.mkdir(parents=True, exist_ok=True)
    if manifest is not None:
        index = ManifestIndex(manifest)
    else:
        recipe = Path(__file__).resolve().parents[2] / "recipes/aero_cfd"
        config = OmegaConf.load(recipe / "config.yaml")
        config.dataset.root = str(raw_root.resolve())
        parts = yaml.safe_load(MANIFEST_PATH.with_name("partition.yaml").read_text())
        config.dataset.partition = {key: parts[key][:limit] for key in ("train", "test")}
        config.data_root = str(output.resolve() / "data")
        config.run_root = str(output.resolve() / "runs")
        config.pipeline.stages = ["rawprep"]
        output.mkdir(parents=True, exist_ok=True)
        path = output / "config.yaml"
        OmegaConf.save(config, path)
        config = configuration_module(recipe / "config.yaml").load_configuration(path)
        sys.path.insert(0, str(recipe))
        spec = importlib.util.spec_from_file_location("reference_datapre", recipe / "rawprep.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        status = run.run_recipe(
            config,
            stages={"rawprep": module.rawprep},
            script=recipe / "rawprep.py",
        )
        if status:
            raise RuntimeError("datapre recipe 失败")
        index = ManifestIndex(Path(config.data_root) / "manifest.json")
    report = {
        "passed": False,
        "samples": 0,
        "failures": [],
        "max_abs": {},
        "reference_sha256": hashlib.sha256(
            Path(inspect.getfile(load_simulation_data)).read_bytes()
        ).hexdigest(),
    }
    for partition, names in index.partitions.items():
        for item, name in enumerate(names):
            pressure, position, normals, mask, vpos, velocity, sdf, vnormals = load_simulation_data(
                raw_root, Path(name)
            )
            expected = {
                "surface_pressure": torch.Tensor(pressure[mask]),
                "surface_position": torch.Tensor(position[mask]),
                "surface_normals": torch.Tensor(normals[mask]),
                "volume_position": torch.Tensor(vpos),
                "volume_velocity": torch.Tensor(velocity),
                "volume_sdf": torch.Tensor(sdf),
                "volume_normals": torch.Tensor(vnormals),
            }
            actual = index.read(partition, item)
            for field, value in actual.items():
                reference = expected[field]
                error = (
                    float((value - reference).abs().max())
                    if value.shape == reference.shape
                    else None
                )
                report["max_abs"][field] = max(error or 0, report["max_abs"].get(field, 0))
                if error is None or not torch.allclose(value, reference, rtol=1e-5, atol=1e-6):
                    report["failures"].append({"sample": name, "field": field, "max_abs": error})
            report["samples"] += 1
            if report["samples"] % 50 == 0:
                print(f"已对照 {report['samples']} 个样本", flush=True)
    report["passed"] = not report["failures"]
    report["full_official_split"] = report["samples"] == 889
    (output / "datapre.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report))
    if not report["passed"]:
        raise AssertionError("datapre 官方对照未通过，见报告")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--manifest", type=Path)
    args = parser.parse_args()
    compare(args.raw_root, args.output, args.limit, args.manifest)
