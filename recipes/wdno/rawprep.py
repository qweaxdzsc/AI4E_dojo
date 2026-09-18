"""物理轨迹划分，不生成模型输入。"""

from configuration import component, load_configuration, validate

from ai4e_contrib.application.spatiotemporal_pde.wdno.handoff import record_arrays
from ai4e_core import run
from ai4e_core.applications.spatiotemporal_pde.rawprep import prepare_physical


def rawprep(cfg):
    cfg = validate(cfg)
    session = run.TrainingRun()
    if session.dry_run:
        return None
    physical = prepare_physical(
        component(cfg["components"]["reader"]),
        {
            "protocol": cfg["inputs"]["rawprep"]["source"],
            "indices": cfg["inputs"]["rawprep"]["indices"],
        },
        session.output_dir("rawprep"),
    )
    record_arrays(session, physical, stage="rawprep", kind="dataset")
    session.report(physical, stage="rawprep")
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
