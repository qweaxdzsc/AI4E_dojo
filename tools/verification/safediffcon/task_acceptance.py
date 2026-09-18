"""通过实际安装的 Task 公开 API 验证两例独立阶段，不绕过 worker。"""

import argparse
import hashlib
import json
import time
from pathlib import Path

import ai4e_task as task
import numpy as np
import torch
from omegaconf import OmegaConf


def execute(root: Path, case: str, output: Path) -> None:
    """新建正式任务、真实更新、后训练、推理及禁用模型后的固定结果评价。"""
    from ai4e_core.applications.pde_control.contracts import read_arrays

    repo = Path(__file__).resolve().parents[3]
    output.mkdir(parents=True, exist_ok=False)
    project = output / "project"
    task.create_project(project)
    total = 5000 if case == "burgers" else 8000
    prior = json.loads((root / f"continuation/{case}-dojo-{total}-final/summary.json").read_text())
    cfg = OmegaConf.to_container(
        OmegaConf.load(root / f"continuation/{case}-dojo-{total}.yaml"), resolve=True
    )
    from ai4e_contrib.application.pde_control.safediffcon.migration import migrate_legacy

    cfg = migrate_legacy(cfg, base=root / "continuation")
    cfg["inputs"]["rawprep"]["source"] = None
    for stage in ("train", "posttrain", "infer"):
        cfg["inputs"][stage].update({"preparation_" + k: v for k, v in prior["prepared"].items()})
    cfg["inputs"]["train"]["resume"] = prior["pretrain_checkpoint"]
    cfg["train"]["updates"] = total + 1
    cfg["posttrain"].update(updates_per_round=1, subset_size=8, calibration_samples=4)
    cfg["infer"].update(test_samples=2, batch_size=2)
    cfg["pipeline"] = {"stages": ["train"]}
    if case == "burgers":
        cfg["inputs"]["infer"]["solver_assets"] = None

    task.register_template(project, "safediffcon", repo / "recipes/safediffcon")
    current = task.new_task(project, case, source="safediffcon", configuration=cfg)
    runs = []
    active = None

    def run(stages, overrides=(), *, success=True):
        nonlocal active
        active = task.submit_run(
            project, current["id"], overrides=[f"pipeline.stages=[{','.join(stages)}]", *overrides]
        )
        deadline = time.monotonic() + 240
        while True:
            value = task.wait_run(project, active["id"], timeout=5)
            if value["status"] in {"succeeded", "failed", "stopped", "unknown"}:
                break
            if time.monotonic() > deadline:
                raise TimeoutError("Task 单阶段超出240秒")
        runs.append(value)
        (output / "runs.json").write_text(json.dumps(runs, indent=2))
        active = None
        assert value["status"] == ("succeeded" if success else "failed"), value
        assert value["version_id"] == current["version_id"]
        print(case, stages, value["status"], flush=True)
        return value

    try:
        run(["infer"], success=False)
        trained = run(["train"])
        checkpoint = Path(trained["run_dir"]) / "checkpoints/pretrain/latest.pt"
        state = torch.load(checkpoint, map_location="cpu", weights_only=False)
        before = torch.load(prior["pretrain_checkpoint"], map_location="cpu", weights_only=False)
        assert state["updates"] == total + 1 and state["status"] == "complete"
        assert any(not torch.equal(v, before["model"][k]) for k, v in state["model"].items())
        del state, before
        calibrated = run(["posttrain"], [f"inputs.posttrain.checkpoint={checkpoint}"])
        checkpoint = Path(calibrated["run_dir"]) / "checkpoints/posttrain_1/latest.pt"
        inferred = run(["infer"], [f"inputs.infer.checkpoint={checkpoint}"])
        results = inferred["summary"]["reports"]["infer"]["results"]
        record, arrays = read_arrays(results, kind="control_results_v1")
        assert len(arrays["ids"]) == 2 and np.isfinite(arrays["response"]).all()
        result_hash = hashlib.sha256(Path(results).read_bytes()).hexdigest()
        posted = run(
            ["post"],
            [
                f"inputs.post.results={results}",
                "components.model=unavailable.model",
                "solver.python=/unavailable",
            ],
        )
        metrics = json.loads(Path(posted["summary"]["reports"]["post"]["metrics_file"]).read_text())
        assert metrics["metrics"] == record["metadata"]["metrics"]
        assert hashlib.sha256(Path(results).read_bytes()).hexdigest() == result_hash
        assert not (Path(posted["run_dir"]) / "checkpoints").exists()
        for value in runs:
            assert Path(value["run_dir"]).is_relative_to(project / "tasks" / current["id"] / "runs")
            assert Path(value["data_dir"]).is_relative_to(
                project / "tasks" / current["id"] / "data"
            )
        assert len(task.get_lineage(project)) == 1
        payload = {
            "status": "passed",
            "case": case,
            "task_id": current["id"],
            "project": str(project),
            "training_updates_added": 1,
            "posttraining_updates": [1, 1],
            "samples": 2,
            "results": results,
            "metrics": metrics["metrics"],
            "runs": [{"id": v["id"], "status": v["status"], "stages": v["stages"]} for v in runs],
            "scope": "Task public API, installed packages, real original data and response; integration only, not accuracy evaluation",
        }
        (output / "acceptance.json").write_text(json.dumps(payload, indent=2))
    finally:
        if active is not None:
            task.stop_run(project, active["id"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--case", choices=["burgers", "tokamak"], required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    execute(args.root, args.case, args.output)
