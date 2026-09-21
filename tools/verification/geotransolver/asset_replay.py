"""用公开 Task 共享及派生 API 验证完整资产复制，隔离来源后继续消费。"""

from __future__ import annotations

import argparse
import json
import signal
from copy import deepcopy
from pathlib import Path

import ai4e_task as task
import numpy as np
from task_replay import managed

from ai4e_core.abilities.data.save.array_manifest import read_arrays
from ai4e_core.applications.parametric_pde.trainprep import read_field_inputs


def replay(root, preparation):
    """准备由真实 worker 重新交付，派生任务用复制准备/权重和固定结果完成推理。"""
    root = Path(root).resolve()
    accepted = json.loads((root / "acceptance.json").read_text())
    project = root / "project"
    parent_id = accepted["task_run"]["task_id"]
    parent = {"id": parent_id}
    config = task.read_configuration(project, parent_id)["config"]
    original = deepcopy(config)
    config["pipeline"]["stages"] = ["trainprep"]
    config["inputs"]["trainprep"]["dataset"] = str(
        Path(preparation).parent.parent / "rawprep/manifest.json"
    )
    shared = next(
        (a for a in task.list_shared(project) if a.get("name") == "prepared-bundle"), None
    )
    if shared is None:
        summary, prepared_run = managed(project, parent, config)
        manifest = summary["reports"]["trainprep"]["preparation"]
        shared = task.share_run_asset(
            project, prepared_run["id"], "prepared-bundle", manifest, kind="preparation", copy=True
        )
    else:
        task.get_shared(project, shared["id"])
        prepared_run = {"id": shared["source"]["run_id"]}
    shared_path = project / shared["path"]
    checkpoint = json.loads(
        (project / accepted["task_run"]["run_path"] / "summary.json").read_text()
    )["reports"]["train"]["checkpoint"]
    original["inputs"]["train"]["preparation"] = str(shared_path)
    original["inputs"]["infer"]["preparation"] = str(shared_path)
    original["inputs"]["train"]["resume"] = checkpoint
    original["inputs"]["infer"]["checkpoint"] = checkpoint
    original["pipeline"]["stages"] = ["infer", "post"]
    task.replace_configuration(
        project,
        parent_id,
        original,
        revision=task.read_configuration(project, parent_id)["revision"],
    )
    child = task.fork_task(project, parent_id, copy_preparation=True, copy_checkpoints=True)
    copied = task.read_configuration(project, child["id"])["config"]
    copied_preparation = Path(copied["inputs"]["infer"]["preparation"])
    assert copied_preparation != shared_path
    read_field_inputs(
        copied_preparation, "validation" if accepted["case"] == "bumper_beam" else "test"
    )
    # 隐藏共享准备和源权重，子任务必须只依赖自己复制的资产。
    source_roots = [shared_path.parent, Path(checkpoint).parent]
    hidden = []
    try:
        for source in source_roots:
            target = source.with_name(source.name + "-asset-isolated")
            source.rename(target)
            hidden.append((source, target))
        predicted, child_run = managed(project, child, copied)
    finally:
        for source, target in reversed(hidden):
            target.rename(source)
    result_path = predicted["reports"]["infer"]["results"]
    fixed = task.share_run_asset(
        project, child_run["id"], "fixed-result-bundle", result_path, copy=True
    )
    fixed_path = project / fixed["path"]
    _, actual = read_arrays(fixed_path, kind="named-field-result-v1")
    _, expected = read_arrays(root / "fixed-copy/manifest.json", kind="named-field-result-v1")
    np.testing.assert_array_equal(actual["prediction"], expected["prediction"])
    copied["pipeline"]["stages"] = ["post"]
    copied["inputs"]["post"]["results"] = str(fixed_path)
    copied["inputs"]["train"]["preparation"] = None
    copied["inputs"]["infer"]["preparation"] = None
    source = Path(result_path).parent
    hidden_result = source.with_name(source.name + "-isolated")
    source.rename(hidden_result)
    try:
        post, post_run = managed(project, child, copied)
    finally:
        hidden_result.rename(source)
    result = {
        "preparation_copied": True,
        "checkpoint_copied": True,
        "prediction_max_difference": 0.0,
        "source_isolated": True,
        "prepared_run": prepared_run["id"],
        "child_run": child_run["id"],
        "post_run": post_run["id"],
        "shared_preparation": shared,
        "shared_results": fixed,
        "post": post["reports"]["post"],
    }
    (root / "asset-acceptance.json").write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":

    def cancelled(signum, frame):
        raise KeyboardInterrupt(f"资产验收停止信号 {signum}")

    signal.signal(signal.SIGTERM, cancelled)
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--preparation", required=True)
    args = parser.parse_args()
    replay(args.root, args.preparation)
