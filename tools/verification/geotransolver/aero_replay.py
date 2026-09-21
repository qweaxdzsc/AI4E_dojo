"""安装环境的真实外流 Task、恢复、独立预测和脱离原路径的固定结果重放。"""

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import ai4e_task as task
import numpy as np
import torch
import yaml

import ai4e_contrib
import ai4e_core


def assert_state(a, b):
    """逐值核验嵌套模型、组合优化器、调度器和随机流状态。"""
    if isinstance(a, torch.Tensor):
        torch.testing.assert_close(a, b, atol=0, rtol=0)
    elif isinstance(a, np.ndarray):
        np.testing.assert_array_equal(a, b)
    elif isinstance(a, dict):
        assert a.keys() == b.keys()
        for key in a:
            assert_state(a[key], b[key])
    elif isinstance(a, (tuple, list)):
        assert len(a) == len(b)
        for x, y in zip(a, b, strict=True):
            assert_state(x, y)
    else:
        assert a == b


def execute(case, config, *, script="pipeline.py"):
    """用当前安装解释器运行外部可编辑研究正文，保留失败日志。"""
    (case / "config.yaml").write_text(yaml.safe_dump(config, sort_keys=False))
    runs = Path(config["run_root"])
    before = set(runs.iterdir()) if runs.exists() else set()
    command = [sys.executable, str(case / script)]
    result = subprocess.run(command, cwd=case.parent, capture_output=True, text=True, check=False)
    (case / "last-command.json").write_text(json.dumps(command))
    (case / "last-command.log").write_text(result.stdout + result.stderr)
    if result.returncode:
        raise RuntimeError(result.stdout + result.stderr)
    return (set(runs.iterdir()) - before).pop()


def predictions_equal(left, right):
    """全点比对保存结果，覆盖全部样本、字段、身份和物理指标。"""
    a, b = (json.loads(Path(p).read_text()) for p in (left, right))
    assert len(a["results"]) == len(b["results"])
    for x, y in zip(a["results"], b["results"], strict=True):
        assert x["sample"] == y["sample"]
        p, q = Path(x["manifest"]), Path(y["manifest"])
        m, n = json.loads(p.read_text()), json.loads(q.read_text())
        assert m["filemap"].keys() == n["filemap"].keys()
        for key in m["filemap"]:
            assert_state(
                torch.load(p.parent / m["filemap"][key], weights_only=True),
                torch.load(q.parent / n["filemap"][key], weights_only=True),
            )


def extension(root, output):
    """从安装资源物化 L1 扩展，修改网络宽度并真实训练、保存和独立读回。"""
    root, output = Path(root), Path(output)
    output.mkdir(parents=True, exist_ok=True)
    case = output / "case"
    task.copy_example("recipe_extensions.geotransolver_aero", case)
    cfg = yaml.safe_load((root / "real/shapenet_car/case/config.yaml").read_text())
    cfg["run_root"], cfg["data_root"] = str(output / "runs"), str(output / "data")
    cfg["model"]["parameters"]["n_hidden"] = 64
    cfg["train"]["max_epochs"] = 1
    run = execute(case, cfg)
    state = torch.load(run / "checkpoints/last.pt", weights_only=False)
    assert state["model"]["preprocess.0.layers.0.weight"].shape[0] == 128
    record = json.loads((run / "artifacts/physical-predictions.json").read_text())
    fields = json.loads(Path(record["results"][0]["manifest"]).read_text())
    assert "surface.absolute_error" in fields["filemap"]
    cfg["pipeline"]["stages"] = ["post"]
    cfg["inputs"]["post"]["results"] = str(run / "artifacts/physical-predictions.json")
    (run / "checkpoints").rename(run / "hidden-checkpoints")
    post = execute(case, cfg)
    assert list((Path(cfg["data_root"]) / post.name).rglob("absolute_error.png"))
    result = {
        "run": str(run),
        "post": str(post),
        "hidden": 64,
        "loss": "L1",
        "saved_error_consumed": True,
        "interpreter": sys.executable,
    }
    (output / "extension.json").write_text(json.dumps(result, indent=2))
    return result


