"""真实 wheel 的外部复制、direct-core/Task、恢复及固定结果隔离消费。"""

from __future__ import annotations

import argparse
import json
import shutil
import signal
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

import ai4e_task as task
import numpy as np
import torch
import yaml


def equal(a, b):
    """只比较科学状态，不把不同管理路径混入一致性结论。"""
    if isinstance(a, torch.Tensor):
        torch.testing.assert_close(a, b, atol=0, rtol=0)
    elif isinstance(a, np.ndarray):
        np.testing.assert_array_equal(a, b)
    elif isinstance(a, dict):
        assert a.keys() == b.keys()
        for key in a:
            equal(a[key], b[key])
    elif isinstance(a, (list, tuple)):
        assert len(a) == len(b)
        for x, y in zip(a, b, strict=True):
            equal(x, y)
    else:
        assert a == b, (a, b)


def direct(code, cfg, label):
    """同一复制脚本从其他工作目录启动，核对真正结果而非导入。"""
    (code / "config.yaml").write_text(yaml.safe_dump(cfg, sort_keys=False))
    process = subprocess.run(
        [
            "uv",
            "run",
            "--no-project",
            "--python",
            sys.executable,
            "python",
            str(code / "pipeline.py"),
        ],
        cwd=code.parent,
        check=False,
        capture_output=True,
        text=True,
        timeout=600,
    )
    (code.parent / (label + "-console.txt")).write_text(process.stdout + process.stderr)
    if process.returncode:
        raise RuntimeError(process.stdout + process.stderr)
    path = max(Path(cfg["run_root"]).glob("*/summary.json"), key=lambda p: p.stat().st_mtime_ns)
    return json.loads(path.read_text())


def managed(project, current, cfg):
    """公开 API 提交/等待 worker；异常时主动停止独立进程组。"""
    task.replace_configuration(
        project,
        current["id"],
        cfg,
        revision=task.read_configuration(project, current["id"])["revision"],
    )
    record = task.submit_run(project, current["id"])
    try:
        done = task.wait_run(project, record["id"], timeout=600, interval=0.2)
        if done["status"] != "succeeded":
            raise RuntimeError(json.dumps(done))
    except BaseException:
        task.stop_run(project, record["id"], timeout=10)
        raise
    return json.loads((project / done["run_path"] / "summary.json").read_text()), done


