"""核验完整发布数据，保存只读来源的自包含副本。"""

from configuration import load_configuration, validate

from ai4e_contrib.application.datasets.geothermal_cmg.adapter import audit
from ai4e_core import run
from ai4e_core.applications.geothermal.data import publish_dataset, record_bundle


def rawprep(cfg):
    cfg = validate(cfg)
    session = run.TrainingRun()
    if session.dry_run:
        return None
    source = cfg["inputs"]["rawprep"]["source"]
    if source is None:
        raise ValueError("请先绑定 inputs.rawprep.source")
    result = publish_dataset(source, session.output_dir("rawprep"), inspect=audit)
    record_bundle(session, result, kind="dataset", stage="rawprep")
    session.report({"dataset": result}, stage="rawprep")
    return result


if __name__ == "__main__":
    raise SystemExit(
        run.launch(
            {"rawprep": rawprep},
            script=__file__,
            only=["rawprep"],
            config_loader=load_configuration,
        )
    )
