"""保留冻结统计量，将规范化数据准备为可独立消费的训练输入。"""

from configuration import load_configuration, validate

from ai4e_core import run
from ai4e_core.applications.geothermal.data import prepare_inputs, record_bundle
from ai4e_core.base.config.conventions import resolve_input


def trainprep(cfg, dataset=None):
    cfg = validate(cfg)
    session = run.TrainingRun()
    if session.dry_run:
        return None
    source = resolve_input(dataset, cfg["inputs"]["trainprep"]["dataset"], name="trainprep.dataset")
    result = prepare_inputs(source, session.output_dir("trainprep"))
    record_bundle(session, result, kind="preparation", stage="trainprep")
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
