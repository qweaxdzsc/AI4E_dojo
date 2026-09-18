"""SafeDiffCon 研究步骤，可独立执行或由 pipeline 交接。"""

from configuration import component, load_configuration, plain

from ai4e_contrib.application.pde_control.safediffcon.handoff import (
    register_checkpoint,
    resolve_splits,
)
from ai4e_contrib.application.pde_control.safediffcon.training import pretrain
from ai4e_core import run


def train(cfg, prepared=None):
    """从明确准备开始预训练，恢复权重只影响本次调用。"""
    cfg = plain(cfg, stage="train")
    session = run.TrainingRun()
    if session.dry_run:
        return None
    prepared = resolve_splits(prepared, cfg["data"]["prepared"], name="train")
    if not prepared:
        raise ValueError("train 缺少模型准备")
    checkpoint = pretrain(
        cfg,
        prepared,
        construct=component(cfg["components"]["model"]),
        objective=component(cfg["components"]["objective"]),
        session=session,
    )
    register_checkpoint(session, checkpoint, stage="train", phase="pretrain")
    return checkpoint


if __name__ == "__main__":
    raise SystemExit(
        run.launch(
            {"train": train}, script=__file__, only=["train"], config_loader=load_configuration
        )
    )
