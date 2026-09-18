"""从真实阶段产物补验公共Task复制、CLI和中断恢复；不实现训练算法。"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

import ai4e_task as task
import torch
import yaml

from ai4e_core.abilities.data.save.array_manifest import read_arrays
from tools.verification.wdno.task_replay import (
    assert_equal,
    bind_prepared,
    direct,
    managed,
    wait_task,
)


def cli(project, *args):
    """使用同一解释器运行公开CLI，返回实际JSON收据。"""
    process = subprocess.run(
        [
            "uv",
            "run",
            "--no-project",
            "--python",
            sys.executable,
            "python",
            "-m",
            "ai4e_task",
            *args,
            "--project",
            str(project),
            "--json",
        ],
        check=False,
        capture_output=True,
        text=True,
        timeout=180,
        cwd=Path(project).parent,
    )
    if process.returncode:
        raise AssertionError(process.stdout + process.stderr)
    return json.loads(process.stdout)


def checkpoint_equal(left, right):
    """路径等运行事实单列，训练状态与科学合同逐值核对。"""
    a, b = [torch.load(p, map_location="cpu", weights_only=False) for p in (left, right)]
    for key in (
        "model",
        "optimizer",
        "scheduler",
        "ema",
        "stream",
        "history",
        "updates",
        "python_rng",
        "numpy_rng",
        "torch_rng",
        "contract",
        "algorithm_state",
    ):
        assert_equal(a[key], b[key])
    assert a["updates"] == 3


def exercise_management(staged_root: Path) -> dict:
    """复用本次小切片，创建复制分支和两个真实中断运行并核验。"""
    staged_root = Path(staged_root).resolve()
    acceptance = json.loads((staged_root / "acceptance.json").read_text())
    project = Path(acceptance["project"])
    current = task.get_task(project, acceptance["task_id"])
    cfg = yaml.safe_load((staged_root / "recipe/config.yaml").read_text())
    cfg["pipeline"]["stages"] = ["rawprep", "trainprep", "train", "infer", "post"]
    for stage in ("trainprep", "train", "infer", "post"):
        cfg["inputs"][stage] = dict.fromkeys(cfg["inputs"][stage])
    cfg["train"]["updates"] = 2
    summary, produced = managed(project, current, cfg)
    original_reports = summary["reports"]
    child = task.fork_task(
        project,
        current["id"],
        source="run",
        run_id=produced["id"],
        copy_datasets=True,
        copy_preparation=True,
        copy_checkpoints=True,
    )

    def copied(suffix):
        matches = [v for k, v in child["copied_outputs"].items() if k.endswith(suffix)]
        assert len(matches) == 1, suffix
        item = matches[0]
        assert not item["external"]
        return str(project / item["path"])

    prepared = {s: copied(f"-trainprep-{s}") for s in ("train", "validation", "test")}
    physical = {s: copied(f"-rawprep-{s}") for s in ("train", "validation", "test")}
    checkpoint = copied("-train-train-latest")
    for stage in cfg["inputs"]:
        cfg["inputs"][stage] = dict.fromkeys(cfg["inputs"][stage])
    bind_prepared(cfg, {"trainprep": prepared})
    cfg["pipeline"]["stages"] = ["train", "infer", "post"]
    cfg["inputs"]["train"]["resume"] = checkpoint
    cfg["train"]["updates"] = 3
    parent_data = project / produced["data_path"]
    hidden_data = parent_data.with_name(parent_data.name + ".test-hidden")
    parent_weights = Path(original_reports["train"]["checkpoint"])
    hidden_weights = parent_weights.with_suffix(".test-hidden")
    data_hidden = weights_hidden = False
    try:
        parent_data.rename(hidden_data)
        data_hidden = True
        parent_weights.rename(hidden_weights)
        weights_hidden = True
        for reference in physical.values():
            read_arrays(reference, kind="spatiotemporal-physical-v1")
        copied_summary, copied_run = managed(project, child, cfg)
        assert copied_summary["reports"]["train"]["updates"] == 3
    finally:
        if weights_hidden:
            hidden_weights.rename(parent_weights)
        if data_hidden:
            hidden_data.rename(parent_data)
    # 字节不重写，冻结准备的来源路径只作历史记录，不成为实际消费依赖。
    reference_cfg = deepcopy(cfg)
    bind_prepared(reference_cfg, original_reports)
    reference_cfg["inputs"]["train"]["resume"] = str(parent_weights)
    reference = direct(staged_root / "recipe", reference_cfg)
    checkpoint_equal(
        reference["reports"]["train"]["checkpoint"],
        copied_summary["reports"]["train"]["checkpoint"],
    )

    values = Path(prepared["train"]).parent / "values.npy"
    before = values.read_bytes()
    broken = deepcopy(cfg)
    broken["pipeline"]["stages"] = ["train"]
    try:
        values.write_bytes(before + b"changed")
        try:
            managed(project, child, broken)
        except (ValueError, AssertionError) as error:
            copy_failure = str(error)
        else:
            raise AssertionError("篡改复制数组后仍成功")
    finally:
        values.write_bytes(before)

    # 仅在验收副本注入停止信号；两侧仍使用同一真实损失，目标均为3次更新。
    code = staged_root / "recovery-recipe"
    shutil.copytree(staged_root / "recipe", code, ignore=shutil.ignore_patterns("__pycache__"))
    objective = cfg["components"]["objective"]
    module, name = objective.rsplit(".", 1)
    (code / "stop_objective.py").write_text(f"""import os
