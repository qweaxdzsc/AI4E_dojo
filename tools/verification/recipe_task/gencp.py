"""GenCP 直接脚本与 Task 的真实短训练、恢复、推理及固定后处理对照。"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import ai4e_task as task
import numpy as np
import torch
import yaml

ROOT = Path(__file__).resolve().parents[3]


def compare(left, right):
    """递归比较数值状态；不比较序列化容器和输出位置。"""
    if isinstance(left, torch.Tensor):
        torch.testing.assert_close(left, right, rtol=1e-4, atol=1e-6)
    elif isinstance(left, dict):
        assert left.keys() == right.keys()
        for key in left:
            compare(left[key], right[key])
    elif isinstance(left, (list, tuple)):
        assert len(left) == len(right)
        for a, b in zip(left, right, strict=True):
            compare(a, b)
    elif isinstance(left, float):
        np.testing.assert_allclose(left, right, rtol=1e-4, atol=1e-6)
    else:
        assert left == right, (left, right)


def execute_case(case, destination):
    """每组累计限时；所有子进程使用同一当前解释器和安装环境。"""
    prior = 0.0
    for report in destination.parent.glob("*/report.json"):
        if report.parent == destination:
            continue
        records = json.loads(report.read_text())
        for record in records if isinstance(records, list) else [records]:
            if record.get("case") == case:
                prior += record.get("attempt_seconds", record.get("seconds", 0.0))
    started = time.monotonic() - prior
    folder = destination / case
    folder.mkdir(parents=True, exist_ok=False)
    recipe = folder / "direct_recipe"
    shutil.copytree(ROOT / "recipes/gencp", recipe)
    cfg = yaml.safe_load((ROOT / "examples/gencp" / case / "config.yaml").read_text())
    cfg["data"].update(train_count=4, val_count=1)
    cfg["train"].update(updates=3, updates_per_run=2, evaluate_every=2, device="cpu", seconds=1200)
    cfg["infer"]["device"] = "cpu"
    cfg["post"]["plots"] = False
    cfg["train"]["snapshot"] = False
    cfg["run_root"] = str(folder / "direct_runs")
    cfg["data_root"] = str(folder / "direct_data")
    config_path = recipe / "config.yaml"
    project = folder / "project"
    task.create_project(project)

    def direct(stage, config):
        config["pipeline"]["stages"] = [stage]
        config_path.write_text(yaml.safe_dump(config, sort_keys=False))
        remaining = 10800 - (time.monotonic() - started)
        if remaining < 300:
            raise TimeoutError("175分钟之后不启动新计算")
        with (folder / f"direct-{stage}-{config['train']['updates']}.log").open("w") as log:
            subprocess.run([sys.executable, str(recipe / "pipeline.py"), "--config", str(config_path)],
                cwd=folder, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=remaining,
                env={**os.environ, "OMP_NUM_THREADS": "2", "MKL_NUM_THREADS": "2"})
        runs = sorted((folder / "direct_runs").glob("*/summary.json"), key=lambda p:p.stat().st_mtime_ns)
        return json.loads(runs[-1].read_text())

    physical = direct("rawprep", cfg)["reports"]["rawprep"]["physical_root"]
    cfg["inputs"]["trainprep"]["dataset"] = physical
    preparation = direct("trainprep", cfg)["reports"]["trainprep"]["preparation"]
    for stage in ("train", "infer", "single"):
        cfg["inputs"][stage]["preparation"] = preparation
    cfg["pipeline"]["stages"] = ["train"]
    config_path.write_text(yaml.safe_dump(cfg, sort_keys=False))
    managed = task.new_task(project, case, source=recipe)

    def managed_run(stage, overrides=()):
        remaining = 10800 - (time.monotonic() - started)
        if remaining < 300:
            raise TimeoutError("175分钟之后不启动新计算")
        value = task.submit_run(project, managed["id"], overrides=[f"pipeline.stages=[{stage}]", *overrides])
        result = task.wait_run(project, value["id"], timeout=remaining)
        if result["status"] not in {"succeeded", "failed", "stopped"}:
            task.stop_run(project, result["id"])
        if result["status"] != "succeeded":
            raise RuntimeError(json.dumps(result, default=str))
        return result["summary"]

    managed_physical = managed_run("rawprep")["reports"]["rawprep"]["physical_root"]
    managed_prepared = managed_run("trainprep", [f"inputs.trainprep.dataset={managed_physical}"])["reports"]["trainprep"]["preparation"]
    assert json.loads(Path(preparation).read_text()) == json.loads(Path(managed_prepared).read_text())
    task.save_configuration(project, managed["id"], {"inputs": {
        stage: {"preparation": managed_prepared} for stage in ("train", "infer", "single")
    }}, revision=task.read_configuration(project, managed["id"])["revision"])
    left = direct("train", cfg)["reports"]["train"]["checkpoints"]
    right = managed_run("train")["reports"]["train"]["checkpoints"]
    for updates in (2, 3):
        if updates == 3:
            cfg["train"]["updates_per_run"] = 1
            cfg["inputs"]["train"]["resume"] = left
            left = direct("train", cfg)["reports"]["train"]["checkpoints"]
            right = managed_run("train", ["train.updates_per_run=1", f"inputs.train.resume={right}"])["reports"]["train"]["checkpoints"]
        a, b = json.loads(Path(left).read_text()), json.loads(Path(right).read_text())
        for field in a["fields"]:
            x = torch.load(a["fields"][field]["path"], map_location="cpu", weights_only=False)
            y = torch.load(b["fields"][field]["path"], map_location="cpu", weights_only=False)
            for key in ("model", "optimizer", "scheduler", "ema", "updates", "stream"):
                if key in x:
                    compare(x[key], y[key])
    cfg["inputs"]["single"]["checkpoint"] = left
    single_a = direct("single", cfg)["reports"]["single"]["single_results"]
    single_b = managed_run("single", [f"inputs.single.checkpoint={right}"])["reports"]["single"]["single_results"]
    a, b = json.loads(Path(single_a).read_text()), json.loads(Path(single_b).read_text())
    for field in a["fields"]:
        for role in ("prediction", "target"):
            np.testing.assert_allclose(np.load(Path(single_a).parent / a["fields"][field][role]),
                np.load(Path(single_b).parent / b["fields"][field][role]), rtol=1e-4, atol=1e-6)
    cfg["inputs"]["infer"]["checkpoint"] = left
    x = direct("infer", cfg)["reports"]["infer"]["results"]
    y = managed_run("infer", [f"inputs.infer.checkpoint={right}"])["reports"]["infer"]["results"]
    a, b = json.loads(Path(x).read_text()), json.loads(Path(y).read_text())
    for field in a["fields"]:
        for role in ("prediction", "target"):
            np.testing.assert_allclose(np.load(Path(x).parent / a["fields"][field][role]),
                np.load(Path(y).parent / b["fields"][field][role]), rtol=1e-4, atol=1e-6)
    cfg["inputs"]["post"]["results"] = x
    post_a = direct("post", cfg)["reports"]["post"]["metrics"]
    post_b = managed_run("post", [f"inputs.post.results={y}"])["reports"]["post"]["metrics"]
    compare(json.loads(Path(post_a).read_text())["metrics"], json.loads(Path(post_b).read_text())["metrics"])
    return {"case": case, "status": "passed", "seconds": time.monotonic()-started,
            "preparation": preparation, "direct_results": x, "task_results": y,
            "scope": "rawprep_prepare_two_updates_resume_to_three_single_infer_post; not_paper_accuracy"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--case", action="append")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    cases = args.case or [p.name for p in sorted((ROOT / "examples/gencp").iterdir()) if (p/"config.yaml").exists()]
    report = []
    for case in cases:
        start = time.monotonic()
        try:
            value = execute_case(case, args.output)
        except Exception as exc:  # noqa: BLE001 - 失败也必须计入同一计算账本
            value = {"case": case, "status": "failed", "error": str(exc), "seconds": time.monotonic()-start}
        value["attempt_seconds"] = time.monotonic() - start
        report.append(value)
        (args.output / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2))
        print(json.dumps(value, ensure_ascii=False), flush=True)
    return int(any(r["status"] != "passed" for r in report))


if __name__ == "__main__":
    raise SystemExit(main())
