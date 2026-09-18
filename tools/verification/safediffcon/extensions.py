"""在仓库外复制研究模板，实际执行网络、约束与派生字段变体。"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import yaml


def execute(root, python):
    """每组在独立目录运行，失败立即结束，整组由外层预算监督。"""
    repository = Path(__file__).resolve().parents[3]
    root = Path(root).resolve()
    root.mkdir(parents=True, exist_ok=False)
    records = {}
    for variant in ("baseline", "small_model", "safety", "derived"):
        destination = root / variant
        shutil.copytree(
            repository / "recipes/safediffcon",
            destination,
            ignore=shutil.ignore_patterns("__pycache__"),
        )
        shutil.copy2(
            repository / "examples/recipe_extensions/safediffcon/variants.py",
            destination / "variants.py",
        )
        cfg = yaml.safe_load((repository / "examples/safediffcon/burgers/quick.yaml").read_text())
        cfg["run_root"] = str(root / "runs" / variant)
        cfg["data_root"] = str(root / "data" / variant)
        cfg["train"]["updates"] = 2
        cfg["posttrain"].update(updates_per_round=2, subset_size=32, calibration_samples=4)
        cfg["infer"]["test_samples"] = 2
        if variant == "small_model":
            cfg["model"]["dim"] = 32
            cfg["components"]["model"] = "variants.small_model"
        if variant == "safety":
            cfg["components"]["guide"] = "variants.stricter_safety"
        if variant == "derived":
            cfg["components"]["derived"] = "variants.safety_margin"
        config = destination / "config.yaml"
        config.write_text(yaml.safe_dump(cfg, sort_keys=False))
        with (root / f"{variant}.log").open("w") as log:
            subprocess.run(
                [
                    "uv",
                    "run",
                    "--no-project",
                    "--python",
                    python,
                    "python",
                    str(destination / "pipeline.py"),
                    "--config",
                    str(config),
                ],
                cwd=root,
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
                stdout=log,
                stderr=subprocess.STDOUT,
                check=True,
            )
        summary = json.loads(next((root / "runs" / variant).glob("*/summary.json")).read_text())
        records[variant] = summary["reports"]["infer"]["results"]
    from ai4e_core.applications.pde_control.contracts import read_arrays

    baseline, base = read_arrays(records["baseline"], kind="control_results_v1")
    _, safety = read_arrays(records["safety"], kind="control_results_v1")
    delta = float(np.max(np.abs(base["controls"] - safety["controls"])))
    if delta == 0:
        raise AssertionError("安全变体未改变实际生成控制")
    derived, values = read_arrays(records["derived"], kind="control_results_v1")
    np.testing.assert_allclose(
        values["safety_margin"], 0.8 - np.abs(values["response"]).max(-1), rtol=0, atol=0
    )
    assert derived["metadata"]["derived_fields"]["safety_margin"]["units"] == "u"
    assert values["safety_margin_valid"].all()
    report = json.loads(
        next((root / "data" / "derived").glob("*/post/analysis/metrics.json")).read_text()
    )
    assert report["derived"]["safety_margin"]["minimum"] == float(values["safety_margin"].min())
    import torch

    weights = torch.load(baseline["metadata"]["checkpoint"], weights_only=False, map_location="cpu")
    smaller, _ = read_arrays(records["small_model"], kind="control_results_v1")
    small_weights = torch.load(
        smaller["metadata"]["checkpoint"], weights_only=False, map_location="cpu"
    )
    assert (
        weights["contract"]["model"]["dim"] == 64
        and small_weights["contract"]["model"]["dim"] == 32
    )

    def count(state):
        return sum(x.numel() for x in state["model"].values())

    assert count(small_weights) < count(weights)
    import ai4e_contrib
    import ai4e_core

    payload = {
        "status": "passed",
        "cases": records,
        "control_delta": delta,
        "dim64_state_elements": count(weights),
        "dim32_state_elements": count(small_weights),
        "derived_report": report,
        "installed_core": ai4e_core.__file__,
        "installed_contrib": ai4e_contrib.__file__,
        "root": str(root),
    }
    (root / "acceptance.json").write_text(json.dumps(payload, indent=2))
    print({k: v for k, v in payload.items() if k not in ("cases", "derived_report")})


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--python", default=sys.executable)
    args = parser.parse_args()
    execute(args.root, args.python)
