"""显式选择网络、取批、解码目标和优化策略；core 执行训练及恢复。"""

import time
from functools import partial

import torch
from configuration import component, validate
from local_components import epoch_records

from ai4e_contrib.application.geotransolver import build_model, build_optimizer, build_scheduler
from ai4e_contrib.application.parametric_pde.geotransolver import binding
from ai4e_core import run
from ai4e_core.abilities.constraint.relative_norm import supervised_objective
from ai4e_core.abilities.geometry.radius_query import install_prepared_queries
from ai4e_core.abilities.inference.prediction import named_array_batch
from ai4e_core.abilities.training.cancellation import cancellation
from ai4e_core.abilities.training.epoch_stream import EpochBatchStream
from ai4e_core.abilities.training.optimization import resolve_device
from ai4e_core.applications.base.iteration_training import train_model
from ai4e_core.applications.parametric_pde.trainprep import read_field_inputs
from ai4e_core.base.config.conventions import resolve_input


def train(cfg, prepared=None):
    """更新数为恢复后的累计目标，不静默重置随机游标或学习率日程。"""
    cfg = validate(cfg)
    session = run.TrainingRun()
    if session.dry_run:
        return None
    prepared = resolve_input(
        prepared, cfg["inputs"]["train"]["preparation"], name="train.preparation"
    )
    record, arrays = read_field_inputs(prepared, "train")
    device = resolve_device(cfg["train"]["device"])
    torch.manual_seed(cfg["seed"])
    model = build_model(cfg["model"]).to(device)
    if cfg["model"].get("include_local_features", False):
        install_prepared_queries(
            model,
            arrays,
            radii=cfg["model"]["radii"],
            neighbors=cfg["model"]["neighbors_in_radius"],
            cache_spec={
                "radii": record["metadata"]["declaration"]["model"]["radii"],
                "neighbors": record["metadata"]["declaration"]["model"]["neighbors_in_radius"],
            },
        )
    batch = partial(
        named_array_batch,
        arrays,
        device=device,
        names=(*binding.INPUT_NAMES, "target", "physical_target"),
    )
    decode, target = binding.objective_binding(record["metadata"]["statistics"])
    objective = partial(
        supervised_objective,
        input_names=binding.INPUT_NAMES,
        decode=decode,
        target_name=target,
        loss=component(cfg["components"]["loss"]),
    )
    optimizer = build_optimizer(
        model, lr=cfg["train"]["lr"], weight_decay=cfg["train"]["weight_decay"]
    )
    stream = EpochBatchStream(
        partial(epoch_records, count=len(arrays["target"])),
        cfg["train"]["batch_size"],
        seed=cfg["seed"],
        source_contract={"fields": record["fields"], "sampling": "pcg64-permutation-v1"},
    )
    scheduler = build_scheduler(
        optimizer,
        policy=cfg["train"]["schedule"],
        updates_per_epoch=(len(arrays["target"]) + cfg["train"]["batch_size"] - 1)
        // cfg["train"]["batch_size"],
        epochs=cfg["train"]["schedule_epochs"],
        end_lr=cfg["train"]["end_lr"],
    )
    # 数组清单的内容摘要加入恢复合同，跨准备目录复制不会改变身份。
    contract = {
        "model": cfg["model"],
        "prepared_fields": record["fields"],
        "metadata": record["metadata"],
        "loss": cfg["components"]["loss"],
        "lr": cfg["train"]["lr"],
        "schedule": cfg["train"]["schedule"],
        "schedule_epochs": cfg["train"]["schedule_epochs"],
        "end_lr": cfg["train"]["end_lr"],
        "weight_decay": cfg["train"]["weight_decay"],
    }
    with cancellation() as stopped:
        result = train_model(
            model=model,
            batch=batch,
            objective=objective,
            optimizer=optimizer,
            stream=stream,
            session=session,
            namespace="train",
            max_grad_norm=None,
            updates=cfg["train"]["updates"],
            contract=contract,
            scheduler=scheduler,
            resume=cfg["inputs"]["train"]["resume"],
            deadline=time.monotonic() + cfg["train"]["seconds"],
            cancelled=stopped,
            checkpoint_every=cfg["train"]["checkpoint_every"],
        )
    result["tail_size"] = len(arrays["target"]) % cfg["train"]["batch_size"]
    result["stream_epoch"] = stream.epoch
    session.report(result, stage="train")
    return result


if __name__ == "__main__":
    from configuration import load_configuration

    raise SystemExit(
        run.launch(
            {"train": train}, script=__file__, only=["train"], config_loader=load_configuration
        )
    )
