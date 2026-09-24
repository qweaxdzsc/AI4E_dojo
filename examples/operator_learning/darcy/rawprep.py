"""显式绑定真实来源、保存物理输入和登记完整数据资产。"""

from configuration import load_configuration, validate

from ai4e_contrib.application.operator_learning.preparation import physical_source
from ai4e_core import run
from ai4e_core.applications.base.array_assets import record_bundle


def rawprep(cfg):
    """数据源只读，准备产物写本次独立输出目录。"""
    cfg = validate(cfg)
    session = run.TrainingRun()
    if session.dry_run:
        return None
    physical = physical_source(cfg, session.output_dir("rawprep"), session)
    record_bundle(session, "dataset", physical, kind="dataset", stage="rawprep")
    session.report({"dataset": physical}, stage="rawprep")
    return physical


if __name__ == "__main__":
    raise SystemExit(
        run.launch(
            {"rawprep": rawprep},
            script=__file__,
            only=["rawprep"],
            config_loader=load_configuration,
        )
    )