def replay(case, preparation, root, *, extension=False):
    """正式结构、真实样本两步和恢复到三步；结果目录独立复制后消费。"""
    root = Path(root)
    root.mkdir(parents=True, exist_ok=False)
    code = root / "recipe"
    task.copy_example(
        "recipe_extensions.geotransolver" if extension else "geotransolver." + case, code
    )
    pipeline = code / "pipeline.py"
    source = pipeline.read_text()
    runtime_probe = """    import sys, ai4e_core, ai4e_contrib, ai4e_task
    run.TrainingRun().artifact("runtime.json", {
        "python": sys.executable,
        "core": ai4e_core.__file__, "contrib": ai4e_contrib.__file__,
        "task": ai4e_task.__file__, "script": __file__,
    })
"""
    source = source.replace("    cfg = validate(cfg)", runtime_probe + "    cfg = validate(cfg)", 1)
    pipeline.write_text(source)
    cfg = yaml.safe_load((code / "config.yaml").read_text())
    cfg["pipeline"]["stages"] = ["train", "infer", "post"]
    cfg["inputs"]["train"]["preparation"] = str(preparation)
    cfg["inputs"]["infer"]["preparation"] = str(preparation)
    cfg["train"].update(updates=2, seconds=500, device="mps", checkpoint_every=1)
    cfg["infer"]["device"] = "mps"
    cfg["run_root"] = str(root / "direct-runs")
    cfg["data_root"] = str(root / "direct-data")
    if extension:
        cfg["components"].update(
            loss="variants.squared_relative_loss",
            derived="variants.error_field",
            consume="variants.consume_error",
        )
    project = root / "project"
    task.create_project(project)
    current = task.new_task(project, case, source=code, configuration=cfg)
    a = direct(code, cfg, "direct")
    b, done = managed(project, current, cfg)

    def check(a, b):
        first = torch.load(
            a["reports"]["train"]["checkpoint"], map_location="cpu", weights_only=False
        )
        second = torch.load(
            b["reports"]["train"]["checkpoint"], map_location="cpu", weights_only=False
        )
        for key in ["model", "optimizer", "scheduler", "stream", "history", "updates"]:
            equal(first[key], second[key])
        from ai4e_core.abilities.data.save.array_manifest import read_arrays

        _, aa = read_arrays(a["reports"]["infer"]["results"], kind="named-field-result-v1")
        _, bb = read_arrays(b["reports"]["infer"]["results"], kind="named-field-result-v1")
        equal(aa, bb)

    check(a, b)
    acfg = deepcopy(cfg)
    bcfg = deepcopy(cfg)
    for config, summary in [(acfg, a), (bcfg, b)]:
        config["train"]["updates"] = 3
        config["inputs"]["train"]["resume"] = summary["reports"]["train"]["checkpoint"]
    ar = direct(code, acfg, "direct-resume")
    br, done = managed(project, current, bcfg)
    check(ar, br)
    uninterrupted_cfg = deepcopy(cfg)
    uninterrupted_cfg["train"]["updates"] = 3
    uninterrupted = direct(code, uninterrupted_cfg, "uninterrupted")
    check(ar, uninterrupted)
    fixed = root / "fixed-copy"
    source = Path(ar["reports"]["infer"]["results"]).parent
    shutil.copytree(source, fixed)
    # 原推理目录被隔离，post 无任何模型/准备输入仍须成功。
    hidden = source.with_name(source.name + "-isolated")
    source.rename(hidden)
    postcfg = deepcopy(cfg)
    postcfg["pipeline"]["stages"] = ["post"]
    postcfg["inputs"]["post"]["results"] = str(fixed / "manifest.json")
    postcfg["inputs"]["train"]["preparation"] = None
    postcfg["inputs"]["infer"]["preparation"] = None
    try:
        post = direct(code, postcfg, "independent-post")
    finally:
        hidden.rename(source)
    if extension:
        base = np.load(root.parent / "darcy/fixed-copy/prediction.npy")
        variant = np.load(fixed / "prediction.npy")
        difference = float(np.max(np.abs(base - variant)))
        if difference == 0:
            raise AssertionError("替换损失未改变真实预测")
        (root.parent / "extension-comparison.json").write_text(
            json.dumps({"prediction_max_difference": difference, "changed": True}) + "\n"
        )
    import ai4e_contrib
    import ai4e_core
    import ai4e_spec

    runtime = {
        "python": sys.executable,
        "core": ai4e_core.__file__,
        "contrib": ai4e_contrib.__file__,
        "task": task.__file__,
        "spec": ai4e_spec.__file__,
    }
    worker_probe = next((project / done["run_path"]).rglob("runtime.json"))
    worker_runtime = json.loads(worker_probe.read_text())
    assert all(
        Path(worker_runtime[key]).resolve().is_relative_to(Path(sys.prefix).resolve())
        for key in ("core", "contrib", "task")
    )
    assert worker_runtime["python"] == sys.executable
    result = {
        "case": case,
        "extension": extension,
        "same_weights_prediction": True,
        "resume_updates": 3,
        "uninterrupted_equal": True,
        "post": post["reports"]["post"],
        "task_run": done,
        "runtime": runtime,
        "worker_runtime": worker_runtime,
    }
    (root / "acceptance.json").write_text(json.dumps(result, indent=2, default=str) + "\n")
    print(json.dumps({"case": case, "extension": extension, "status": "passed"}))
    return result


if __name__ == "__main__":

    def cancelled(signum, frame):
        raise KeyboardInterrupt(f"验收停止信号 {signum}")

    signal.signal(signal.SIGTERM, cancelled)
    p = argparse.ArgumentParser()
    p.add_argument("--case", required=True)
    p.add_argument("--preparation", required=True)
    p.add_argument("--root", required=True)
    p.add_argument("--extension", action="store_true")
    a = p.parse_args()
    torch.set_num_threads(4)
    replay(a.case, a.preparation, a.root, extension=a.extension)
