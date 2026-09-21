"""只读固定结果，分别计算物理误差、技术经济表及派生分析。"""

from pathlib import Path

from configuration import load_configuration, validate

from ai4e_contrib.application.geothermal.pcno.post import economic_table
from ai4e_contrib.application.geothermal.pcno.training import component_identity
from ai4e_core import run
from ai4e_core.abilities.data.save.arrays import atomic_path, save_json
from ai4e_core.abilities.eval.relative_field import errors
from ai4e_core.applications.geothermal.post import evaluate_results, read_results
from ai4e_core.base.config.conventions import resolve_input


def post(cfg, results=None):
    cfg = validate(cfg)
    session = run.TrainingRun()
    if session.dry_run:
        return None
    source = resolve_input(results, cfg["inputs"]["post"]["results"], name="post.results")
    record, arrays = read_results(source)
    metrics = evaluate_results(record, arrays)
    table = economic_table(record, arrays, **cfg["post"])
    metrics["economic_undefined_cells"] = {
        name: int(count)
        for name, count in table.replace([float("inf"), float("-inf")], float("nan"))
        .isna()
        .sum()
        .items()
        if count
    }
    output = session.output_dir("post")
    csv = output / "technical_economic.csv"
    with atomic_path(csv) as target:
        table.to_csv(target, index=True)
    save_json(output / "metrics.json", metrics)
    dependencies = [Path(source).parent / r["file"] for r in record["samples"]]
    dependencies.extend(Path(source).parent / r["file"] for r in record.get("derived", {}).values())
    if metrics["mean"]:
        for field, values in metrics["mean"].items():
            for metric, value in values.items():
                units = {
                    "pres": "MPa",
                    "temp": "degC",
                    "Temp_wh": "degC",
                    "Heat_wh": "W",
                    "P_inj": "Pa",
                }
                session.record_metric(
                    field + "_" + metric,
                    value,
                    stage="post",
                    semantics={
                        "field": field,
                        "unit": "1" if metric == "mare" else units[field],
                        "split": record["source"],
                        "statistic": metric + "_years1_20_equal_cases",
                        "data_identity": {
                            "source": record["data_identity"],
                            "samples": [s["id"] for s in record["samples"]],
                        },
                        "definition": component_identity(errors),
                        "paper_protocol_matched": False,
                        "scope": record["scope"],
                    },
                    assets=[source, *dependencies],
                )
    session.record_asset(
        "economic_table",
        csv,
        kind="other",
        stage="post",
        dependencies=[output / "metrics.json"],
        bundle_root=output,
    )
    report = {"metrics": metrics, "csv": str(csv), "metrics_file": str(output / "metrics.json")}
    session.report(report, stage="post")
    return report


if __name__ == "__main__":
    raise SystemExit(
        run.launch({"post": post}, script=__file__, only=["post"], config_loader=load_configuration)
    )
