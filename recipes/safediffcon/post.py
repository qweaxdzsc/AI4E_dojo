"""SafeDiffCon 研究步骤，可独立执行或由 pipeline 交接。"""

import json
from pathlib import Path

from configuration import component, load_configuration, plain

from ai4e_contrib.application.pde_control.safediffcon.handoff import register_metrics
from ai4e_core import run
from ai4e_core.applications.pde_control.post import analyze
from ai4e_core.base.config.conventions import resolve_input


def post(cfg, results=None):
    """仅消费固定数组，重复评价不更新网络或调用响应求解器。"""
    cfg = plain(cfg, stage="post")
    session = run.TrainingRun()
    if session.dry_run:
        return None
    results = resolve_input(results, cfg["post"]["results"], name="post.results")
    if not results:
        raise ValueError("post 缺少固定推理结果")
    output = session.output_dir("post") / "analysis"
    evaluate = component(cfg["components"]["metrics"])
    value = analyze(results, output, evaluate=evaluate)
    register_metrics(
        session, results, json.loads(Path(value).read_text())["metrics"], evaluate=evaluate
    )
    session.record_asset(
        "metrics", value, kind="other", stage="post", dependencies=[Path(results).parent]
    )
    session.report({"metrics_file": value}, stage="post")
    return value


if __name__ == "__main__":
    raise SystemExit(
        run.launch({"post": post}, script=__file__, only=["post"], config_loader=load_configuration)
    )