def replay(root, output):
    """从已完成真实五轮来源重放两例，交付安装和 worker 证据。"""
    torch.set_num_threads(2)
    root, output = Path(root), Path(output)
    output.mkdir(parents=True, exist_ok=True)
    evidence = {
        "interpreter": sys.executable,
        "packages": {
            module.__name__: module.__file__ for module in (ai4e_core, ai4e_contrib, task)
        },
        "cases": {},
    }
    for name in ("shapenet_car", "nasa_crm"):
        source = root / "real" / name
        dest = output / name
        dest.mkdir(parents=True, exist_ok=True)
        case = dest / "case"
        task.copy_example("aero_cfd." + name + "_geotransolver", case)
        cfg = yaml.safe_load((source / "case/config.yaml").read_text())
        cfg["run_root"] = str(dest / "runs")
        cfg["data_root"] = str(dest / "data")
        (case / "config.yaml").write_text(yaml.safe_dump(cfg, sort_keys=False))
        original = Path(json.loads((source / "completed-run.json").read_text())["run"])
        expected = torch.load(original / "checkpoints/last.pt", weights_only=False)
        project = dest / "project"
        task.create_project(project)
        item = task.new_task(project, name, source=case)
        submitted = task.submit_run(project, item["id"])
        result = task.wait_run(project, submitted["id"], timeout=300)
        (dest / "worker.json").write_text(json.dumps(result, indent=2, default=str))
        assert result["status"] == "succeeded", task.read_log(project, submitted["id"])
        managed = Path(result["run_dir"])
        actual = torch.load(managed / "checkpoints/last.pt", weights_only=False)
        for key in (
            "model",
            "optimizer",
            "scheduler",
            "updates",
            "epoch",
            "python_rng",
            "numpy_rng",
            "torch_rng",
        ):
            assert_state(expected[key], actual[key])
        predictions_equal(
            original / "artifacts/physical-predictions.json",
            managed / "artifacts/physical-predictions.json",
        )
        cfg["pipeline"]["stages"] = ["train"]
        cfg["train"]["max_epochs"] = 1
        first = execute(case, cfg)
        cfg["train"]["max_epochs"] = 5
        cfg["inputs"]["train"]["resume"] = str(first / "checkpoints/last.pt")
        resumed = execute(case, cfg)
        restored = torch.load(resumed / "checkpoints/last.pt", weights_only=False)
        for key in (
            "model",
            "optimizer",
            "scheduler",
            "updates",
            "epoch",
            "python_rng",
            "numpy_rng",
            "torch_rng",
        ):
            assert_state(expected[key], restored[key])
        full_protocol = json.loads((original / "artifacts/training-protocol.json").read_text())
        resumed_protocol = json.loads((resumed / "artifacts/training-protocol.json").read_text())
        assert full_protocol["inputs"][2:] == resumed_protocol["inputs"]
        cfg["pipeline"]["stages"] = ["infer"]
        cfg["inputs"]["infer"]["checkpoint"] = str(resumed / "checkpoints/last.pt")
        inferred = execute(case, cfg)
        predictions_equal(
            original / "artifacts/physical-predictions.json",
            inferred / "artifacts/physical-predictions.json",
        )
        fixed = dest / "detached"
        fixed.mkdir()
        record = json.loads((inferred / "artifacts/physical-predictions.json").read_text())
        for index, row in enumerate(record["results"]):
            old = Path(row["manifest"])
            new = fixed / str(index)
            shutil.copytree(old.parent, new)
            row["manifest"] = str(new / old.name)
        reference = fixed / "results.json"
        reference.write_text(json.dumps(record))
        cfg["pipeline"]["stages"] = ["post"]
        cfg["inputs"]["post"]["results"] = str(reference)
        # 除固定结果外的所有声明输入均失效；后处理不能暗中依赖检查点或物理清单。
        for stage, inputs in cfg["inputs"].items():
            if stage != "post":
                for key in inputs:
                    inputs[key] = str(dest / "unavailable" / key) if inputs[key] else None
        inferred.rename(inferred.with_name(inferred.name + "-hidden"))
        post = execute(case, cfg)
        assert list((Path(cfg["data_root"]) / post.name).rglob("*.png"))
        evidence["cases"][name] = {
            "task_run": str(managed),
            "resume_run": str(resumed),
            "post_run": str(post),
            "weights_optimizer_scheduler_exact": True,
            "rng_exact": True,
            "sample_query_stream_exact": True,
            "all_prediction_arrays_exact": True,
            "epochs": actual["epoch"],
            "updates": actual["updates"],
            "case_files": {
                p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in case.glob("*.py")
            },
        }
    (output / "replay.json").write_text(json.dumps(evidence, indent=2))
    return evidence


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--extension-only", action="store_true")
    args = parser.parse_args()
    if args.extension_only:
        extension(args.root, args.output)
    else:
        replay(args.root, args.output)
