"""调用锁定 Noether user_project 的真实后处理入口，仅用于离线验收。"""

import argparse
import importlib.util
from copy import deepcopy
from functools import partial
from pathlib import Path

import torch
from noether.core.utils.seed import set_seed
from recipe_config import read_experiment


def main():
    """保留参考算法，允许配对用户实验的设备、种子和采样参数。"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--reference-root", type=Path, required=True)
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--raw-root", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--run-id", default="reference")
    parser.add_argument("--mode", choices=["anchors", "mesh"], required=True)
    parser.add_argument("--experiment", type=Path)
    args = parser.parse_args()
    user, sampling = read_experiment(args.experiment)
    seed = sampling.get("seed", 42)
    filename = "infer_shapenet_car.py" if args.mode == "anchors" else "post_vtk_shapenet_car.py"
    path = args.reference_root / "recipes/aero_cfd/user_project" / filename
    spec = importlib.util.spec_from_file_location("reference_post", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    original = module.ShapeNetCarPreset

    class SingleProcessPreset(original):
        def __init__(self):
            super().__init__()
            if sampling:
                self.pipeline_model_overrides = deepcopy(self.pipeline_model_overrides)
                self.pipeline_model_overrides[
                    "noether.modeling.models.aerodynamics.AeroABUPT"
                ].update(
                    num_geometry_supernodes=sampling["supernodes"]["num_points"],
                    num_surface_anchor_points=sampling["domains"]["surface"]["anchor"][
                        "num_points"
                    ],
                    num_volume_anchor_points=sampling["domains"]["volume"]["anchor"]["num_points"],
                )

        def build_config(self, **kwargs):
            kwargs["seed"] = seed
            config = super().build_config(**kwargs)
            config.num_workers = 0
            return config

    module.ShapeNetCarPreset = SingleProcessPreset
    set_seed(seed)
    torch.set_num_threads(1)
    common = {
        "dataset_root": args.dataset,
        "output_path": args.output,
        "run_id": args.run_id,
        "accelerator": user.get("train", {}).get("device", "cpu"),
        "resume_checkpoint": "last",
    }
    if args.mode == "anchors":
        module.infer_shapenet_car(**common, export_vtk=True)
    else:
        module.chunked_query_inference = partial(
            module.chunked_query_inference,
            chunk_size=user.get("post", {}).get("query_chunk_size", 16384),
        )
        module.post_vtk_shapenet_car(
            **common,
            raw_root=args.raw_root,
            sample_indices=user.get("post", {}).get("sample_indices", [0]),
        )


if __name__ == "__main__":
    main()
