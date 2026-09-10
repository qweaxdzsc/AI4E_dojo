"""观察原真实单样本推理函数返回的全部层缓存，并与 Dojo 实际组件比较。"""

import argparse
import json
import sys
from dataclasses import replace
from pathlib import Path

import numpy as np
import torch

from ai4e_contrib.ability.model.transolver3.inference import SurfaceInference
from ai4e_contrib.ability.model.transolver3.model import construct
from ai4e_contrib.application.datasets.nasa_crm import View
from ai4e_core.applications.aero_cfd.trainprep.pointfields import FieldNormalization, features
from tools.verification.transolver3.compare import compare


def main():
    """只在原函数返回后观察缓存，不替换原参考缓存算法。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, required=True)
    parser.add_argument("--settings", type=Path, required=True)
    parser.add_argument("--dojo-checkpoint", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    sys.path.insert(0, str(args.repository.resolve()))
    from user_project.config import (
        DataConfig,
        InferenceConfig,
        ModelConfig,
        PipelineConfig,
        TrainingConfig,
    )
    from user_project.inference import _infer_sample, run_inference

    settings = json.loads(args.settings.read_text())
    data = dict(settings["data"])
    for key in (
        "train_h5",
        "test_h5",
        "connectivity_h5",
        "processed_dir",
        "predictions_dir",
        "post_dir",
    ):
        data[key] = Path(data[key]) if data.get(key) else None
    training = dict(settings["training"])
    training["checkpoint_dir"] = Path(training["checkpoint_dir"])
    config = PipelineConfig(
        DataConfig(**data),
        ModelConfig(**settings["model"]),
        TrainingConfig(**training),
        InferenceConfig(training["checkpoint_dir"] / "best.pt", training["device"]),
        args.settings,
    )
    config = replace(
        config,
        data=replace(config.data, predictions_dir=args.output_root / "reference-predictions"),
    )
    view = View(config.data.processed_dir)
    norm = FieldNormalization(view.describe()["statistics"])
    name = view.partitions["test"][0]
    reference = []
    code = _infer_sample.__wrapped__.__code__

    def observer(frame, event, _arg):
        if event == "return" and frame.f_code is code:
            reference.extend(
                value.detach().cpu().numpy().copy() for value in frame.f_locals["state_cache"]
            )

    previous = sys.getprofile()
    try:
        sys.setprofile(observer)
        run_inference(config, sample_ids=[name])
    finally:
        sys.setprofile(previous)
    if len(reference) != 24:
        raise ValueError("正式参考必须产生24层缓存")
    model = construct(**settings["model"]).to(training["device"]).float()
    state = torch.load(args.dojo_checkpoint, map_location="cpu", weights_only=False)
    model.load_state_dict(state["model"])
    reports = []

    def chunks():
        for part in range(view.chunk_count):
            raw = view.read("test", 0, selection=part, fields=("points", "normals"))
            yield part, {"features": torch.from_numpy(features(raw, norm))[None]}

    def observe(_kind, layer, state):
        reports.append(
            compare(state.cpu().numpy(), reference[layer], identity=f"{name}/cache/{layer}")
        )

    for part, prediction in SurfaceInference(model).predict(chunks, observer=observe):
        physical = norm.inverse(prediction["fields"][0].cpu().numpy())
        expected = np.load(
            config.data.predictions_dir / "test" / name / f"prediction_part{part}.npy"
        )
        reports.append(compare(physical, expected, identity=f"{name}/prediction/{part}"))
    result = {
        "passed": all(r["passed"] for r in reports),
        "sample": name,
        "layers": len(reference),
        "point_count": view.point_count,
        "comparisons": reports,
        "mismatch_count": sum(r["mismatch_count"] for r in reports),
        "max_absolute_error": max((r["max_absolute_error"] or 0) for r in reports),
    }
    args.output_root.mkdir(parents=True, exist_ok=True)
    (args.output_root / "comparison.json").write_text(json.dumps(result, indent=2))
    print(json.dumps({k: v for k, v in result.items() if k != "comparisons"}))
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
