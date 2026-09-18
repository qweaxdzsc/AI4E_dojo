"""SafeDiffCon 研究步骤，可独立执行或由 pipeline 交接。"""

from configuration import component, load_configuration, plain

from ai4e_contrib.application.pde_control.safediffcon.handoff import register_splits
from ai4e_core import run
from ai4e_core.applications.pde_control.rawprep import materialize


def rawprep(cfg):
    """读取原数据，独立发布三个物理分片。"""
    cfg = plain(cfg, stage="rawprep")
    session = run.TrainingRun()
    if session.dry_run:
        return None
    output = session.output_dir("rawprep") / "physical"
    value = materialize(
        cfg["data"]["root"], output, reader=component(cfg["components"]["reader"]), case=cfg["case"]
    )
    register_splits(session, value, stage="rawprep", kind="dataset")
    session.report({"physical": value}, stage="rawprep")
    return value


if __name__ == "__main__":
    raise SystemExit(
        run.launch(
            {"rawprep": rawprep},
            script=__file__,
            only=["rawprep"],
            config_loader=load_configuration,
        )
    )
