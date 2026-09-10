"""隔离加载只读参考仓库，调用原始四阶段入口；不属于正式包依赖。"""

import argparse
import json
import shutil
import sys
from pathlib import Path


def main():
    """读取配对后的 JSON 参数，运行原仓库并将产物写入独立目录。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, required=True)
    parser.add_argument("--settings", type=Path, required=True)
    parser.add_argument(
        "--stage", choices=["preprocess", "train", "inference", "post"], required=True
    )
    parser.add_argument("--resume", type=Path)
    args = parser.parse_args()
    sys.path.insert(0, str(args.repository.resolve()))
    from user_project.config import (
        DataConfig,
        InferenceConfig,
        ModelConfig,
        PipelineConfig,
        TrainingConfig,
    )

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
        InferenceConfig(Path(training["checkpoint_dir"]) / "best.pt", training["device"]),
        args.settings.resolve(),
    )
    if args.stage == "preprocess":
        from user_project.preprocess import run_preprocess

        run_preprocess(config)
    elif args.stage == "train":
        from user_project import train as training_module

        if args.resume:
            import torch

            prior = torch.load(args.resume, map_location="cpu", weights_only=False)
            if int(prior["epoch"]) + 1 >= config.training.epochs:
                raise ValueError("参考恢复必须实际执行剩余轮次，不能仅凭文件名认定第一轮")
            last = prior.get("history", [])[-1].get("validation") if prior.get("history") else None
            candidate = (
                args.resume
                if last and last["normalized_mse"] == prior["best_validation_mse"]
                else args.resume.with_name("best.pt")
            )
            if not candidate.is_file():
                raise ValueError("独立恢复目录需要与该轮对应的此前最佳检查点")
            selected = torch.load(candidate, map_location="cpu", weights_only=False)
            if (
                selected["best_validation_mse"] != prior["best_validation_mse"]
                or selected["epoch"] > prior["epoch"]
            ):
                raise ValueError("此前最佳检查点与恢复轮次不一致")
            config.training.checkpoint_dir.mkdir(parents=True, exist_ok=True)
            if not (config.training.checkpoint_dir / "best.pt").exists():
                shutil.copyfile(candidate, config.training.checkpoint_dir / "best.pt")

        # 工具目录加入路径仅供验收观察器导入，不进入正式包。
        sys.path.insert(1, str(Path(__file__).resolve().parents[3]))
        from tools.verification.transolver3.trace import install

        trace = install(training_module, config.training.checkpoint_dir)
        training_module.run_training(config, resume_checkpoint=args.resume)
        (config.training.checkpoint_dir / "input-trace.json").write_text(json.dumps(trace))
    elif args.stage == "inference":
        from user_project.inference import run_inference

        run_inference(config)
    else:
        from user_project.post import run_postprocess

        run_postprocess(config, all_samples=True, export_vtk=settings.get("export_vtk", False))


if __name__ == "__main__":
    main()
