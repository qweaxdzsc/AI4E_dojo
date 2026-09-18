"""真实原数据、实际安装包下的公共模板/案例/Task双入口验收。"""

import argparse
import json
import shutil
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

import ai4e_task as task
import numpy as np
import torch
import yaml

from ai4e_contrib.application.pde_control.safediffcon.configuration import load_configuration
from ai4e_core.applications.pde_control.contracts import read_arrays

REPO = Path(__file__).resolve().parents[3]
ORDER = ["rawprep", "trainprep", "train", "posttrain", "infer", "post"]

EXTENSION = '''"""验收用真实原分片前缀与用户扩展；不改变原数组数值。"""
from pathlib import Path
import json
import numpy as np
from ai4e_contrib.application.datasets.safediffcon.arrays import read_burgers, read_tokamak
from ai4e_contrib.ability.model.safediffcon.adapters import build_model
from ai4e_core.applications.pde_control.contracts import read_arrays
from ai4e_core import run

def burgers_prefix(root, split):
    return {k: v[:{"train": 8, "cal": 4, "test": 2}[split]] for k,v in read_burgers(root, split).items()}

def tokamak_prefix(root, split):
    return {k: v[:{"train": 8, "cal": 4, "test": 2}[split]] for k,v in read_tokamak(root, split).items()}

def model(**settings):
    return build_model(**settings)

def energy(response, *, case):
    values = np.square(np.ascontiguousarray(response)).mean(tuple(range(1, response.ndim)))
    return {"energy": {"values": values, "valid": np.ones_like(values, dtype=bool),
                       "units": "source_units_squared", "axes": "B"}}

def audit(cfg, results):
    _, arrays = read_arrays(results, kind="control_results_v1")
    expected = np.square(np.ascontiguousarray(arrays["response"])).mean(tuple(range(1, arrays["response"].ndim)))
    np.testing.assert_array_equal(expected, arrays["energy"])
    session = run.TrainingRun()
    path = session.output_dir("audit") / "energy.json"
    path.write_text(json.dumps(expected.tolist()))
    session.record_asset("energy", path, kind="other", stage="audit")
    session.report({"energy": str(path)}, stage="audit")
    return path
'''


def equal(a, b):
    """递归逐值比较真正的训练状态，失败不放宽容差。"""
    if isinstance(a, torch.Tensor):
        assert torch.equal(a, b)
    elif isinstance(a, np.ndarray):
        np.testing.assert_array_equal(a, b)
    elif isinstance(a, dict):
        assert a.keys() == b.keys()
        for key in a:
            equal(a[key], b[key])
    elif isinstance(a, (list, tuple)):
        assert len(a) == len(b)
        for x, y in zip(a, b):
            equal(x, y)
    else:
        assert a == b, (a, b)


def states_equal(a, b):
    """管理路径单独核对；模型、优化、EMA、随机流和历史必须逐值相同。"""
    left = torch.load(a, weights_only=False, map_location="cpu")
    right = torch.load(b, weights_only=False, map_location="cpu")
    for key in (
        "model",
        "optimizer",
        "ema",
        "scheduler",
        "updates",
        "history",
        "stream",
        "python_rng",
        "numpy_rng",
        "torch_rng",
        "cuda_rng",
        "mps_rng",
        "algorithm_state",
        "status",
    ):
        equal(left[key], right[key])
    first, second = deepcopy(left["contract"]), deepcopy(right["contract"])
    # 后训练与适配记录明确父权重位置；它的科学字节已在本组前序比较。
    for contract in (first, second):
        contract.pop("parent", None)
        if "settings" in contract:
            contract["settings"].pop("checkpoint", None)
    equal(first, second)
    return {"updates": left["updates"], "loss": left["history"], "max_weight_difference": 0.0}


def direct(code, cfg, root, label):
    """仓库外工作目录通过实际脚本执行，不在测试进程中代调计算函数。"""
    cfg = deepcopy(cfg)
    cfg["run_root"], cfg["data_root"] = str(root / label / "runs"), str(root / label / "data")
    path = root / f"{label}.yaml"
    path.write_text(yaml.safe_dump(cfg, sort_keys=False))
    command = [
        "uv",
        "run",
        "--no-project",
        "--python",
        sys.executable,
        "python",
        str(code / "pipeline.py"),
        "--config",
        str(path),
    ]
    with (root / f"{label}.log").open("w") as log:
        subprocess.run(
            command, cwd=root, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=240
        )
    return json.loads(next(Path(cfg["run_root"]).glob("*/summary.json")).read_text())


