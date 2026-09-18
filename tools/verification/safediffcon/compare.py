"""原 Trainer 与 Dojo 迭代的独立对照入口；共同数据流消除抽样噪声。"""

import argparse
import importlib
import json
import os
import sys
import tempfile
import time
from pathlib import Path


def source_model(*, case, dim, ddim_steps, device):
    """从已摘要冻结的原代码构造网络，配置显式对应官方构造函数。"""
    diffusion = importlib.import_module("model.diffusion").GaussianDiffusion
    module = importlib.import_module("model.unet")
    if case == "burgers":
        unet = module.Unet2D(dim=dim, dim_mults=(1, 2, 4, 8), channels=3, resnet_block_groups=1)
        model = diffusion(
            unet,
            seq_length=(16, 128),
            use_conv2d=True,
            temporal=True,
            train_on_padded_locations=False,
            is_condition_u0=True,
            is_condition_uT=True,
            condition_idx=10,
            is_condition_u0_zero_pred_noise=True,
            is_condition_uT_zero_pred_noise=True,
            sampling_timesteps=ddim_steps,
            ddim_sampling_eta=1.0,
        )
    else:
        unet = module.Unet1D(dim=dim, dim_mults=(1, 2, 4, 8), channels=12, resnet_block_groups=1)
        model = diffusion(
            unet,
            seq_length=128,
            nt=122,
            use_conv2d=False,
            temporal=False,
            guidance_u0=True,
            is_condition_u0=True,
            is_condition_uT=True,
            is_condition_u0_zero_pred_noise=True,
            is_condition_uT_zero_pred_noise=True,
            sampling_timesteps=ddim_steps,
            ddim_sampling_eta=1.0,
        )
    return model.to(device)


def source_iterations(
    model,
    optimizer,
    stream,
    batch,
    objective,
    *,
    updates,
    start=0,
    scheduler=None,
    ema=None,
    after_update=None,
    checkpoint=None,
    history=None,
    **kwargs,
):
    """执行原 Trainer.train；只替换批次来源、日志落点和观察器。"""
    import torch
    from model import trainer as original

    if start < 0 or updates < start or len(history or []) != start:
        raise ValueError("参考恢复历史与总更新目标不一致")
    original.cpu_count = lambda: 0
    torch_rng = torch.get_rng_state()
    mps_rng = torch.mps.get_rng_state() if torch.backends.mps.is_available() else None
    loss_history = list(history or [])
    with tempfile.TemporaryDirectory(prefix="source-trainer-") as directory:
        previous = Path.cwd()
        os.chdir(directory)
        try:
            instance = original.Trainer(
                model,
                torch.zeros(1),
                train_batch_size=stream.batch_size,
                train_lr=optimizer.param_groups[0]["lr"],
                train_num_steps=updates,
                results_folder=Path(directory) / "weights",
                save_and_sample_every=500,
            )
            if instance.device.type != next(model.parameters()).device.type:
                raise RuntimeError("原 Trainer 设备不符")

            def batches():
                while True:
                    yield batch(stream.next())

            instance.dl = batches()
            # Dojo 容器已恢复数据流、权重和随机状态；映射到原 Trainer 的公开状态。
            instance.step = start
            instance.opt.load_state_dict(optimizer.state_dict())
            if scheduler:
                instance.scheduler.load_state_dict(scheduler.state_dict())
            instance.opt.zero_grad()

            def save_progress(milestone):
                # 原循环已完成优化器、调度器和 EMA 更新；只保留 latest 状态。
                optimizer.load_state_dict(instance.opt.state_dict())
                if scheduler:
                    scheduler.load_state_dict(instance.scheduler.state_dict())
                if checkpoint:
                    checkpoint(instance.step, loss_history, "running")

            instance.save = save_progress

            def observe(*_):
                loss_history.append(float(instance.total_loss))
                if after_update:
                    after_update(instance.step + 1, model)

            instance.opt.optimizer.register_step_post_hook(observe)
            torch.set_rng_state(torch_rng)
            if mps_rng is not None:
                torch.mps.set_rng_state(mps_rng)
            writer_type = original.SummaryWriter
            original.SummaryWriter = lambda **kwargs: writer_type(
                logdir=str(Path(directory) / "tensorboard")
            )
            try:
                instance.train()
            finally:
                original.SummaryWriter = writer_type
            optimizer.load_state_dict(instance.opt.state_dict())
            if scheduler:
                scheduler.load_state_dict(instance.scheduler.state_dict())
        finally:
            os.chdir(previous)
    if checkpoint:
        checkpoint(updates, loss_history, "complete")
    return loss_history


