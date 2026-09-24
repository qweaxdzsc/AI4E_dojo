"""显式交接物理输入、训练统计和模型独立准备。"""

from configuration import load_configuration, validate

from ai4e_contrib.application.operator_learning.preparation import prepare
from ai4e_core import run
from ai4e_core.applications.base.array_assets import record_bundle
from ai4e_core.base.config.conventions import resolve_input


def trainprep(cfg, physical=None):
    """归一化仅拟合训练分片，不以模型结构限制共享准备。"""
    cfg = validate(cfg)
    session = run.TrainingRun()
    if session.dry_run:
        return None
    physical = resolve_input(
        physical, cfg["inputs"]["trainprep"]["dataset"], name="trainprep.dataset"
    )
    prepared = prepare(physical, session.output_dir("trainprep"), cfg["dataset"], session)
    record_bundle(session, "preparation", prepared, kind="preparation", stage="trainprep")
    session.report({"preparation": prepared}, stage="trainprep")
    return prepared


if __name__ == "__main__":
    raise SystemExit(
        run.launch(
            {"trainprep": trainprep},
            script=__file__,
            only=["trainprep"],
            config_loader=load_configuration,
        )
    )
