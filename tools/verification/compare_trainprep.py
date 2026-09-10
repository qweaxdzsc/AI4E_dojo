"""真实官方处理器与 recipe 准备数据逐样本自然采样对照。"""

import argparse
import hashlib
import inspect
import json
from copy import deepcopy
from pathlib import Path

import torch
from aero_cfd.pipeline.multistage_pipelines.aero_multistage import AeroMultistagePipeline
from aero_cfd.presets import ShapeNetCarPreset
from noether.data.preprocessors.normalizers import (
    MeanStdNormalization,
    MeanStdNormalizerConfig,
    PositionNormalizer,
    PositionNormalizerConfig,
)
from recipe_config import load_application_config

from ai4e_contrib.ability.model.abupt.sampling import prepare_inputs
from ai4e_core.applications.aero_cfd.train.resolve import apply_resolved
from ai4e_core.applications.aero_cfd.trainprep import preparation


def compare(config_path: Path, output: Path):
    """对照归一化、索引、坐标和目标，并确认全局随机状态推进一致。"""
    from ai4e_core.base.events import LOGGER

    LOGGER.propagate = False
    config = apply_resolved(load_application_config(config_path))
    # 与复制 recipe 配对采样预算；用相同自然随机流逐个比较处理器。
    config["sampling"]["random_stream"] = "global"
    config["sampling"]["pipeline_seed"] = None
    config["normalization"]["execute"] = True
    data = preparation.freeze_normalization(
        preparation.prepare_fields(preparation.open_dataset(config))
    )
    preset = ShapeNetCarPreset()
    preset.pipeline_model_overrides = deepcopy(preset.pipeline_model_overrides)
    preset.pipeline_model_overrides["noether.modeling.models.aerodynamics.AeroABUPT"].update(
        num_geometry_supernodes=config["sampling"]["supernodes"]["num_points"],
        num_surface_anchor_points=config["sampling"]["domains"]["surface"]["anchor"]["num_points"],
        num_volume_anchor_points=config["sampling"]["domains"]["volume"]["anchor"]["num_points"],
    )
    cfg = preset.build_pipeline("noether.modeling.models.aerodynamics.AeroABUPT")
    pipeline = AeroMultistagePipeline(cfg)
    processors = pipeline._build_sample_processor_pipeline()
    max_abs = {}
    comparisons = 0
    for partition, names in data.index.partitions.items():
        for item, name in enumerate(names):
            physical = data.physical_prepare(data.index.read(partition, item))
            expected = dict(physical)
            for field, decl in data.normalization.record["fields"].items():
                params = decl["parameters"]
                if decl["method"] == "coordinate":
                    expected[field] = PositionNormalizer(
                        PositionNormalizerConfig(
                            raw_pos_min=params["minimum"],
                            raw_pos_max=params["maximum"],
                            scale=params["scale"],
                        ),
                        normalization_key=field,
                    )(expected[field])
                elif decl["method"] == "zscore":
                    expected[field] = MeanStdNormalization(
                        MeanStdNormalizerConfig(mean=params["mean"], std=params["std"]),
                        normalization_key=field,
                    )(expected[field])
            normalized = data.normalization.apply(physical)
            for field, value in normalized.items():
                torch.testing.assert_close(value, expected[field], rtol=1e-6, atol=1e-6)
            expected["index"] = item
            torch.manual_seed(100 + comparisons)
            state = torch.get_rng_state()
            for processor in processors:
                expected = processor(expected)
            after = torch.get_rng_state()
            torch.set_rng_state(state)
            actual = prepare_inputs(
                normalized,
                config["sampling"],
                sample=name,
                sample_index=item,
                data_specs=config["model"]["data_specs"],
                bindings=config["trainprep"],
                normalization=data.normalization,
            )
            assert torch.equal(after, torch.get_rng_state()), "随机流推进不一致"
            values = {
                "geometry_position": actual["inputs"]["geometry_position"],
                "geometry_supernode_idx": actual["inputs"]["geometry_supernode_idx"],
                **{
                    d + "_anchor_position": v
                    for d, v in actual["inputs"]["domain_anchor_positions"].items()
                },
                **actual["targets"],
            }
            for key, value in values.items():
                reference = expected[key]
                torch.testing.assert_close(value, reference, rtol=1e-6, atol=1e-6)
                max_abs[key] = max(max_abs.get(key, 0), float((value - reference).abs().max()))
            comparisons += 1
    report = {
        "passed": True,
        "samples": comparisons,
        "full_official_split": comparisons == 889,
        "max_abs": max_abs,
        "reference_sha256": hashlib.sha256(
            Path(inspect.getfile(AeroMultistagePipeline)).read_bytes()
        ).hexdigest(),
    }
    output.write_text(json.dumps(report, indent=2))
    print(json.dumps(report))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    compare(args.config, args.output)