def setup_source(snapshot, case):
    """导入前检查原快照，每个进程仅加载一个案例，避免原包重名。"""
    sys.dont_write_bytecode = True
    from reference import verify_source

    verify_source(Path(snapshot))
    sys.path.insert(0, str(Path(snapshot) / ("1D" if case == "burgers" else "tokamak")))


def main():
    """同预算监督器下运行参考或 Dojo；不在本工具暗中扩展预算。"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--snapshot", required=True)
    parser.add_argument("--side", choices=["reference", "dojo"], required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--set", action="append", default=[])
    parser.add_argument("--pretrain-only", action="store_true")
    parser.add_argument("--pretrained-summary")
    parser.add_argument("--posttrained-summary")
    parser.add_argument("--independent-stages", action="store_true")
    args = parser.parse_args()
    from ai4e_contrib.application.pde_control.safediffcon.configuration import load_configuration

    cfg = load_configuration(args.config, args.set)
    if args.side == "reference":
        setup_source(args.snapshot, cfg["case"])
    # 公开 recipe 普通函数保持可编辑，验证工具只选择原构造器和原训练器。
    recipe = Path(__file__).resolve().parents[3] / "recipes/safediffcon"
    sys.path.insert(0, str(recipe))
    from infer import infer
    from post import post
    from posttrain import posttrain
    from rawprep import rawprep
    from trainprep import trainprep

    from ai4e_contrib.ability.constraint.safediffcon.objective import diffusion_loss
    from ai4e_contrib.ability.model.safediffcon.adapters import build_model
    from ai4e_contrib.application.pde_control.safediffcon.training import pretrain
    from ai4e_core import run
    from ai4e_core.abilities.training.iterations import fit_iterations

    if args.independent_stages and args.side == "reference":
        from reference_stages import ReferenceStages

        stages = ReferenceStages(Path(args.snapshot), cfg["case"])
        posttrain, infer = stages.posttrain, stages.infer

    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()

    def pipeline(config):
        from configuration import plain

        public = config
        config = plain(public)
        physical = config["data"]["physical"] or run.stage("rawprep", rawprep, public)
        prepared = config["data"]["prepared"] or run.stage("trainprep", trainprep, public, physical)
        checkpoint = (
            json.loads(Path(args.pretrained_summary).read_text())["pretrain_checkpoint"]
            if args.pretrained_summary
            else run.stage(
                "train",
                pretrain,
                config,
                prepared,
                construct=source_model if args.side == "reference" else build_model,
                objective=diffusion_loss,
                session=run.TrainingRun(),
                iterate=source_iterations if args.side == "reference" else fit_iterations,
            )
        )
        summary = {
            "side": args.side,
            "pretrain_checkpoint": checkpoint,
            "prepared": prepared,
            "physical": physical,
            "scope": (
                "original_Trainer_and_independent_source_control_stages"
                if args.independent_stages and args.side == "reference"
                else "original_Trainer_pretrain_plus_shared_disclosed_control_stages"
            ),
            "paper_reproduction": False,
        }
        if not args.pretrain_only:
            # 原网络和原 Trainer 独立训练；后训练连接的数值算术另用原函数对照。
            calibrated = (
                json.loads(Path(args.posttrained_summary).read_text())["posttrain_checkpoint"]
                if args.posttrained_summary
                else run.stage(
                    "posttrain",
                    posttrain,
                    config if args.independent_stages and args.side == "reference" else public,
                    prepared,
                    checkpoint,
                )
            )
            results = run.stage(
                "infer",
                infer,
                config if args.independent_stages and args.side == "reference" else public,
                prepared,
                calibrated,
            )
            report = run.stage("post", post, public, results)
            summary.update(posttrain_checkpoint=calibrated, results=results, report=report)
        summary["seconds"] = time.monotonic() - start
        run.TrainingRun().artifact("comparison.json", summary)
        (output / "summary.json").write_text(json.dumps(summary, indent=2))
        return summary

    code = run.launch(
        {"pipeline": pipeline},
        script=__file__,
        only=["pipeline"],
        config_loader=load_configuration,
        argv=["--config", str(Path(args.config).resolve())]
        + [part for item in args.set for part in ("--set", item)],
    )
    return code


if __name__ == "__main__":
    raise SystemExit(main())
