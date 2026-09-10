"""官方 ShapeNet-Car 完整训练入口；仅在验收环境导入 Noether。"""

import argparse
from pathlib import Path

import torch
from aero_cfd.presets import ShapeNetCarPreset
from noether.training.runners import HydraRunner
from recipe_config import read_experiment


def train(dataset: Path, output: Path, run_id: str, experiment: Path | None = None):
    """保留正式模型；可从用户复制的 recipe 读取配对实验参数。"""
    user, sampling = read_experiment(experiment)
    training = user.get("train", {})
    device = training.get("device", "cpu")
    preset = ShapeNetCarPreset()
    if sampling:
        from copy import deepcopy

        preset.pipeline_model_overrides = deepcopy(preset.pipeline_model_overrides)
        preset.pipeline_model_overrides["noether.modeling.models.aerodynamics.AeroABUPT"].update(
            num_geometry_supernodes=sampling["supernodes"]["num_points"],
            num_surface_anchor_points=sampling["domains"]["surface"]["anchor"]["num_points"],
            num_volume_anchor_points=sampling["domains"]["volume"]["anchor"]["num_points"],
        )
    config = preset.build_config(
        model_kind="noether.modeling.models.aerodynamics.AeroABUPT",
        model_params={
            "hidden_dim": 192,
            "geometry_depth": 6,
            "physics_blocks": ["perceiver"] + ["shared", "cross"] * 5,
        },
        trainer_kind="noether.training.trainers.WeightedLossTrainer",
        trainer_params={"field_weights": {"surface_pressure": 1.0, "volume_velocity": 1.0}},
        dataset_root=str(dataset),
        output_path=str(output),
        optimizer=preset.build_optimizer(
            lr=training.get("learning_rate", 5e-5),
            weight_decay=training.get("weight_decay", 0.05),
        ),
        seed=sampling.get("seed", 42),
        max_epochs=training.get("max_epochs", 2),
        batch_size=1,
        accelerator=device,
        run_id=run_id,
    )
    config.num_workers = 0
    HydraRunner().main(device=device, config=config)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--experiment", type=Path)
    parser.add_argument("--deterministic", action="store_true")
    args = parser.parse_args()
    if args.deterministic:
        torch.use_deterministic_algorithms(True)
    train(args.dataset, args.output, args.run_id, args.experiment)
