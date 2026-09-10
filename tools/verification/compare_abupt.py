"""在官方 Noether 环境运行的差分验收；正式包无 Noether 依赖。"""

import argparse
import hashlib
import json
from pathlib import Path

import torch
from aero_cfd.presets import ShapeNetCarPreset
from noether.modeling.models.ab_upt import AnchoredBranchedUPT as Reference
from state_mapping import mapped_state

from ai4e_contrib.ability.model.abupt.network import AnchoredBranchedUPT


def reference_model():
    """实际官方预设，仅缩小模型以逐张量定位误差。"""
    config = ShapeNetCarPreset().build_config(
        model_kind="noether.modeling.models.aerodynamics.AeroABUPT",
        model_params={
            "hidden_dim": 24,
            "geometry_depth": 1,
            "physics_blocks": ["perceiver", "shared", "cross"],
            "num_domain_decoder_blocks": {"surface": 1, "volume": 1},
        },
        trainer_kind="noether.training.trainers.WeightedLossTrainer",
        trainer_params={"field_weights": {"surface_pressure": 1.0, "volume_velocity": 1.0}},
        dataset_root="/Users/zonghui/work/datasets/shapenet_car_cfd",
        output_path="/tmp/dojo-reference",
        max_epochs=2,
        batch_size=1,
        accelerator="cpu",
        run_id="differential",
    )
    return Reference(config.model)


def compare(output):
    """实际前向、反向及更新差分；失败保留报告并非零退出。"""
    torch.set_num_threads(1)
    torch.manual_seed(32)
    reference = reference_model()
    from omegaconf import OmegaConf

    config = OmegaConf.to_container(
        OmegaConf.load(Path(__file__).resolve().parents[2] / "recipes/aero_cfd/config.yaml"),
        resolve=True,
    )
    torch.manual_seed(32)
    model = AnchoredBranchedUPT(
        data_specs=config["model"]["data_specs"],
        require_features=False,
        dim=24,
        geometry_depth=1,
        num_heads=3,
        blocks="psc",
        num_domain_decoder_blocks={"surface": 1, "volume": 1},
    )
    for key, value in model.state_dict().items():
        torch.testing.assert_close(value, mapped_state(reference, model)[key], rtol=0, atol=0)
    positions = torch.rand(8, 3) * 4
    inputs = {
        "geometry_position": positions,
        "geometry_supernode_idx": torch.tensor([0, 2, 4, 6]),
        "geometry_batch_idx": torch.zeros(8, dtype=torch.long),
        "domain_anchor_positions": {
            "surface": torch.rand(1, 4, 3) * 4,
            "volume": torch.rand(1, 5, 3) * 4,
        },
    }
    left = reference(**inputs)[0]
    right = model(**inputs)[0]
    errors = {name: float((left[name] - right[name]).abs().max().detach()) for name in left}
    report = {
        "scope": "CPU FP32 equal seeded initialization, forward and backward; not full-training equivalence",
        "forward_max_abs": errors,
        "passed": False,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2))
    for name in left:
        torch.testing.assert_close(left[name], right[name], rtol=1e-5, atol=1e-6)
    sum(x.square().mean() for x in left.values()).backward()
    sum(x.square().mean() for x in right.values()).backward()
    # 一个普通 SGD 更新后重新映射参数，覆盖反向的整体数值效应。
    for network in (reference, model):
        torch.optim.SGD(network.parameters(), lr=0.01).step()
    mapped = mapped_state(reference, model)
    for name, value in model.state_dict().items():
        torch.testing.assert_close(value, mapped[name], rtol=1e-5, atol=1e-6)
    from noether.core.optimizer.lion import Lion as ReferenceLion
    from noether.core.schedules.linear_warmup_cosine_decay import (
        LinearWarmupCosineDecaySchedule,
        LinearWarmupCosineDecayScheduleConfig,
    )

    from ai4e_core.abilities.training.optimization import Lion, parameter_groups
    from ai4e_core.abilities.training.schedule import build_scheduler

    ropt = ReferenceLion(parameter_groups(reference, weight_decay=0.05), lr=5e-5)
    opt = Lion(parameter_groups(model, weight_decay=0.05), lr=5e-5)
    schedule = build_scheduler(
        "warmup_cosine", opt, total_updates=20, min_lr=1e-6, warmup_ratio=0.25
    )
    official = LinearWarmupCosineDecaySchedule(
        LinearWarmupCosineDecayScheduleConfig(max_value=5e-5, end_value=1e-6, warmup_percent=0.25)
    )
    for update in range(20):
        rate = official.get_value(update, 20)
        assert abs(opt.param_groups[0]["lr"] - rate) < 1e-15
        for group in ropt.param_groups:
            group["lr"] = rate
        for network, optimizer in [(reference, ropt), (model, opt)]:
            optimizer.zero_grad()
            predictions = network(**inputs)[0]
            sum(v.square().mean() for v in predictions.values()).backward()
            torch.nn.utils.clip_grad_norm_(network.parameters(), 1.0)
            optimizer.step()
        schedule.step()
        mapped = mapped_state(reference, model)
        for name, value in model.state_dict().items():
            torch.testing.assert_close(value, mapped[name], rtol=1e-5, atol=1e-6)
    report["lion_updates"] = 20
    report["initialization_exact"] = True
    report["passed"] = True
    report["reference_model_sha256"] = hashlib.sha256(
        Path(__import__("inspect").getfile(Reference)).read_bytes()
    ).hexdigest()
    output.write_text(json.dumps(report, indent=2))
    print(json.dumps(report))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    compare(parser.parse_args().output)
