"""最终wheel从500次更新权重预测、Task独立post及清理后保留结果消费。"""

import argparse
import json
import sys
from pathlib import Path

import ai4e_task as task
import numpy as np
import yaml
from installed import direct

import ai4e_contrib
import ai4e_core
from ai4e_core.abilities.data.save.array_manifest import read_arrays


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("root")
    parser.add_argument("config")
    parser.add_argument("source_results")
    args = parser.parse_args()
    root = Path(args.root)
    root.mkdir(parents=True, exist_ok=False)
    case = root / "case"
    task.copy_example("pcno.double_cylinder", case)
    cfg = yaml.safe_load(Path(args.config).read_text())
    cfg["run_root"] = str(root / "runs")
    cfg["data_root"] = str(root / "data")
    cfg["pipeline"]["stages"] = ["infer", "post"]
    result = direct(case, cfg)
    original = json.loads(Path(args.source_results).read_text())
    replay = json.loads(Path(result["reports"]["infer"]["results"]).read_text())
    for left, right in zip(original["windows"], replay["windows"], strict=True):
        _, a = read_arrays(left, kind="field-window-result-v1")
        _, b = read_arrays(right, kind="field-window-result-v1")
        for key in a:
            np.testing.assert_allclose(a[key], b[key], rtol=1e-5, atol=1e-6)
    project = root / "project"
    task.create_project(project)
    cfg["pipeline"]["stages"] = ["post"]
    cfg["inputs"]["post"]["results"] = result["reports"]["infer"]["results"]
    for stage in ("rawprep", "trainprep", "train", "infer"):
        cfg["inputs"][stage] = {k: None for k in cfg["inputs"][stage]}
    (case / "config.yaml").write_text(yaml.safe_dump(cfg, sort_keys=False))
    item = task.new_task(project, "fixed-post", source=case)
    completed = task.wait_run(project, task.submit_run(project, item["id"])["id"], timeout=120)
    assert completed["status"] == "succeeded", completed
    task_report = json.loads(
        Path(completed["summary"]["reports"]["post"]["comparison"]).read_text()
    )
    direct_report = json.loads(Path(result["reports"]["post"]["comparison"]).read_text())
    # 不同进程的线程归约次序可产生末位差异；使用计划预先规定的CPU容差。
    for variant in direct_report["aggregate"]:
        for field in ("fluid", "structure"):
            for metric in ("mae", "rmse", "relative_l2"):
                np.testing.assert_allclose(
                    task_report["aggregate"][variant][field][metric],
                    direct_report["aggregate"][variant][field][metric],
                    rtol=1e-5,
                    atol=1e-6,
                )
        np.testing.assert_allclose(
            task_report["aggregate"][variant]["divergence_rms"],
            direct_report["aggregate"][variant]["divergence_rms"],
            rtol=1e-5,
            atol=1e-6,
        )
    evidence = {
        "passed": True,
        "direct": result,
        "task": completed,
        "comparison": direct_report,
        "installed": {m.__name__: m.__file__ for m in (ai4e_core, ai4e_contrib, task)},
        "python": sys.executable,
        "weight_contract": "500 updates per final branch",
        "rtol": 1e-5,
        "atol": 1e-6,
    }
    (root / "replay.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n")
    print("final wheel prediction and independent Task post passed", flush=True)


if __name__ == "__main__":
    main()
