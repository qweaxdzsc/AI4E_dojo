"""显式冻结训练统计及窗口规则，无窗口张量副本。"""

from configuration import load_configuration, validate

from ai4e_contrib.application.datasets.gencp.cylinder import prepare
from ai4e_core import run
from ai4e_core.base.config.conventions import resolve_input


def trainprep(cfg, dataset=None):
    cfg = validate(cfg)
    session = run.TrainingRun()
    if session.dry_run:
        return None
    source = resolve_input(dataset, cfg["inputs"]["trainprep"]["dataset"], name="trainprep.dataset")
    result = prepare(
        source,
        session.output_dir("trainprep") / "preparation.json",
        history=cfg["model"]["history"],
        horizon=cfg["model"]["horizon"],
    )
    session.record_asset("preparation", result, kind="preparation", stage="trainprep")
    session.report({"preparation": result}, stage="trainprep")
    return result


if __name__ == "__main__":
    raise SystemExit(
        run.launch(
            {"trainprep": trainprep},
            script=__file__,
            only=["trainprep"],
            config_loader=load_configuration,
        )
    )
