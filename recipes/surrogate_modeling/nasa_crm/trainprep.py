"""准备拟合特征并冻结训练统计，交付自包含数组与身份。"""

from configuration import load_configuration, validate

from ai4e_contrib.application.surrogate_modeling.preparation import prepare_nasa
from ai4e_core import run
from ai4e_core.applications.base.array_assets import record_bundle
from ai4e_core.base.config.conventions import resolve_input


def trainprep(cfg):
    """NASA 只读取全局属性；双圆柱仅在训练快照上拟合一次 POD。"""
    cfg = validate(cfg)
    session = run.TrainingRun()
    if session.dry_run:
        return None
    train_h5 = resolve_input(
        None, cfg["inputs"]["trainprep"]["train_h5"], name="trainprep.train_h5"
    )
    test_h5 = resolve_input(None, cfg["inputs"]["trainprep"]["test_h5"], name="trainprep.test_h5")
    prepared = prepare_nasa(train_h5, test_h5, session.output_dir("trainprep") / "prepared")
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
