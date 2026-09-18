"""直接运行固定 Burgers 原 Trainer 的参考预训练，不导入 Dojo 算法。

本入口只改变路径、数据加载工作进程数与权重保留策略，不改变前向、损失、
优化器、更新顺序或随机种子。完整论文复现仍须后训练、适配与物理响应验收。
原 Trainer 的 checkpoint 缺少数据流游标，本入口明确不提供精确恢复。
"""

import argparse
import hashlib
import importlib.metadata
import json
import os
import sys
import time
import traceback
from pathlib import Path


def verify_source(snapshot: Path) -> dict:
    """对导入前的实际文件核验摘要，避免原始快照漂移。"""
    manifest = json.loads((snapshot / "source.json").read_text())
    for name, expected in manifest["files"].items():
        with (snapshot / name).open("rb") as stream:
            actual = hashlib.file_digest(stream, "sha256").hexdigest()
        if actual != expected:
            raise ValueError(f"参考快照摘要变化: {name}")
    return manifest


def verify_pretrain_inputs(admission: Path, snapshot: Path, dataset: Path) -> None:
    """完整预训练必须消费本次已扫描、未变化的 Burgers 数据和参考源码。"""
    report = json.loads(admission.read_text())
    if report.get("burgers", {}).get("status") != "passed":
        raise ValueError("Burgers 数据准入未通过")
    manifest = json.loads((snapshot / "source.json").read_text())
    if report["source"] != manifest:
        raise ValueError("参考源码与准入记录不符")
    for split, expected in {"train": 39000, "cal": 1000, "test": 50}.items():
        item = report["burgers"]["splits"][split]
        path = dataset / f"burgers_{split}.h5"
        if item["samples"] != expected or Path(item["source"]).resolve() != path.resolve():
            raise ValueError("数据路径或正式样本数量变化")
        with path.open("rb") as stream:
            actual = hashlib.file_digest(stream, "sha256").hexdigest()
        if actual != item["sha256"]:
            raise ValueError(f"准入后数据变化: {split}")


def pretrain_burgers(
    snapshot: Path, dataset: Path, output: Path, *, steps: int, device: str, record: dict
) -> None:
    """执行原版完整宽度网络；短更新数只允许标成诊断。"""
    import torch

    sys.path.insert(0, str(snapshot / "1D"))
    from configs.train_config import get_train_config
    from data.burgers import BurgersDataset
    from model import trainer as original
    from utils.common import build_model, set_seed

    torch.set_num_threads(4)
    config = get_train_config(exp_id="dojo-reference", model_size="turbo")
    config.device = device
    set_seed(config.seed)
    dataset_view = BurgersDataset(
        root_path=str(dataset.parent), dataset=dataset.name, split="train", config=config
    )
    model = build_model(config, dataset_view)
    # 原数据读取和变换均确定性；禁用多进程以避免 macOS fork/重复大数组。
    original.cpu_count = lambda: 0
    checkpoints = output / "checkpoints"
    checkpoints.mkdir()
    trainer = original.Trainer(
        model,
        dataset_view,
        results_folder=checkpoints,
        train_num_steps=steps,
        train_lr=config.lr,
        save_and_sample_every=1000,
    )
    if str(trainer.device) != device:
        raise RuntimeError(f"Accelerate 实际设备 {trainer.device} 与请求 {device} 不同")
    save_original = trainer.save

    def retained_save(milestone):
        """调用原保存方法，仅保留最新完整状态与正式选定的两个里程碑。"""
        save_original("pending")
        pending = checkpoints / "model-pending.pt"
        pending.replace(checkpoints / "latest.pt")
        record.update(
            step=trainer.step, loss=trainer.total_loss, elapsed_seconds=time.monotonic() - start
        )
        (output / "progress.json").write_text(json.dumps(record, indent=2))

    trainer.save = retained_save

    def observe_update(*_):
        """仅观察优化器完成次数，每 50 次刷新可读进度，不修改模型状态。"""
        completed = trainer.step + 1
        if completed % 50 == 0:
            record.update(
                step=completed, loss=trainer.total_loss, elapsed_seconds=time.monotonic() - start
            )
            temporary = output / "progress.pending.json"
            temporary.write_text(json.dumps(record, indent=2))
            temporary.replace(output / "progress.json")

    trainer.opt.optimizer.register_step_post_hook(observe_update)
    record.update(
        parameters=sum(p.numel() for p in model.parameters()),
        batch_size=trainer.batch_size,
        dataset_samples=len(dataset_view),
        dim=config.dim,
        dim_mults=list(config.dim_mults),
        seed=config.seed,
        train_lr=config.lr,
        scheduler_T_max=trainer.scheduler.T_max,
        adam_betas=list(trainer.opt.param_groups[0]["betas"]),
        precision="float32",
        workers=0,
        device=str(trainer.device),
        original_trainer=True,
        resume_supported=False,
    )
    (output / "progress.json").write_text(json.dumps(record, indent=2))
    start = time.monotonic()
    trainer.train()
    if steps % 1000:
        retained_save("diagnostic-final")
    record.update(
        step=trainer.step, loss=trainer.total_loss, elapsed_seconds=time.monotonic() - start
    )


def main() -> int:
    """参考进程入口，独占输出目录并记录实际环境和失败原因。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, required=True)
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--steps", type=int, required=True)
    parser.add_argument("--admission", type=Path)
    parser.add_argument("--device", choices=("cpu", "mps"), default="mps")
    args = parser.parse_args()
    args.snapshot, args.dataset, args.output = (
        p.resolve() for p in (args.snapshot, args.dataset, args.output)
    )
    if args.steps <= 0 or args.steps > 4000:
        parser.error("当前授权为三小时集成，参考更新数必须在 1 到 4000 之间")
    if args.output.exists() or any(
        args.output.is_relative_to(p) for p in (args.snapshot, args.dataset)
    ):
        parser.error("输出必须为新的独立目录")
    manifest = verify_source(args.snapshot)
    if args.admission is not None:
        verify_pretrain_inputs(args.admission.resolve(), args.snapshot, args.dataset)
    args.output.mkdir(parents=True)
    work = args.output / "work"
    work.mkdir()
    os.chdir(work)
    record = {
        "status": "running",
        "scope": "diagnostic",
        "requested_updates": args.steps,
        "source_commit": manifest["commit"],
        "source_patch": manifest["patch_sha256"],
        "dataset": str(args.dataset),
        "pid": os.getpid(),
        "paper_reproduction": "not_complete",
        "started": time.time(),
        "packages": {d.metadata["Name"]: d.version for d in importlib.metadata.distributions()},
    }
    (args.output / "progress.json").write_text(json.dumps(record, indent=2))
    try:
        pretrain_burgers(
            args.snapshot,
            args.dataset,
            args.output,
            steps=args.steps,
            device=args.device,
            record=record,
        )
        record["status"] = "pretrain_completed"
    except BaseException as error:
        record.update(status="failed", error=str(error), traceback=traceback.format_exc())
        raise
    finally:
        (args.output / "progress.json").write_text(json.dumps(record, indent=2))
    print(json.dumps({k: v for k, v in record.items() if k != "packages"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
