"""显式读取拟合矩阵、调用普通拟合函数并保存可重建状态。"""

import time

from configuration import component, fit_context, load_configuration, validate

from ai4e_contrib.application.surrogate_modeling.preparation import read_prepared
from ai4e_core import run
from ai4e_core.abilities.data.save.surrogate import save_state
from ai4e_core.abilities.training.cancellation import cancellation
from ai4e_core.applications.base.array_assets import record_bundle
from ai4e_core.base.config.conventions import resolve_input


def train(cfg, prepared=None):
    """代数求解不伪造 epoch/优化器；仅保存普通数组和声明，不 pickle 模型对象。"""
    cfg = validate(cfg)
    session = run.TrainingRun()
    if session.dry_run:
        return None
    prepared = resolve_input(
        prepared, cfg["inputs"]["train"]["preparation"], name="train.preparation"
    )
    record, arrays = read_prepared(prepared, "train")
    context = fit_context(cfg, prepared, record["metadata"])
    fit = component(cfg["components"]["fit"])
    with cancellation() as stopped:
        _, state, diagnostics = fit(
            cfg["model"]["family"],
            arrays["input"],
            arrays["target"],
            cfg["model"]["parameters"],
            deadline=time.monotonic() + cfg["train"]["seconds"],
            cancelled=stopped,
        )
    checkpoint = save_state(session.output_dir("train") / "fitted", state, context=context)
    record_bundle(session, "fitted_state", checkpoint, kind="checkpoint", stage="train")
    result = {"checkpoint": checkpoint, "diagnostics": diagnostics}
    session.report(result, stage="train")
    return result


if __name__ == "__main__":
    raise SystemExit(
        run.launch(
            {"train": train}, script=__file__, only=["train"], config_loader=load_configuration
        )
    )