def submit(project, item, cfg, *, success=True):
    """公开提交并确认终态；预算中断时明确停止独立会话的worker。"""
    previous = task.read_configuration(project, item["id"])
    task.replace_configuration(project, item["id"], cfg, revision=previous["revision"])
    launched = task.submit_run(project, item["id"])
    try:
        done = task.wait_run(project, launched["id"], timeout=240, interval=0.1)
        if done["status"] not in {"succeeded", "failed", "stopped"}:
            raise TimeoutError("Task未在阶段预算内结束")
    finally:
        state = task.get_run(project, launched["id"])
        if state["status"] not in {"succeeded", "failed", "stopped"}:
            stopped = task.stop_run(project, launched["id"], timeout=10)
            if stopped["status"] not in {"succeeded", "failed", "stopped"}:
                raise RuntimeError("Task停止未确认")
    assert done["status"] == ("succeeded" if success else "failed"), (
        done["id"],
        done.get("error"),
        task.read_log(project, done["id"]),
    )
    assert done["version_id"] == item["version_id"]
    return done


def execute(case, output, *, template=False):
    """完整正向计算先行，随后执行恢复、资产迁移及附加失败用例。"""
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    source = REPO / ("recipes/safediffcon" if template else f"examples/safediffcon/{case}")
    code = output / "recipe"
    shutil.copytree(source, code, ignore=shutil.ignore_patterns("__pycache__"))
    (code / "verification_ext.py").write_text(EXTENSION)
    pipeline = code / "pipeline.py"
    text = pipeline.read_text().replace(
        "from configuration import", "from verification_ext import audit\nfrom configuration import"
    )
    text = text.replace(
        '        results = run.stage("infer", infer, cfg, prepared, calibrated)',
        '        results = run.stage("infer", infer, cfg, prepared, calibrated)\n        run.stage("audit", audit, cfg, results)',
    )
    pipeline.write_text(text)
    cfg = load_configuration(code / "config.yaml")
    assert cfg["case"] == case
    cfg["model"].update(dim=8, ddim_steps=4)
    cfg["train"].update(updates=2, batch_size=2, device="cpu")
    cfg["posttrain"].update(updates_per_round=1, subset_size=8, batch_size=2, calibration_samples=4)
    cfg["infer"].update(device="cpu", test_samples=2, batch_size=2, adaptation_updates=1)
    cfg["components"].update(
        reader=f"verification_ext.{case}_prefix",
        model="verification_ext.model",
        derived="verification_ext.energy",
    )
    cfg["pipeline"]["stages"] = ORDER
    project = output / "project"
    task.create_project(project)
    item = task.new_task(project, case, source=code, configuration=cfg)
    full = submit(project, item, cfg)
    report = full["summary"]["reports"]
    assert set(ORDER) - {"train"} <= report.keys()
    prepared = report["trainprep"]["prepared"]
    # 同一准备交给两入口，避免将路径导致的清单身份变化混进数值对照。
    staged = deepcopy(cfg)
    for phase in ("train", "posttrain", "infer"):
        staged["inputs"][phase].update({"preparation_" + s: p for s, p in prepared.items()})
    staged["pipeline"]["stages"] = ["train", "posttrain", "infer", "post"]
    outside = direct(code, staged, output, "direct")
    numeric = {}
    for phase in ("pretrain", "posttrain_0", "posttrain_1", "adapt"):
        numeric[phase] = states_equal(
            report[phase]["checkpoint"], outside["reports"][phase]["checkpoint"]
        )
    first = report["infer"]["results"]
    _, a = read_arrays(first, kind="control_results_v1")
    _, b = read_arrays(outside["reports"]["infer"]["results"], kind="control_results_v1")
    equal(a, b)
    assert len(a["ids"]) == 2 and np.isfinite(a["response"]).all()
    for split, n in (("train", 8), ("cal", 4), ("test", 2)):
        _, arrays = read_arrays(report["rawprep"]["physical"][split], kind="control_physical_v1")
        assert len(arrays["states"]) == n
    # 续训完整状态，并分别验证独立posttrain/infer/post交接。
    resumed_cfg = deepcopy(staged)
    resumed_cfg["pipeline"]["stages"] = ["train"]
    resumed_cfg["train"]["updates"] = 3
    resumed_cfg["inputs"]["train"]["resume"] = report["pretrain"]["checkpoint"]
    resumed = submit(project, item, resumed_cfg)
    resumed_cfg["inputs"]["train"]["resume"] = outside["reports"]["pretrain"]["checkpoint"]
    direct_resume = direct(code, resumed_cfg, output, "direct-resume")
    numeric["resume"] = states_equal(
        resumed["summary"]["reports"]["pretrain"]["checkpoint"],
        direct_resume["reports"]["pretrain"]["checkpoint"],
    )
    assert numeric["resume"]["loss"][:2] == numeric["pretrain"]["loss"]
    assert numeric["resume"]["updates"] == 3
    state0 = torch.load(report["pretrain"]["checkpoint"], weights_only=False, map_location="cpu")
    state1 = torch.load(
        resumed["summary"]["reports"]["pretrain"]["checkpoint"],
        weights_only=False,
        map_location="cpu",
    )
    assert any(not torch.equal(v, state1["model"][k]) for k, v in state0["model"].items())
    stages = []
    independent = deepcopy(staged)
    for phase, input_path in (
        ("posttrain", report["pretrain"]["checkpoint"]),
        ("infer", report["posttrain"]["checkpoint"]),
    ):
        independent["pipeline"]["stages"] = [phase]
        independent["inputs"][phase]["checkpoint"] = input_path
        result = submit(project, item, independent)
        stages.append(result["id"])
        if phase == "infer":
            _, independent_arrays = read_arrays(
                result["summary"]["reports"]["infer"]["results"], kind="control_results_v1"
            )
            equal(a, independent_arrays)
    posted_cfg = deepcopy(staged)
    posted_cfg["pipeline"]["stages"] = ["post"]
    posted_cfg["inputs"]["post"]["results"] = first
    posted_cfg["components"]["model"] = "missing.model"
    posted_cfg["solver"]["python"] = "/missing/python"
    posted = submit(project, item, posted_cfg)
    assert not (Path(posted["run_dir"]) / "checkpoints").exists()
    comparison = task.compare_runs(project, full["id"], posted["id"])
    # 公共指标不是从报告中猜测，来源同一固定数组，科学口径必须匹配。
    assert comparison["metrics"]
    assert all(v["status"] == "available" for v in comparison["metrics"].values()), comparison
    shared = task.share_run_asset(
        project, full["id"], f"{case}/results", first, kind="other", copy=True
    )
    from ai4e_task.tasks.assets import validate_asset

    shared_path = validate_asset(project, shared)
    original_bytes = Path(first).read_bytes()
    assert shared_path.read_bytes() == original_bytes
    posted_cfg["inputs"]["post"]["results"] = str(shared_path)
    consumer = task.new_task(project, "shared-consumer", source=code, configuration=posted_cfg)
    child = task.fork_task(project, consumer["id"])
    # 只移走本次验收生成的原结果；历史实验产物绝不移动。
    original = Path(first).parent
    moved = original.with_name(original.name + "-held")
    original.rename(moved)
    try:
        consumed = submit(project, child, posted_cfg)
        assert (
            json.loads(Path(consumed["summary"]["reports"]["post"]["metrics_file"]).read_text())[
                "metrics"
            ]
            == report["infer"]["metrics"]
        )
    finally:
        moved.rename(original)
    posted_cfg["inputs"]["post"]["results"] = None
    failed = submit(project, item, posted_cfg, success=False)
    assert len(task.get_lineage(project)) == 3
    result = {
        "case": case,
        "source": str(source),
        "project": str(project),
        "task_id": item["id"],
        "full_run": full["id"],
        "resume_run": resumed["id"],
        "independent_runs": stages,
        "post_run": posted["id"],
        "expected_failure": failed["id"],
        "copied_post": consumed["id"],
        "numeric": numeric,
        "all_result_arrays_equal": True,
        "raw_counts": [8, 4, 2],
        "raw_reader": "official reader then fixed original split prefix",
        "results": first,
        "prepared": prepared,
        "metrics": report["infer"]["metrics"],
        "scope": "real training and public handoff; not paper accuracy",
        "python": sys.executable,
    }
    (output / "report.json").write_text(json.dumps(result, indent=2))
    print(
        json.dumps({"case": case, "status": "passed", "report": str(output / "report.json")}),
        flush=True,
    )
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=["burgers", "tokamak"], required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--template", action="store_true")
    args = parser.parse_args()
    execute(args.case, args.output, template=args.template)
