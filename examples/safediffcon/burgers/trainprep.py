"""SafeDiffCon 研究步骤，可独立执行或由 pipeline 交接。"""

from configuration import component, load_configuration, plain

from ai4e_contrib.application.pde_control.safediffcon.handoff import register_splits, resolve_splits
from ai4e_core import run
from ai4e_core.applications.pde_control.trainprep import prepare


def trainprep(cfg, physical=None):
    """物理分片转换为模型准备，保留物理目标。"""
    cfg = plain(cfg, stage="trainprep")
    session = run.TrainingRun()
    if session.dry_run:
        return None
    physical = resolve_splits(physical, cfg["data"]["physical"], name="trainprep")
    if not physical:
        raise ValueError("trainprep 缺少明确物理清单")
    output = session.output_dir("trainprep") / "prepared"
    value = prepare(
        physical, output, transform=component(cfg["components"]["transform"]), case=cfg["case"]
    )
    register_splits(session, value, stage="trainprep", kind="preparation")
    session.report({"prepared": value}, stage="trainprep")
    return value


if __name__ == "__main__":
    raise SystemExit(
        run.launch(
            {"trainprep": trainprep},
            script=__file__,
            only=["trainprep"],
            config_loader=load_configuration,
        )
    )
