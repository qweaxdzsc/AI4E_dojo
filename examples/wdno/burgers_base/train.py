"""按有效更新次数训练；可在正文替换网络和目标函数。"""

from configuration import component, load_configuration, validate

from ai4e_contrib.application.spatiotemporal_pde.wdno.handoff import split_inputs
from ai4e_contrib.application.spatiotemporal_pde.wdno.training import train as fit
from ai4e_core import run
from ai4e_core.abilities.training.cancellation import cancellation


def train(cfg, prepared=None):
    cfg = validate(cfg)
    session = run.TrainingRun()
    if session.dry_run:
        return None
    prepared = split_inputs(cfg, "train", prepared)
    with cancellation() as stopped:
        result = fit(
            cfg,
            prepared,
            construct=component(cfg["components"]["network"]),
            objective=component(cfg["components"]["objective"]),
            session=session,
            cancelled=stopped,
        )

    if result["status"] != "complete":
        raise RuntimeError("训练未完成，已保存完整更新边界；请使用检查点继续")
    return result


if __name__ == "__main__":
    raise SystemExit(
        run.launch(
            {"train": train}, script=__file__, only=["train"], config_loader=load_configuration
        )
    )
