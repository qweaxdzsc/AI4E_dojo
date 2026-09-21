"""显式加载两组权重，预测两场、计算井级量并保存固定结果。"""

from configuration import component, load_configuration, validate

from ai4e_contrib.application.geothermal.pcno.inference import load_networks, predict_cases
from ai4e_core import run
from ai4e_core.base.config.conventions import resolve_input


def infer(cfg, preparation=None, trained=None):
    cfg = validate(cfg)
    session = run.TrainingRun()
    if session.dry_run:
        return None
    prepared = resolve_input(
        preparation, cfg["inputs"]["infer"]["preparation"], name="infer.preparation"
    )
    networks = None
    if cfg["infer"]["source"] != "author18":
        checkpoints = resolve_input(
            trained, cfg["inputs"]["infer"]["checkpoints"], name="infer.checkpoints"
        )
        networks = load_networks(
            cfg, prepared, checkpoints, component(cfg["components"]["network"])
        )
    results = predict_cases(cfg, prepared, networks, session=session)
    session.report({"results": results, "source": cfg["infer"]["source"]}, stage="infer")
    return results


if __name__ == "__main__":
    raise SystemExit(
        run.launch(
            {"infer": infer}, script=__file__, only=["infer"], config_loader=load_configuration
        )
    )
