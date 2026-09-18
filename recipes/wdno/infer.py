"""固定普通权重采样并保存物理场。"""

from configuration import component, load_configuration, validate

from ai4e_contrib.application.spatiotemporal_pde.wdno.handoff import record_arrays, split_inputs
from ai4e_contrib.application.spatiotemporal_pde.wdno.inference import infer as predict
from ai4e_core import run
from ai4e_core.base.config.conventions import resolve_input


def infer(cfg, prepared=None, trained=None):
    cfg = validate(cfg)
    session = run.TrainingRun()
    if session.dry_run:
        return None
    prepared = split_inputs(cfg, "infer", prepared)
    checkpoint = resolve_input(
        trained["checkpoint"] if trained is not None else None,
        cfg["inputs"]["infer"]["checkpoint"],
        name="infer.checkpoint",
    )
    results = predict(
        cfg,
        prepared,
        checkpoint,
        construct=component(cfg["components"]["network"]),
        objective=component(cfg["components"]["objective"]),
        predict=component(cfg["components"]["predict"]),
        derived=component(cfg["components"]["derived"]),
        output=session.output_dir("infer"),
    )
    record_arrays(session, results, stage="infer", kind="other")
    session.report(results, stage="infer")
    return results


if __name__ == "__main__":
    raise SystemExit(
        run.launch(
            {"infer": infer}, script=__file__, only=["infer"], config_loader=load_configuration
        )
    )
