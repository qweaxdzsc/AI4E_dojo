"""公共配置下直接脚本与Task的真实训练/恢复/预测及扩展对照。"""

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

from ai4e_core.abilities.data.save.array_manifest import digest, read_arrays
from tools.verification.wdno.report import check_arrays

REPO = Path(__file__).resolve().parents[3]


def assert_equal(first, second):
    """逐值检查嵌套训练状态，不比较运行目录等管理字段。"""
    if isinstance(first, torch.Tensor):
        assert torch.equal(first, second)
    elif isinstance(first, np.ndarray):
        np.testing.assert_array_equal(first, second)
    elif isinstance(first, dict):
        assert first.keys() == second.keys()
        for key in first:
            assert_equal(first[key], second[key])
    elif isinstance(first, (list, tuple)):
        assert len(first) == len(second)
        for a, b in zip(first, second):
            assert_equal(a, b)
    else:
        assert first == second


def direct(code, cfg):
    config = code / "config.yaml"
    config.write_text(yaml.safe_dump(cfg, sort_keys=False))
    proc = subprocess.run(
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
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
    )
    (code.parent / "direct-console.txt").write_text(proc.stdout + proc.stderr)
    if proc.returncode:
        raise AssertionError(proc.stdout + proc.stderr)
    summaries = list(Path(cfg["run_root"]).glob("*/summary.json"))
    return json.loads(max(summaries, key=lambda p: p.stat().st_mtime_ns).read_text())


def wait_task(project, run_id, *, timeout=180):
    """验收进程中断/超时时，通过公开API收尾独立会话中的Task worker。"""
    try:
        done = task.wait_run(project, run_id, timeout=timeout, interval=0.1)
        if done["status"] not in {"succeeded", "failed", "stopped"}:
            raise TimeoutError("Task验收等待未完成")
        return done
    except BaseException:
        # Task worker独立于预算监督的进程组，不能只结束验收父进程。
        stopped = task.stop_run(project, run_id, timeout=10)
        if stopped["status"] not in {"succeeded", "failed", "stopped"}:
            raise RuntimeError("Task停止尚未确认，不能把本次验收记作收尾") from None
        raise


def managed(project, current, cfg):
    task.replace_configuration(
        project,
        current["id"],
        cfg,
        revision=task.read_configuration(project, current["id"])["revision"],
    )
    record = task.submit_run(project, current["id"])
    done = wait_task(project, record["id"])
    if done["status"] != "succeeded":
        raise AssertionError(json.dumps(done, default=str))
    summary = json.loads((project / done["run_path"] / "summary.json").read_text())
    assert summary["research_status"] == "completed"
    assert done["version_id"] == current["version_id"]
    return summary, done


def bind_prepared(cfg, reports):
    for stage in ("train", "infer"):
        prepared = reports["trainprep"]
        cfg["inputs"][stage].update(
            preparation=prepared["train"], validation=prepared["validation"], test=prepared["test"]
        )


