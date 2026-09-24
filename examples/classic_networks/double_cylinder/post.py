"""只读固定数组，评价有效域并消费用户派生输出。"""

from configuration import component, load_configuration, validate

from ai4e_contrib.application.classic_networks.prediction import evaluate
from ai4e_core import run
from ai4e_core.abilities.data.save.array_manifest import digest
from ai4e_core.applications.base.array_assets import record_bundle
from ai4e_core.base.config.conventions import resolve_input


def post(cfg, results=None):
    """无需网络或检查点即可复算物理指标，不设精度改善门槛。"""
    cfg = validate(cfg)
    session = run.TrainingRun()
    if session.dry_run:
        return None
    results = resolve_input(results, cfg["inputs"]["post"]["results"], name="post.results")
    report = evaluate(
        results, session.output_dir("post"), consume=component(cfg["components"]["consume"])
    )
    record_bundle(session, "results", results, kind="other", stage="post")
    session.record_asset(
        "metrics", session.output_dir("post") / "metrics.json", kind="other", stage="post"
    )
    for metric in report["field_metrics"]:
        session.record_metric(
            "mse_" + metric["field"],
            metric["mse"],
            stage="post",
            assets=[results],
            semantics={
                "field": metric["field"],
                "unit": metric["unit"],
                "split": "test",
                "statistic": "sample_equal_mean_mse",
                "data_identity": digest(results),
                "space": "physical-valid-domain",
            },
        )
    session.report(report, stage="post")
    return report


if __name__ == "__main__":
    raise SystemExit(
        run.launch({"post": post}, script=__file__, only=["post"], config_loader=load_configuration)
    )
