"""独立读回固定预测并评价；新增速度模长字段由同一后处理消费。"""

from configuration import load_configuration, validate

from ai4e_contrib.application.spatiotemporal_pde.pcno.post import metrics, summarize
from ai4e_core import run
from ai4e_core.applications.spatiotemporal_pde.window_results import analyze_windows
from ai4e_core.base.config.conventions import resolve_input


def post(cfg, results=None):
    cfg = validate(cfg)
    session = run.TrainingRun()
    if session.dry_run:
        return None
    source = resolve_input(results, cfg["inputs"]["post"]["results"], name="post.results")
    report = analyze_windows(source, metrics, session.output_dir("post"))
    summary = summarize(report, session.output_dir("post") / "comparison.json")
    session.record_asset("metrics", report, kind="other", stage="post")
    session.record_asset("comparison", summary, kind="other", stage="post")
    session.report({"metrics": report, "comparison": summary, "source": source}, stage="post")
    return report


if __name__ == "__main__":
    raise SystemExit(
        run.launch({"post": post}, script=__file__, only=["post"], config_loader=load_configuration)
    )
