"""实际wheel环境：外部案例direct/Task对照及网络替换、派生字段消费。"""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import ai4e_task as task
import numpy as np
import torch
import yaml

import ai4e_contrib
import ai4e_core
from ai4e_core.abilities.data.save.array_manifest import read_arrays


def direct(case, config):
    """调用复制目录的公开入口并返回本次真实摘要。"""
    (case / "config.yaml").write_text(yaml.safe_dump(config, sort_keys=False))
    result = subprocess.run(
        [
            "uv",
            "run",
            "--no-sync",
            "--no-project",
            "--python",
            sys.executable,
            "python",
            str(case / "pipeline.py"),
            "--config",
            str(case / "config.yaml"),
        ],
        cwd=case.parent,
        capture_output=True,
        text=True,
        check=False,
        env={k: v for k, v in os.environ.items() if k != "PYTHONPATH"},
    )
    (case.parent / (case.name + "-console.log")).write_text(result.stdout + result.stderr)
    if result.returncode:
        raise RuntimeError(result.stdout + result.stderr)
    summaries = sorted(Path(config["run_root"]).glob("*/summary.json"))
    return json.loads(summaries[-1].read_text())


def compare(a, b):
    """比较实际训练权重与固定预测，不只比较导入和退出状态。"""
    ca = json.loads(Path(a["reports"]["train"]["checkpoints"]).read_text())
    cb = json.loads(Path(b["reports"]["train"]["checkpoints"]).read_text())
    max_difference = 0.0
    for key in ca["branches"]:
        sa = torch.load(ca["branches"][key]["path"], weights_only=False)
        sb = torch.load(cb["branches"][key]["path"], weights_only=False)
        for name in sa["model"]:
            torch.testing.assert_close(sa["model"][name], sb["model"][name], rtol=1e-5, atol=1e-6)
            max_difference = max(
                max_difference, float((sa["model"][name] - sb["model"][name]).abs().max())
            )
        assert sa["history"] == sb["history"]
    ra = json.loads(Path(a["reports"]["infer"]["results"]).read_text())
    rb = json.loads(Path(b["reports"]["infer"]["results"]).read_text())
    for pa, pb in zip(ra["windows"], rb["windows"], strict=True):
        _, aa = read_arrays(pa, kind="field-window-result-v1")
        _, bb = read_arrays(pb, kind="field-window-result-v1")
        for key in aa:
            np.testing.assert_allclose(aa[key], bb[key], rtol=1e-5, atol=1e-6)
    return max_difference


def main():
    p = argparse.ArgumentParser()
    p.add_argument("output")
    p.add_argument("source")
    args = p.parse_args()
    root = Path(args.output).resolve()
    root.mkdir(parents=True, exist_ok=False)
    assert str(Path(ai4e_core.__file__).resolve()).startswith(sys.prefix)
    assert str(Path(ai4e_contrib.__file__).resolve()).startswith(sys.prefix)
    assert str(Path(task.__file__).resolve()).startswith(sys.prefix)
    start = time.monotonic()
    case = root / "direct-case"
    task.copy_example("pcno.double_cylinder", case)
    cfg = yaml.safe_load((case / "config.yaml").read_text())
    cfg["train"]["updates"] = 10
    cfg["inputs"]["rawprep"]["source"] = str(Path(args.source).resolve())
    cfg["run_root"] = str(root / "direct-runs")
    cfg["data_root"] = str(root / "direct-data")
    first = direct(case, cfg)
    project = root / "project"
    task.create_project(project)
    item = task.new_task(project, "pcno-cylinder", source=case)
    submitted = task.submit_run(project, item["id"])
    completed = task.wait_run(project, submitted["id"], timeout=180)
    if completed["status"] != "succeeded":
        raise RuntimeError(json.dumps(completed, ensure_ascii=False))
    parity = compare(first, completed["summary"])
    extension = root / "extension-case"
    task.copy_example("extension.pcno_cylinder", extension)
    cfg["components"]["network"] = "local_components.shifted_network"
    cfg["train"]["updates"] = 8
    cfg["loss"]["divergence_weight"] = 0.2
    cfg["run_root"] = str(root / "extension-runs")
    cfg["data_root"] = str(root / "extension-data")
    extended = direct(extension, cfg)
    post = json.loads(Path(extended["reports"]["post"]["metrics"]).read_text())
    assert all("derived_speed" in x["metrics"] for x in post["results"])
    weights = json.loads(Path(extended["reports"]["train"]["checkpoints"]).read_text())
    state = torch.load(weights["branches"]["physics"]["path"], weights_only=False)
    assert (
        state["updates"] == 8
        and state["contract"]["network"]["name"] == "local_components.shifted_network"
    )
    old = torch.load(
        json.loads(Path(first["reports"]["train"]["checkpoints"]).read_text())["branches"][
            "physics"
        ]["path"],
        weights_only=False,
    )
    assert any(not torch.equal(state["model"][k], old["model"][k]) for k in state["model"])
    report = {
        "passed": True,
        "seconds": time.monotonic() - start,
        "python": sys.executable,
        "installed": {m.__name__: m.__file__ for m in (ai4e_core, ai4e_contrib, task)},
        "direct": first,
        "task": completed,
        "extension": extended,
        "max_weight_difference": parity,
        "extension_updates": 8,
        "derived_windows": len(post["results"]),
    }
    (root / "installation.json").write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(
        json.dumps(
            {
                k: report[k]
                for k in (
                    "passed",
                    "seconds",
                    "max_weight_difference",
                    "extension_updates",
                    "derived_windows",
                )
            }
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
