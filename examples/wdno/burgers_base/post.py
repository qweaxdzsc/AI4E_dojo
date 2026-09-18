"""仅消费固定结果；指标或派生分析可在这里继续组合。"""

from configuration import component, load_configuration, validate

from ai4e_contrib.application.spatiotemporal_pde.wdno.handoff import (
    record_arrays,
    record_metrics,
    split_inputs,
)
from ai4e_core import run
from ai4e_core.applications.spatiotemporal_pde.post import evaluate


def post(cfg, results=None):
    cfg = validate(cfg)
    session = run.TrainingRun()
    if session.dry_run:
        return None
    results = split_inputs(cfg, "post", results)
    summary = evaluate(results, component(cfg["components"]["metrics"]))
    record_arrays(session, results, stage="post", kind="other")
    record_metrics(session, results, summary, component(cfg["components"]["metrics"]))
    session.report(summary, stage="post")
    session.artifact("wdno-evaluation.json", summary)
    return summary


if __name__ == "__main__":
    raise SystemExit(
        run.launch({"post": post}, script=__file__, only=["post"], config_loader=load_configuration)
    )
