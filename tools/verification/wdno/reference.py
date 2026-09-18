"""原 WDNO Trainer 的本地切片入口；不导入 Dojo 算法，不宣称论文复现。"""

import argparse
import importlib.metadata
import json
import random
import signal
import sys
import time
from pathlib import Path
from types import SimpleNamespace

from protocol import digest, verify, write_json


class BudgetStop(Exception):
    """只在一个完整更新之后停止。"""


def main():
    """准备、原训练、普通权重采样和固定结果报告共用一个累计时钟。"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--frozen", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--diagnostic", action="store_true")
    args = parser.parse_args()
    started = time.monotonic()
    ledger = json.loads(args.ledger.read_text())
    credit = ledger["seconds"]
    if not ledger["runs"] or ledger["runs"][-1]["status"] != "running":
        raise ValueError("必须由累计预算监督器启动")
    # 包括监督器启动子进程的时间，不能以导入/准备重置阶段截止。
    credit += max(0, time.time() - ledger["runs"][-1]["started"])
    elapsed = lambda: credit + time.monotonic() - started
    cfg = verify(args.frozen)
    if (
        cfg["max_updates"],
        cfg["train_cutoff"],
        cfg["evaluation_cutoff"],
        cfg["total_seconds"],
    ) != (2000, 8100, 9900, 10800):
        raise ValueError("冻结切片预算不符，不能静默扩大计算")
    args.output.mkdir(parents=True, exist_ok=False)
    output = args.output.resolve()
    write_json(output / "protocol.json", cfg)
    write_json(
        output / "entry-source.json",
        {
            "protocol_sha256": digest(args.frozen / "protocol.json"),
            "reference_sha256": digest(__file__),
            "protocol_tool_sha256": digest(Path(__file__).with_name("protocol.py")),
        },
    )
    sys.path.insert(0, str(args.frozen.resolve() / "source" / "burgers"))
    sys.path.insert(0, str(args.frozen.resolve() / "source" / "burgers" / "ddpm_burgers"))
    import numpy as np
    import torch
    from ddpm_burgers import test_util
    from ddpm_burgers import train_diffusion as original
    from ddpm_burgers.data_burgers_1d import get_wavelet_super_preprocess
    from ddpm_burgers.diffusion_1d import GaussianDiffusion
    from ddpm_burgers.unet import Unet2D
    from pytorch_wavelets import DWTForward, DWTInverse
    from wave_trans import coef_to_tensor, tensor_to_coef

    torch.set_num_threads(8)
    if not torch.backends.mps.is_available():
        raise RuntimeError("计划要求本机 MPS，不静默改用 CPU")
    stopped = [False]
    signal.signal(signal.SIGINT, lambda *_: stopped.__setitem__(0, True))
    indices = json.loads((args.frozen / "indices.json").read_text())
    if args.diagnostic:
        indices = {key: values[:64] for key, values in indices.items()}
        indices["validation"] = indices["validation"][:2]
        indices["test"] = indices["test"][:2]
    raw = {}
    for name, item in cfg["sources"].items():
        if digest(item["file"]) != item["sha256"]:
            raise ValueError("开训前数据摘要变化")
        raw[name] = torch.load(item["file"], mmap=True, weights_only=True, map_location="cpu")
    scale = torch.tensor([10, 3, 3, 1, 21, 5, 5, 1, 10]).view(1, 9, 1, 1)
    transform = DWTForward(J=1, mode="periodization", wave="bior2.4")
    prepare = get_wavelet_super_preprocess(
        rescaler=scale,
        mode="periodization",
        wave_type="bior2.4",
        is_condition_u0=True,
        is_condition_uT=False,
    )
    prepared_path = output / "train.npy"
    prepared = np.lib.format.open_memmap(
        prepared_path, mode="w+", dtype="float32", shape=(len(indices["train"]), 9, 64, 64)
    )
    reconstruction_error = 0.0
    inverse = DWTInverse(mode="periodization", wave="bior2.4")
    for start in range(0, len(indices["train"]), 256):
        if stopped[0] or elapsed() > cfg["train_cutoff"] - 120:
            raise TimeoutError("准备期间预算不足")
        chosen = indices["train"][start : start + 256]
        u, f = raw["train"]["u"][chosen], raw["train"]["f"][chosen]
        fields = torch.stack((u, torch.nn.functional.pad(f, (0, 0, 0, 1))), dim=1)
        with torch.no_grad():
            coefficients = coef_to_tensor(*transform(fields))
            values, shape, ori_shape = prepare({"coef": [coefficients], "ori_shape": [81, 120]})
            reconstructed = inverse(tensor_to_coef(values[:, :8] * scale[:, :8], shape))[
                :, :, :81, :120
            ]
            reconstruction_error = max(
                reconstruction_error, float((fields - reconstructed).abs().max())
            )
        if not torch.isfinite(values).all():
            raise ValueError("非有限小波系数")
        prepared[start : start + len(chosen)] = values.numpy()
        print("prepare", start + len(chosen), "/", len(indices["train"]), flush=True)
    prepared.flush()
    write_json(
        output / "preparation.json",
        {
            "samples": len(prepared),
            "shape": list(prepared.shape),
            "coefficient_shape": shape,
            "original_shape": ori_shape,
            "reconstruction_max_abs": reconstruction_error,
            "sha256": digest(prepared_path),
            "source_functions": True,
        },
    )

    class Dataset(torch.utils.data.Dataset):
        def __len__(self):
            return len(prepared)

        def __getitem__(self, index):
            return torch.from_numpy(prepared[index].copy())

    random.seed(cfg["seed"])
    np.random.seed(cfg["seed"])
    torch.manual_seed(cfg["seed"])
    torch.mps.manual_seed(cfg["seed"])
    network = Unet2D(dim=128, dim_mults=(1, 2, 4, 8), channels=9, out_dim=9, resnet_block_groups=1)
    diffusion = GaussianDiffusion(
        network,
        seq_length=(64, 64),
        is_wavelet=True,
        padded_shape=shape,
        ori_shape=ori_shape,
        pad_mode="periodization",
        wave_type="bior2.4",
        is_super_model=False,
        upsample_t=0,
        upsample_x=0,
        timesteps=1000,
        sampling_timesteps=50,
        ddim_sampling_eta=1,
        beta_schedule="cosine",
        loss_layer_weight=scale,
        is_condition_pad=True,
        is_condition_u0=True,
        is_condition_uT=False,
        is_condition_f=True,
    )
    if sum(p.numel() for p in network.parameters()) != 140748553:
        raise ValueError("正式切片网络参数数量变化")
    history = []

    class Writer:
        def __init__(self, *_, **__):
            pass

        def add_scalar(self, name, value, step):
            if not np.isfinite(value):
                raise FloatingPointError("非有限训练损失")
            history.append({"source_step": step, "loss": value})

        def close(self):
            write_json(output / "losses.json", history)

    # 唯一运行时适配：单进程读盘、日志观察、保存位置和安全边界取消。
    original.cpu_count = lambda: 0
    original.SummaryWriter = Writer
    maximum = 2 if args.diagnostic else cfg["max_updates"]
    trainer = original.Trainer(
        diffusion,
        Dataset(),
        rescaler=scale,
        wave_type="bior2.4",
        pad_mode="periodization",
        train_batch_size=16,
        train_num_steps=maximum,
        train_lr=1e-4,
        save_and_sample_every=500,
        test_every=50,
        results_folder=str(output / "checkpoints"),
    )
    if str(trainer.device) != "mps":
        raise RuntimeError("原 Trainer 未选择 MPS: " + str(trainer.device))
    record = {
        "status": "training",
        "parameters": 140748553,
        "updates": 0,
        "torch": torch.__version__,
        "python": sys.version,
        "device": str(trainer.device),
        "original_trainer": True,
        "diagnostic": args.diagnostic,
        "exact_resume_supported": False,
        "ema_initial_step": int(trainer.ema.step),
        "dependencies": {
            name: importlib.metadata.version(name)
            for name in ("torch", "accelerate", "ema-pytorch", "pytorch-wavelets", "numpy")
        },
    }
    write_json(output / "progress.json", record)
    save_original = trainer.save

    def save(completed):
        before = time.monotonic()
        save_original("pending")
        pending = output / "checkpoints" / "True-cos10000-model-pending.pt"
        pending.replace(output / "checkpoints" / "latest.pt")
        # 原文件 step 在周期保存时为零起始下标；明确保存完成更新数，不能误读。
        write_json(
            output / "checkpoint.json",
            {
                "completed_updates": completed,
                "source_step_field": trainer.step,
                "path": str(output / "checkpoints" / "latest.pt"),
                "seconds": time.monotonic() - before,
                "weights_for_evaluation": "model",
                "exact_resume_supported": False,
            },
        )
        Writer().close()

    trainer.save = lambda _: save(trainer.step + 1)
    stream = trainer.dl
    ticks = []

    def guarded_batches():
        previous = time.monotonic()
        while True:
            if trainer.step:
                ticks.append(time.monotonic() - previous)
            previous = time.monotonic()
            record.update(
                updates=trainer.step,
                elapsed_seconds=elapsed(),
                last_loss=history[-1]["loss"] if history else None,
            )
            if trainer.step % 10 == 0:
                write_json(output / "progress.json", record)
            # 保留至少两分钟给完整权重保存；只依据时间，不依据测试成绩。
            expected = max(ticks[-20:] or [5])
            if stopped[0] or elapsed() + expected + 120 >= cfg["train_cutoff"]:
                raise BudgetStop()
            yield next(stream)

    trainer.dl = guarded_batches()
    try:
        trainer.train()
        record["status"] = "training_complete"
    except BudgetStop:
        record["status"] = "training_budget_stopped"
    save(trainer.step)
    record.update(
        updates=trainer.step,
        elapsed_seconds=elapsed(),
        last_loss=history[-1]["loss"] if history else None,
    )
    write_json(output / "progress.json", record)
    if args.diagnostic:
        check = torch.load(
            output / "checkpoints" / "latest.pt", map_location="cpu", weights_only=False
        )
        assert check["step"] == 2 and int(check["ema"]["step"]) == 2
        write_json(output / "diagnostic.json", {"checkpoint_readback": True, **record})
        del check

    # 原 get_target 仅替换数据来源；其条件小波变换与原 mse_deviation 直接执行。
    target_args = SimpleNamespace(
        dataset="1d",
        pad_mode="periodization",
        wave_type="bior2.4",
        is_condition_u0=True,
        is_condition_uT=False,
    )
    diffusion = trainer.accelerator.unwrap_model(trainer.model).eval()
    inverse = inverse.to("mps")
    all_metrics = {}
    for split in ("validation", "test"):
        source = raw["train" if split == "validation" else "test"]

        class Targets:
            def __init__(self, *_, arrays=source, **__):
                self.ori_shape = [81, 120]
                self.arrays = arrays

            def get(self, selected):
                return torch.stack(
                    (
                        self.arrays["u"][selected],
                        torch.nn.functional.pad(self.arrays["f"][selected], (0, 0, 0, 1)),
                    ),
                    dim=1,
                )

        test_util.DiffusionDataset = Targets
        completed = []
        metrics = []
        predictions = []
        truths = []
        controls = []
        duration = 60.0
        for offset in range(0, len(indices[split]), 16):
            if stopped[0] or elapsed() + duration + 30 >= cfg["evaluation_cutoff"]:
                break
            before = time.monotonic()
            chosen = indices[split][offset : offset + 16]
            # 原评价 CPU seed 随 batch，MPS 每 batch seed=0。
            torch.manual_seed(offset // 16)
            torch.mps.manual_seed(0)
            u0 = test_util.get_target(target_args, True, chosen, device="cpu")[:, :32] / 10
            force = (
                test_util.get_target(target_args, True, chosen, f=True, device="cpu")
                / scale[:, 4:8]
            )
            with torch.no_grad():
                sampled = diffusion.sample(
                    batch_size=len(chosen), u_init=u0.to("mps"), f=force.to("mps")
                )
                physical = inverse(tensor_to_coef(sampled * scale.to("mps"), shape))[
                    :, :, :81, :120
                ]
                predicted = physical[:, 0].cpu()
                truth = source["u"][chosen]
                values = test_util.mse_deviation(predicted[:, 1:], truth[:, 1:])
            if not torch.isfinite(physical).all() or not torch.isfinite(values).all():
                raise FloatingPointError("非有限采样结果")
            completed.extend(chosen)
            predictions.append(predicted.numpy())
            truths.append(truth.numpy())
            controls.append(physical[:, 1, :80].cpu().numpy())
            metrics.extend(values.tolist())
            duration = time.monotonic() - before
            print("evaluate", split, len(completed), "seconds", duration, flush=True)
            np.savez(
                output / (split + "-results.npz"),
                ids=completed,
                prediction=np.concatenate(predictions),
                target=np.concatenate(truths),
                forcing=np.concatenate(controls),
                mse=metrics,
            )
            write_json(
                output / (split + "-metrics.json"),
                {
                    "status": "complete" if len(completed) == len(indices[split]) else "partial",
                    "requested": len(indices[split]),
                    "completed": len(completed),
                    "sample_mse": metrics,
                    "mse": float(np.mean(metrics)),
                    "initial_condition_max_abs": float(
                        np.max(
                            np.abs(np.concatenate(predictions)[:, 0] - np.concatenate(truths)[:, 0])
                        )
                    ),
                },
            )
        all_metrics[split] = {
            "requested": len(indices[split]),
            "completed": len(completed),
            "mse": float(np.mean(metrics)) if metrics else None,
        }
    record.update(
        status="slice_complete"
        if all(v["requested"] == v["completed"] for v in all_metrics.values())
        else "partial",
        elapsed_seconds=elapsed(),
        evaluation=all_metrics,
        paper_reproduced=False,
    )
    write_json(output / "result.json", record)
    write_json(output / "progress.json", record)
    print(json.dumps(record), flush=True)


if __name__ == "__main__":
    main()
