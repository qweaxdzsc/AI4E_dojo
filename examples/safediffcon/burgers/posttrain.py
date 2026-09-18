"""SafeDiffCon 研究步骤，可独立执行或由 pipeline 交接。"""

from configuration import component, load_configuration, plain

from ai4e_contrib.application.pde_control.safediffcon.handoff import (
    register_checkpoint,
    resolve_splits,
)
from ai4e_contrib.application.pde_control.safediffcon.training import posttrain_round
from ai4e_core import run
from ai4e_core.base.config.conventions import resolve_input


def posttrain(cfg, prepared=None, checkpoint=None):
    """显式两轮校准及重加权更新；下轮使用上轮输出。"""
    cfg = plain(cfg, stage="posttrain")
    session = run.TrainingRun()
    if session.dry_run:
        return None
    prepared = resolve_splits(prepared, cfg["data"]["prepared"], name="posttrain")
    checkpoint = resolve_input(
        checkpoint, cfg["posttrain"]["checkpoint"], name="posttrain.checkpoint"
    )
    if not prepared or not checkpoint:
        raise ValueError("posttrain 缺少准备或预训练权重")
    components = {
        "construct": component(cfg["components"]["model"]),
        "objective": component(cfg["components"]["objective"]),
        "session": session,
    }
    first, q = posttrain_round(cfg, prepared, checkpoint, round_index=0, q=0.0, **components)
    second, q = posttrain_round(cfg, prepared, first, round_index=1, q=q, **components)
    register_checkpoint(session, first, stage="posttrain", phase="posttrain_0")
    register_checkpoint(session, second, stage="posttrain", phase="posttrain_1")
    session.report({"checkpoint": second, "q": q}, stage="posttrain")
    return second


if __name__ == "__main__":
    raise SystemExit(
        run.launch(
            {"posttrain": posttrain},
            script=__file__,
            only=["posttrain"],
            config_loader=load_configuration,
        )
    )
