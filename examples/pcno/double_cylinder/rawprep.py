"""核验来源并保存只读轨迹清单，不复制大场数组。"""

from configuration import load_configuration, validate

from ai4e_contrib.application.datasets.gencp.cylinder import describe
from ai4e_core import run


def rawprep(cfg):
    cfg = validate(cfg)
    session = run.TrainingRun()
    if session.dry_run:
        return None
    if cfg["dataset"]["case"] != "double_cylinder":
        raise ValueError("CylinderFlow P1散度未通过1%准入，当前不能交付可训练案例")
    source = cfg["inputs"]["rawprep"]["source"]
    if source is None:
        raise ValueError("请绑定 inputs.rawprep.source")
    result = describe(source, session.output_dir("rawprep") / "dataset.json")
    session.record_asset("dataset", result, kind="dataset", stage="rawprep")
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
