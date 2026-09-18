"""在外部复制的 GenCP recipe 旁运行条件变体与派生字段消费。"""


from configuration import load_configuration, plain
from custom import speed_pair
from infer import infer

from ai4e_core import run
from ai4e_core.applications.coupled_physics.infer import save_results
from ai4e_core.applications.coupled_physics.post import (
    evaluate_fields,
    export_analysis,
    read_results,
)


def extension(cfg):
    """改条件后真实生成；保存速度，再读回评价，不借用内存代替交接。"""
    cfg = plain(cfg)
    cfg["components"]["fluid_condition"] = "custom.averaged_fluid_condition"
    results = run.stage("infer", infer, cfg)
    record, pairs = read_results(results)
    prediction, target = speed_pair(pairs["fluid"])
    output = run.TrainingRun().output_dir("extension") / "speed"
    reference = save_results(
        {"speed": prediction},
        {"speed": target},
        output,
        metadata={
            "derived_from": record["content_id"],
            "field": "speed",
            "unit": "m/s",
            "variant": "averaged_fluid_condition",
        },
    )
    run.TrainingRun().record_asset("speed", reference, kind="other", stage="extension", dependencies=[output])
    frozen, fixed = read_results(reference)
    metrics = evaluate_fields(fixed)
    report = export_analysis(fixed, metrics, output / "analysis", metadata=frozen, plots=True)
    run.TrainingRun().report(
        {"variant_results": results, "speed_results": reference, "metrics": report},
        stage="extension",
    )
    return report


if __name__ == "__main__":
    raise SystemExit(
        run.launch(
            {"extension": extension},
            script=__file__,
            only=["extension"],
            config_loader=load_configuration,
        )
    )
