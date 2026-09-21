"""只读取 infer 已固定的 rollout 结果和指标，不重新运行或重新评价模型。"""

from __future__ import annotations

import json
from pathlib import Path

from configuration import load_configuration, validate

from ai4e_core import run
from ai4e_core.abilities.data.save.bundle import load_bundle, save_json


def post(cfg, results=None):
    """读取 infer 固定结果并生成只读指标摘要。"""
    cfg = validate(cfg)
    session = run.TrainingRun()
    if session.dry_run:
        return None
    results = results or cfg["inputs"]["post"].get("results")
    if isinstance(results, (str, Path)):
        path = Path(results)
        results = {**json.loads(path.read_text()), "manifest": str(path)}
    if not isinstance(results, dict) or "bundle" not in results:
        raise ValueError("post 需要 infer 的固定结果")
    fixed = load_bundle(results["bundle"])
    metrics = fixed["metrics"]
    samples = fixed["samples"]
    output = session.output_dir("post")
    report = save_json(
        output / "metrics.json",
        {"metrics": metrics, "samples": len(samples), "source": results["manifest"]},
    )
    summary = {"metrics": metrics, "samples": len(samples), "report": report}
    session.report(summary, stage="post")
    return summary


if __name__ == "__main__":
    raise SystemExit(
        run.launch({"post": post}, script=__file__, only=["post"], config_loader=load_configuration)
    )
