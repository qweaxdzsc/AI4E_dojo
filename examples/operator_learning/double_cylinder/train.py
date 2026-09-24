"""模型与监督显式接入共享训练，保留初值、有效更新和完整恢复状态。"""

import time
from functools import partial

import torch
from configuration import load_configuration, validate

from ai4e_contrib.application.operator_learning.binding import batch, construct
from ai4e_contrib.application.operator_learning.objectives import FieldObjective
from ai4e_contrib.application.operator_learning.preparation import read_prepared
from ai4e_core import run
from ai4e_core.abilities.inference.randomness import seeded_randomness
from ai4e_core.abilities.training.cancellation import cancellation
from ai4e_core.abilities.training.iteration_stream import IterationStream
from ai4e_core.abilities.training.optimization import resolve_device
from ai4e_core.applications.base.iteration_training import train_model
from ai4e_core.base.config.conventions import resolve_input


def train(cfg, prepared=None):
    """恢复目标是累计更新数；无梯度裁剪或额外调度器。"""
    cfg = validate(cfg)
    session = run.TrainingRun()
    if session.dry_run:
        return None
    prepared = resolve_input(
        prepared, cfg["inputs"]["train"]["preparation"], name="train.preparation"
    )
    record, arrays = read_prepared(prepared, "train")
    device = resolve_device(cfg["train"]["device"])
    with seeded_randomness(cfg["seed"]):
        model = construct(cfg).to(device)
        optimizer = torch.optim.Adam(model.parameters(), lr=cfg["train"]["lr"])
        stream = IterationStream(
            len(arrays["target"]), cfg["train"]["batch_size"], seed=cfg["seed"]
        )
        get_batch = partial(
            batch,
            arrays,
            device=device,
            case=cfg["dataset"]["case"],
            sample_points=cfg["train"]["sample_points"],
            point_sequence=cfg["model"]["family"] == "rnn",
        )
        contract = {
            "model": cfg["model"],
            "components": cfg["components"],
            "fields": record["fields"],
            "sensor_layout": "reference-grid-index; per-sample physical coordinates; C-order flatten",
            "metadata": record["metadata"],
            "physical_weight": cfg["train"]["physical_weight"],
            "lr": cfg["train"]["lr"],
            "batch_size": cfg["train"]["batch_size"],
            "sample_points": cfg["train"]["sample_points"],
            "seed": cfg["seed"],
        }
        initial = session.checkpoint(
            "latest",
            {
                "model": model.state_dict(),
                "rng": torch.get_rng_state(),
                "mps_rng": torch.mps.get_rng_state() if device.type == "mps" else None,
            },
            namespace="initial",
        )
        with cancellation() as stopped:
            result = train_model(
                model,
                optimizer,
                stream,
                get_batch,
                FieldObjective(
                    record["metadata"]["statistics"],
                    physical_weight=cfg["train"]["physical_weight"],
                ),
                updates=cfg["train"]["updates"],
                session=session,
                contract=contract,
                namespace="train",
                resume=cfg["inputs"]["train"]["resume"],
                max_grad_norm=None,
                deadline=time.monotonic() + cfg["train"]["seconds"],
                cancelled=stopped,
                checkpoint_every=cfg["train"]["checkpoint_every"],
            )
        if any(not torch.isfinite(p).all() for p in model.parameters()):
            raise FloatingPointError("训练参数非有限")
        result["initial"] = str(initial)
        session.report(result, stage="train")
        return result


if __name__ == "__main__":
    raise SystemExit(
        run.launch(
            {"train": train}, script=__file__, only=["train"], config_loader=load_configuration
        )
    )