import signal
from {module} import {name} as original

calls = 0

def objective(model, values):
    global calls
    result = original(model, values)
    calls += 1
    if os.environ.get("DOJO_WDNO_TEST_STOP") == "1" and calls == 2:
        os.kill(os.getpid(), signal.SIGTERM)
    return result
""")
    recovery_cfg = deepcopy(cfg)
    recovery_cfg["components"]["objective"] = "stop_objective.objective"
    recovery_cfg["pipeline"]["stages"] = ["train"]
    recovery_cfg["inputs"]["train"]["resume"] = None
    recovery_cfg["run_root"] = str(staged_root / "recovery-direct")
    recovery_cfg["data_root"] = str(staged_root / "recovery-data")
    reference = direct(code, recovery_cfg)
    target = reference["reports"]["train"]["checkpoint"]
    receipts = []
    for mode in ("python", "cli"):
        created = (
            task.new_task(project, "recovery-python", source=code, configuration=recovery_cfg)
            if mode == "python"
            else cli(project, "new", "recovery-cli", "--from", str(code))
        )
        saved_configuration = task.read_configuration(project, created["id"])
        previous_flag = os.environ.get("DOJO_WDNO_TEST_STOP")
        os.environ["DOJO_WDNO_TEST_STOP"] = "1"
        try:
            submitted = (
                task.submit_run(project, created["id"])
                if mode == "python"
                else cli(project, "run", created["id"])
            )
            interrupted = wait_task(project, submitted["id"])
        finally:
            if previous_flag is None:
                os.environ.pop("DOJO_WDNO_TEST_STOP", None)
            else:
                os.environ["DOJO_WDNO_TEST_STOP"] = previous_flag
        assert interrupted["status"] in {"failed", "stopped"}
        initial = project / interrupted["run_path"] / "checkpoints/train/latest.pt"
        initial_state = torch.load(initial, map_location="cpu", weights_only=False)
        assert initial_state["updates"] == 2 and initial_state["status"] == "interrupted"
        resumed = (
            task.resume_run(project, interrupted["id"], checkpoint="train/latest.pt")
            if mode == "python"
            else cli(project, "resume", interrupted["id"], "--checkpoint", "train/latest.pt")
        )
        done = wait_task(project, resumed["id"])
        assert done["status"] == "succeeded", done
        assert done["resumed_from"] == interrupted["id"]
        assert task.read_configuration(project, created["id"]) == saved_configuration
        status = cli(project, "status", done["id"])
        assert status["status"] == "succeeded"
        assert done["version_id"] == interrupted["version_id"] == created["version_id"]
        saved = project / done["run_path"] / "checkpoints/train/latest.pt"
        checkpoint_equal(target, saved)
        receipts.append(
            {
                "mode": mode,
                "task_id": created["id"],
                "interrupted": interrupted["id"],
                "resumed": done["id"],
                "checkpoint": str(saved),
                "states_equal": True,
            }
        )
    result = {
        "passed": True,
        "copied_task": child["id"],
        "source_run": produced["id"],
        "copied_run": copied_run["id"],
        "prepared": prepared,
        "physical": physical,
        "copied_checkpoint": checkpoint,
        "original_locations_hidden": True,
        "copy_states_equal": True,
        "copy_tamper_rejected": bool(copy_failure),
        "recovery": receipts,
        "version_count": len(task.get_lineage(project)),
    }
    assert result["version_count"] == 4  # 原任务、复制分支、两个CLI/API恢复任务
    (staged_root / "management.json").write_text(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--staged-root", type=Path, required=True)
    exercise_management(parser.parse_args().staged_root)
