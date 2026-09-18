"""模型准备：训练小波数组与原始评价条件分别交接。"""

from configuration import component, load_configuration, validate

from ai4e_contrib.application.spatiotemporal_pde.wdno.handoff import record_arrays, split_inputs
from ai4e_contrib.application.spatiotemporal_pde.wdno.provenance import identity
from ai4e_core import run
from ai4e_core.applications.spatiotemporal_pde.trainprep import prepare_inputs


def trainprep(cfg, physical=None):
    cfg = validate(cfg)
    session = run.TrainingRun()
    if session.dry_run:
        return None
    physical = split_inputs(cfg, "trainprep", physical)
    transform = component(cfg["components"]["transform"])
    prepared = prepare_inputs(
        physical,
        session.output_dir("trainprep"),
        transform,
        declaration={"transform": identity(transform), "version": 1},
    )
    record_arrays(session, prepared, stage="trainprep", kind="preparation")
    session.report(prepared, stage="trainprep")
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
