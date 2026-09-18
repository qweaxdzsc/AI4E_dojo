"""经 Task 公开入口复核控制流程；真实数据子集只用于工程交接验收。"""

import argparse
import hashlib
import json
import time
from pathlib import Path

import ai4e_task as task
import numpy as np
import torch
from omegaconf import OmegaConf

from ai4e_core.applications.pde_control.contracts import read_arrays, save_arrays


def exercise(project: Path, recipe: Path, configuration: dict, *, timeout=180) -> dict:
    """创建任务，独立准备/训练/后训练/推理/post，再验证组合运行与失败。"""
    task.create_project(project)
    item = task.new_task(
        project, "SafeDiffCon Task 验证", source=recipe, configuration=configuration
    )
    task_id = item["id"]
    records = []

    def execute(stages, patch=None, *, succeeds=True):
        current = task.read_configuration(project, task_id)
        task.save_configuration(
            project,
            task_id,
            {**(patch or {}), "pipeline": {"stages": stages}},
            revision=current["revision"],
        )
        submitted = task.submit_run(project, task_id)
        try:
            result = task.wait_run(project, submitted["id"], timeout=timeout)
            if result["status"] not in {"succeeded", "failed", "stopped", "unknown"}:
                raise TimeoutError(f"Task 超时: {submitted['id']}")
        finally:
            current_run = task.get_run(project, submitted["id"])
            if current_run["status"] in {"running", "pending", "stopping"}:
                task.stop_run(project, submitted["id"])
        records.append({k: result[k] for k in ("id", "status", "stages", "run_dir", "data_dir")})
        (project.parent / "progress.json").write_text(json.dumps(records, indent=2))
        expected = "succeeded" if succeeds else "failed"
        assert result["status"] == expected, (result, task.read_log(project, result["id"]))
        assert result["version_id"] == item["version_id"]
        assert Path(result["run_dir"]).parent.name == "runs"
        assert Path(result["data_dir"]).parent.name == "data"
        print(f"{configuration['case']} {'+'.join(stages)}: {expected}", flush=True)
        return result

    prepared_run = execute(["trainprep"])
    prepared = prepared_run["summary"]["reports"]["trainprep"]["prepared"]
    bindings = {
        stage: {"preparation_" + split: path for split, path in prepared.items()}
        for stage in ("train", "posttrain", "infer")
    }
    trained = execute(["train"], {"inputs": bindings})
    weight = trained["summary"]["reports"]["pretrain"]["checkpoint"]
    initial = torch.load(weight, map_location="cpu", weights_only=False)
    assert initial["updates"] == configuration["train"]["updates"]
    assert len(initial["history"]) == initial["updates"]
    assert np.isfinite(initial["history"]).all()
    # 增加一个真实更新，检查恢复消费了原状态，而非只加载网络重新计步。
    resumed = execute(
        ["train"],
        {"inputs": {"train": {"resume": weight}}, "train": {"updates": initial["updates"] + 1}},
    )
    resumed_weight = resumed["summary"]["reports"]["pretrain"]["checkpoint"]
    continued = torch.load(resumed_weight, map_location="cpu", weights_only=False)
    assert continued["updates"] == initial["updates"] + 1
    assert continued["history"][:-1] == initial["history"]
    calibrated = execute(["posttrain"], {"inputs": {"posttrain": {"checkpoint": resumed_weight}}})
    calibrated_weight = calibrated["summary"]["reports"]["posttrain"]["checkpoint"]
    generated = execute(["infer"], {"inputs": {"infer": {"checkpoint": calibrated_weight}}})
    result_path = generated["summary"]["reports"]["infer"]["results"]
    _, arrays = read_arrays(result_path, kind="control_results_v1")
    assert len(arrays["response"]) == configuration["infer"]["test_samples"]
    assert all(np.isfinite(value).all() for value in arrays.values())
    before = hashlib.sha256(Path(result_path).read_bytes()).hexdigest()
    # post 必须只捕获固定结果；故意令模型和响应环境不可用，防止隐式重算。
    posted = execute(
        ["post"],
        {
            "inputs": {
                "post": {"results": result_path},
                "infer": {"checkpoint": "/missing/checkpoint.pt"},
            },
            "solver": {"python": "/missing/python"},
            "components": {"model": "missing_module.build_model"},
        },
    )
    assert set(posted["summary"]["reports"]) == {"post"}
    request = json.loads((project / posted["request_path"]).read_text())
    assert set(request["context"]["assets"]) == {"inputs.post.results"}
    assert not (Path(posted["run_dir"]) / "checkpoints").exists()
    report = json.loads(Path(posted["summary"]["reports"]["post"]["metrics_file"]).read_text())
    assert report["metrics"] == generated["summary"]["reports"]["infer"]["metrics"]
    assert hashlib.sha256(Path(result_path).read_bytes()).hexdigest() == before
    execute(["post"], {"inputs": {"post": {"results": None}}}, succeeds=False)
    # 恢复合法组件；在一次 Task 运行内验证 Python 的直接产物交接。
    combined = execute(
        ["train", "posttrain", "infer", "post"],
        {
            "components": configuration["components"],
            "solver": configuration["solver"],
            "train": configuration["train"],
            "inputs": {
                **bindings,
                "train": {**bindings["train"], "resume": None},
                "posttrain": {**bindings["posttrain"], "checkpoint": None},
                "infer": {**bindings["infer"], "checkpoint": None},
                "post": {"results": None},
            },
        },
    )
    assert {"pretrain", "posttrain", "infer", "post"} <= set(combined["summary"]["reports"])
    assert len(task.get_lineage(project)) == 1
    return {
        "case": configuration["case"],
        "project": str(project),
        "task_id": task_id,
        "runs": records,
        "result": result_path,
        "metrics": report["metrics"],
        "scope": "small real-model Task handoff; not paper accuracy",
    }


def main():
    """从已核实的官方物理数组抽取固定前缀，保留原始清单来源。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.output.resolve()
    root.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    cfg = OmegaConf.to_container(OmegaConf.load(args.config), resolve=True)
    sources = {s: cfg["inputs"]["trainprep"]["dataset_" + s] for s in ("train", "cal", "test")}
    physical = {}
    for split, count in (("train", 8), ("cal", 4), ("test", 2)):
        record, arrays = read_arrays(sources[split], kind="control_physical_v1")
        physical[split] = save_arrays(
            root / "physical" / split,
            {name: value[:count] for name, value in arrays.items()},
            kind="control_physical_v1",
            metadata={**record["metadata"], "count": count, "source_manifest": sources[split]},
        )
    cfg["inputs"]["trainprep"] = {"dataset_" + s: path for s, path in physical.items()}
    cfg["model"].update(dim=8, ddim_steps=4)
    cfg["train"].update(updates=2, batch_size=2, device="cpu")
    cfg["posttrain"].update(updates_per_round=1, subset_size=8, batch_size=2, calibration_samples=4)
    cfg["infer"].update(device="cpu", adaptation_updates=1, test_samples=2, batch_size=2)
    cfg["pipeline"] = {"stages": ["trainprep"]}
    if cfg["case"] == "burgers":
        cfg["solver"].update(python=None)
        cfg["inputs"]["infer"]["solver_assets"] = None
    OmegaConf.save(OmegaConf.create(cfg), root / "configuration.yaml")
    repository = Path(__file__).resolve().parents[3]
    report = exercise(root / "project", repository / "recipes/safediffcon", cfg)
    report["elapsed_seconds"] = time.monotonic() - started
    report["data_source"] = sources
    report["configuration"] = str(root / "configuration.yaml")
    (root / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