def exercise(directory: Path, config: dict) -> dict:
    """相同真实输入两侧从零2步、恢复到3步；插入步骤两侧都实际执行。"""
    directory.mkdir(parents=True, exist_ok=False)
    code = directory / "recipe"
    shutil.copytree(REPO / "recipes/wdno", code, ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copy2(REPO / "examples/recipe_extensions/wdno/variants.py", code / "variants.py")
    (code / "audit.py").write_text("""import json
import sys
import importlib
from pathlib import Path
import numpy as np
from ai4e_core import run
from ai4e_core.abilities.data.save.array_manifest import read_arrays

def audit(cfg, results):
    session = run.TrainingRun()
    _, arrays = read_arrays(results["test"], kind="spatiotemporal-result-v1")
    energy = np.mean(arrays["prediction"] ** 2, axis=-1)
    np.testing.assert_array_equal(energy, arrays["energy"])
    output = session.output_dir("audit") / "energy.npy"
    np.save(output, energy)
    np.testing.assert_array_equal(np.load(output), energy)
    session.record_asset("energy", output, kind="other", stage="audit", dependencies=[results["test"]], semantics={"unit": "u^2", "axes": ["sample", "time"]})
    names = ["ai4e_core.run.session", "ai4e_contrib.application.spatiotemporal_pde.wdno.training", "ai4e_task.tasks.worker"]
    session.artifact("runtime.json", {"python": sys.executable, "modules": {name: str(Path(importlib.import_module(name).__file__).resolve()) for name in names}})
    return str(output)
""")
    pipeline = code / "pipeline.py"
    pipeline.write_text(
        pipeline.read_text()
        .replace(
            "from configuration import", "from audit import audit\nfrom configuration import", 1
        )
        .replace(
            '    if "post" in selected:',
            '    if results is not None:\n        run.stage("audit", audit, cfg, results)\n    if "post" in selected:',
        )
    )
    cfg = deepcopy(config)
    cfg["model"].update(dim=8, dim_mults=[1, 2], ddim_steps=2)
    cfg["train"].update(updates=2, batch_size=2, device="cpu", seconds=120)
    cfg["infer"].update(device="cpu", batch_size=2)
    cfg["inputs"]["train"]["resume"] = None
    cfg["inputs"]["infer"]["checkpoint"] = None
    cfg["components"].update(
        network="variants.custom_network",
        objective="variants.custom_loss",
        derived="variants.energy",
    )
    cfg["run_root"], cfg["data_root"] = (
        str(directory / "direct-runs"),
        str(directory / "direct-data"),
    )
    cfg["pipeline"] = {"stages": ["rawprep", "trainprep", "train", "infer", "post"]}
    (code / "config.yaml").write_text(yaml.safe_dump(cfg, sort_keys=False))
    project = directory / "project"
    task.create_project(project)
    current = task.new_task(project, "wdno", source=code, configuration=cfg)
    first = direct(code, cfg)
    second, record = managed(project, current, cfg)
    original_checkpoints = [
        first["reports"]["train"]["checkpoint"],
        second["reports"]["train"]["checkpoint"],
    ]
    # 原准备含绝对来源位置，字节不必相同；物理输入和准备值必须一致。
    for stage, kind in [
        ("rawprep", "spatiotemporal-physical-v1"),
        ("trainprep", "spatiotemporal-prepared-v1"),
    ]:
        for split in ("train", "validation", "test"):
            actual_kind = "spatiotemporal-physical-v1" if split != "train" else kind
            _, a = read_arrays(first["reports"][stage][split], kind=actual_kind)
            _, b = read_arrays(second["reports"][stage][split], kind=actual_kind)
            assert_equal(a, b)
    records = [record]

    def compare(a, b):
        states = [
            torch.load(x["reports"]["train"]["checkpoint"], map_location="cpu", weights_only=False)
            for x in (a, b)
        ]
        for key in (
            "model",
            "optimizer",
            "scheduler",
            "ema",
            "stream",
            "python_rng",
            "numpy_rng",
            "torch_rng",
            "history",
            "updates",
        ):
            assert_equal(states[0][key], states[1][key])
        for split in ("validation", "test"):
            _, x = read_arrays(a["reports"]["infer"][split], kind="spatiotemporal-result-v1")
            _, y = read_arrays(b["reports"]["infer"][split], kind="spatiotemporal-result-v1")
            assert_equal(x, y)
        return states

    state2 = compare(first, second)
    left, right = deepcopy(cfg), deepcopy(cfg)
    for c, summary in ((left, first), (right, second)):
        bind_prepared(c, summary["reports"])
        c["inputs"]["train"]["resume"] = summary["reports"]["train"]["checkpoint"]
        c["train"]["updates"] = 3
        c["pipeline"]["stages"] = ["train", "infer", "post"]
    first = direct(code, left)
    second, record = managed(project, current, right)
    records.append(record)
    state3 = compare(first, second)
    assert state3[0]["updates"] == 3 and state3[0]["history"][:2] == state2[0]["history"]
    assert any(
        not torch.equal(state2[0]["model"][k], state3[0]["model"][k]) for k in state2[0]["model"]
    )
    runtime = []
    for summary in (first, second):
        directory_run = Path(summary["run_dir"])
        runtime.append(json.loads((directory_run / "artifacts/runtime.json").read_text()))
        assert [x["stage"] for x in summary["stage_events"]] == ["train", "infer", "audit", "post"]
        for item in json.loads((directory_run / "artifacts/assets.json").read_text())[
            "items"
        ].values():
            if item["kind"] != "checkpoint" and item["stage"] in ("infer", "audit"):
                assert Path(item["path"]).is_relative_to(Path(summary["data_dir"]))
    assert_equal(runtime[0], runtime[1])
    # 正常推理后独立post；非法模型路径证明它只消费固定结果。
    right["inputs"]["post"] = second["reports"]["infer"]
    right["components"]["network"] = "not_installed.network"
    right["pipeline"]["stages"] = ["post"]
    fixed, record = managed(project, current, right)
    records.append(record)
    assert fixed["reports"]["post"] == second["reports"]["post"]
    comparison = task.compare_runs(project, records[1]["id"], record["id"])
    assert all(item["status"] == "available" for item in comparison["metrics"].values()), comparison
    assert len(task.get_lineage(project)) == 1
    request = json.loads((project / record["request_path"]).read_text())
    assert set(request["context"]["assets"]) == {"inputs.post.validation", "inputs.post.test"}
    result = {
        "passed": True,
        "updates": [2, 3],
        "prediction_max_abs": 0.0,
        "runtime": runtime[0],
        "runs": records,
        "comparison": comparison,
        "old_checkpoints": original_checkpoints,
        "final_checkpoint": second["reports"]["train"]["checkpoint"],
    }
    (directory / "acceptance.json").write_text(json.dumps(result, indent=2))
    return result


def staged_exercise(directory: Path, config: dict, *, case="extension") -> dict:
    """公开API新建任务，分次准备/训练/推理/post/续训，逐阶段与直接脚本对照。"""
    directory.mkdir(parents=True, exist_ok=False)
    code = directory / "recipe"
    if case not in {"recipe", "example", "extension"}:
        raise ValueError("未知WDNO验收来源")
    source = REPO / ("examples/wdno/burgers_base" if case == "example" else "recipes/wdno")
    shutil.copytree(source, code, ignore=shutil.ignore_patterns("__pycache__"))
    extension = REPO / "examples/recipe_extensions/wdno"
    if case == "extension":
        for name in ("pipeline.py", "audit.py", "variants.py"):
            shutil.copy2(extension / name, code / name)
    cfg = deepcopy(config)
    cfg["model"].update(dim=8, dim_mults=[1, 2], ddim_steps=2)
    cfg["train"].update(updates=2, batch_size=2, device="cpu", seconds=120)
    cfg["infer"].update(device="cpu", batch_size=2)
    if case == "extension":
        cfg["components"].update(
            network="variants.custom_network",
            objective="variants.custom_loss",
            derived="variants.energy",
        )
    network = cfg["components"]["network"]
    cfg["run_root"] = str(directory / "direct-runs")
    cfg["data_root"] = str(directory / "direct-data")
    (code / "config.yaml").write_text(yaml.safe_dump(cfg, sort_keys=False))
    project = directory / "project"
    task.create_project(project)
    current = task.new_task(project, "wdno-stages", source=code, configuration=cfg)
    left, right = deepcopy(cfg), deepcopy(cfg)
    records, summaries = [], {}

    def pair(label, stages):
        left["pipeline"]["stages"] = right["pipeline"]["stages"] = stages
        a = direct(code, left)
        console = code.parent / "direct-console.txt"
        shutil.copy2(console, directory / f"{label}-direct-console.txt")
        b, record = managed(project, current, right)
        expected = stages + (["audit"] if stages == ["infer"] and case == "extension" else [])
        for summary in (a, b):
            assert [event["stage"] for event in summary["stage_events"]] == expected
            assert not summary["failed"]
        records.append({"label": label, **record})
        summaries[label] = {"direct": a, "task": b}
        return a["reports"], b["reports"]

    a, b = pair("rawprep", ["rawprep"])
    for c, reports in ((left, a), (right, b)):
        physical = reports["rawprep"]
        c["inputs"]["trainprep"].update(
            dataset=physical["train"], validation=physical["validation"], test=physical["test"]
        )
    a, b = pair("trainprep", ["trainprep"])
    for c, reports in ((left, a), (right, b)):
        bind_prepared(c, reports)
    a, b = pair("train", ["train"])
    initial_paths = [a["train"]["checkpoint"], b["train"]["checkpoint"]]

    def states(paths, updates):
        loaded = [torch.load(p, map_location="cpu", weights_only=False) for p in paths]
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
        ):
            assert_equal(loaded[0][key], loaded[1][key])
        assert loaded[0]["updates"] == updates and len(loaded[0]["history"]) == updates
        return loaded

    initial = states(initial_paths, 2)
    for c, path in zip((left, right), initial_paths):
        c["inputs"]["infer"]["checkpoint"] = path
    a, b = pair("infer", ["infer"])
    predictions = deepcopy(b["infer"])
    hashes = {}
    for split in ("validation", "test"):
        record, x = read_arrays(a["infer"][split], kind="spatiotemporal-result-v1")
        _, y = read_arrays(b["infer"][split], kind="spatiotemporal-result-v1")
        assert_equal(x, y)
        if case == "extension":
            assert record["metadata"]["derived_fields"]["energy"] == {
                "units": "u^2",
                "axes": ["sample", "time"],
            }
            np.testing.assert_array_equal(y["energy"], np.mean(y["prediction"] ** 2, axis=-1))
        hashes[split] = {
            key: digest(Path(b["infer"][split]).parent / value["path"])
            for key, value in record["fields"].items()
        }
    for c, reports in ((left, a), (right, b)):
        c["inputs"]["post"] = reports["infer"]
        c["components"]["network"] = "not_installed.network"
    a, b = pair("post", ["post"])
    mse = {}
    for split, path in predictions.items():
        record, arrays = read_arrays(path, kind="spatiotemporal-result-v1")
        # 沿用已冻结的独立NumPy逐样本复算标准；不混入新的float64评价协议。
        # 新推理只保存物理数组；逐样本指标来自随后执行的post报告。
        sample_mse = np.asarray(b["post"][split]["sample_mse"])
        check_arrays({**arrays, "mse": sample_mse}, arrays["ids"].tolist())
        expected = float(np.mean(sample_mse.tolist()))
        actual = b["post"][split]["mse"]
        np.testing.assert_allclose(actual, expected, rtol=1e-12, atol=1e-12)
        np.testing.assert_allclose(a["post"][split]["mse"], actual, rtol=0, atol=0)
        assert hashes[split] == {
            key: digest(Path(path).parent / field["path"])
            for key, field in record["fields"].items()
        }
        mse[split] = actual
    for c, path in zip((left, right), initial_paths):
        c["components"]["network"] = network
        c["inputs"]["train"]["resume"] = path
        c["train"]["updates"] = 3
    a, b = pair("resume", ["train"])
    resumed_paths = [a["train"]["checkpoint"], b["train"]["checkpoint"]]
    final = states(resumed_paths, 3)
    assert final[0]["history"][:2] == initial[0]["history"]
    assert any(
        not torch.equal(initial[0]["model"][k], final[0]["model"][k]) for k in initial[0]["model"]
    )
    failures = {}
    for stage, field in (("train", "preparation"), ("infer", "checkpoint"), ("post", "test")):
        broken = deepcopy(right)
        broken["pipeline"]["stages"] = [stage]
        broken["inputs"][stage][field] = None
        task.replace_configuration(
            project,
            current["id"],
            broken,
            revision=task.read_configuration(project, current["id"])["revision"],
        )
        try:
            request = task.submit_run(project, current["id"])
        except (ValueError, FileNotFoundError, RuntimeError) as error:
            failures[stage] = {"status": "rejected", "error": str(error)}
        else:
            done = wait_task(project, request["id"])
            assert done["status"] == "failed", done
            failures[stage] = done
    task.replace_configuration(
        project,
        current["id"],
        right,
        revision=task.read_configuration(project, current["id"])["revision"],
    )
    assert len(task.get_lineage(project)) == 1
    result = {
        "passed": True,
        "case": case,
        "source": str(source),
        "task_id": current["id"],
        "project": str(project),
        "updates": [2, 3],
        "training_states_equal": True,
        "prediction_max_abs": 0.0,
        "mse": mse,
        "post_without_model": True,
        "prediction_unchanged_by_post": True,
        "runs": records,
        "failures": failures,
        "version_count": 1,
        "initial_checkpoints": initial_paths,
        "final_checkpoints": resumed_paths,
    }
    (directory / "summaries.json").write_text(json.dumps(summaries, indent=2))
    (directory / "acceptance.json").write_text(json.dumps(result, indent=2))
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--staged", action="store_true", help="新建任务并分次提交每个阶段")
    parser.add_argument("--case", choices=["recipe", "example", "extension"], default="extension")
    args = parser.parse_args()
    if not args.staged and args.case != "extension":
        parser.error("--case recipe/example 需要 --staged")
    cfg = yaml.safe_load((REPO / "recipes/wdno/config.yaml").read_text())
    indices = json.loads((args.root / "frozen/indices.json").read_text())
    path = args.output.parent / "task-indices.json"
    path.write_text(json.dumps({s: indices[s][: (8 if s == "train" else 2)] for s in indices}))
    cfg["inputs"]["rawprep"] = {
        "source": str(args.root / "frozen/protocol.json"),
        "indices": str(path),
    }
    result = (
        staged_exercise(args.output, cfg, case=args.case)
        if args.staged
        else exercise(args.output, cfg)
    )
    result["real_original_data"] = True
    result["inputs_sha256"] = {key: digest(path) for key, path in cfg["inputs"]["rawprep"].items()}
    (args.output / "acceptance.json").write_text(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
