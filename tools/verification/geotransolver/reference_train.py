"""独立原定义的成对短训；不调用 Dojo 训练/损失/解码/调度/优化能力。"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import torch
import yaml

from .reference import cached_cpu_radius, load_reference, reference_optimizer


def run(case, preparation, config, output):
    """用审计过的冻结数组，独立原网络执行同一采样顺序及更新目标。"""
    torch.set_num_threads(4)
    torch.manual_seed(config["seed"])
    root = Path(preparation).parent
    prepared = json.loads(Path(preparation).read_text())
    split = root / prepared["splits"]["train"]
    record = json.loads(split.read_text())
    arrays = {
        name: np.load(split.parent / value["path"], mmap_mode="r")
        for name, value in record["fields"].items()
    }
    stats = prepared["statistics"]
    count = len(arrays["target"])
    size = config["train"]["batch_size"]
    device = config["train"]["device"]
    reference = load_reference()
    cached_cpu_radius(reference)
    model = reference.GeoTransolver(**config["model"]).to(device)
    opt = reference_optimizer(
        model, lr=config["train"]["lr"], weight_decay=config["train"]["weight_decay"]
    )
    per_epoch = count // size
    epochs = config["train"]["schedule_epochs"]
    warmup = per_epoch * 2
    if case == "darcy":
        scheduler = torch.optim.lr_scheduler.SequentialLR(
            opt,
            [
                torch.optim.lr_scheduler.LinearLR(opt, start_factor=0.01, total_iters=warmup),
                torch.optim.lr_scheduler.CosineAnnealingLR(
                    opt, T_max=per_epoch * epochs - warmup, eta_min=config["train"]["end_lr"]
                ),
            ],
            milestones=[warmup],
        )
    else:
        scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
            opt, T_max=epochs, eta_min=config["train"]["end_lr"]
        )
    rng = torch.Generator().manual_seed(config["seed"])
    offset = count
    order = None
    history = []
    started = time.monotonic()
    for update in range(config["train"]["updates"]):
        if offset == count:
            order = torch.randperm(count, generator=rng)
            offset = 0
        ids = order[offset : offset + size].numpy()
        offset += size

        def get(name, ids=ids):
            return torch.from_numpy(np.array(arrays[name][ids], copy=True)).to(
                device=device, dtype=torch.float32
            )

        inputs = {name: get(name) for name in ("local_embedding", "geometry") if name in arrays}
        if case != "darcy":
            inputs.update(
                local_positions=get("local_positions"), global_embedding=get("global_embedding")
            )
        opt.zero_grad()
        raw = model(**inputs)
        if case == "darcy":
            prediction = raw * raw.new_tensor(stats["sol"]["std"]) + raw.new_tensor(
                stats["sol"]["mean"]
            )
            target = get("physical_target")[:, 0]
            loss = (
                torch.norm((prediction - target).reshape(size, -1), p=2, dim=1)
                / torch.norm(target.reshape(size, -1), p=2, dim=1)
            ).mean()
        else:
            b, n, _ = raw.shape
            prediction = raw.reshape(b, n, 10, 5).permute(0, 2, 1, 3).clone()
            prediction[..., :3] += inputs["local_embedding"][:, None]
            loss = torch.nn.functional.mse_loss(prediction, get("target"))
        loss.backward()
        opt.step()
        if case == "darcy" or (update + 1) % per_epoch == 0:
            scheduler.step()
        history.append(float(loss.detach()))
        if (update + 1) % 25 == 0:
            print(
                f"{case} reference {update + 1}/{config['train']['updates']} loss={history[-1]:.7g}",
                flush=True,
            )
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "model": model.state_dict(),
            "history": history,
            "updates": len(history),
            "optimizer": opt.state_dict(),
            "scheduler": scheduler.state_dict(),
            "order": order,
            "offset": offset,
            "rng": rng.get_state(),
        },
        output / "checkpoint.pt",
    )
    (output / "summary.json").write_text(
        json.dumps(
            {
                "case": case,
                "seconds": time.monotonic() - started,
                "updates": len(history),
                "first_loss": history[0],
                "last_loss": history[-1],
            },
            indent=2,
        )
        + "\n"
    )


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--case", required=True)
    p.add_argument("--preparation", required=True)
    p.add_argument("--config", type=Path, required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()
    run(a.case, a.preparation, yaml.safe_load(a.config.read_text()), a.output)
