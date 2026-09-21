"""只消费固定结果和可替换派生数组，不导入网络。"""

from configuration import component, validate

from ai4e_core import run
from ai4e_core.applications.base.array_assets import record_bundle
from ai4e_core.applications.spatiotemporal_pde.post import report_trajectories
from ai4e_core.base.config.conventions import resolve_input


def post(cfg, results=None):
    """CPU float64 评价、表格、误差曲线与场图，记录来源资产。"""
    cfg = validate(cfg)
    session = run.TrainingRun()
    if session.dry_run:
        return None
    results = resolve_input(results, cfg["inputs"]["post"]["results"], name="post.results")
    summary = report_trajectories(
        results,
        session.output_dir("post"),
        time_unit="ms",
        consume=component(cfg["components"]["consume"]),
    )
    record_bundle(session, "fixed-results", results, kind="other", stage="post")
    record_bundle(session, "evaluation", summary["metrics"], kind="other", stage="post")
    for metric in summary["field_metrics"]:
        session.record_metric(
            metric["name"],
            metric["value"],
            stage="post",
            semantics=metric["semantics"],
            assets=[results],
        )
    session.report(summary, stage="post")
    return summary


if __name__ == "__main__":
    from configuration import load_configuration

    raise SystemExit(
        run.launch({"post": post}, script=__file__, only=["post"], config_loader=load_configuration)
    )
