"""独立wheel的外复制、公开入口与Task实跑；由主控逐项串行调度。

本脚本只导入当前安装的公开Dojo包，不读取仓库recipe或验证helper。
主控必须将一次调用包在相应组合的BudgetLedger.measure中，传入剩余seconds，
并为Task超时清理预留余量；本脚本不建立第二本账。每次root必须是新目录。
示例：uv run --no-project --no-sync --python <wheel环境/bin/python> installed_replay.py
  --root <实验根/本次重放> --environment <wheel环境> --case-id classic_networks.darcy
  --preparation <真实准备/manifest.json> --seconds 600 --budget-identity mlp-darcy
  --with-task
"""

from __future__ import annotations

import argparse
import contextlib
import copy
import hashlib
import importlib
import json
import os
import runpy
import shutil
import signal
import sys
import time
import traceback
from pathlib import Path

CASE_IDS = (
    "classic_networks.darcy",
    "classic_networks.shapenet_volume",
    "classic_networks.double_cylinder",
    "recipe_extensions.network_composition.resunet",
    "recipe_extensions.network_composition.unet_transformer",
    "recipe_extensions.network_composition.cnn_rnn",
)


def write_json(path, value):
    """保存验证器自己的证据；不写框架run目录。"""
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def file_digest(path):
    """按真实文件字节核对搬移，不使用路径或文件大小冒充内容相同。"""
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def copy_asset(path, destination, *, bundle=False):
    """复制自包含目录或单文件，逐文件验证摘要并保留来源字节。"""
    path, destination = Path(path).resolve(), Path(destination).resolve()
    origin = path.parent if bundle else path
    if destination == origin or destination.is_relative_to(origin):
        raise ValueError("搬移验证目标不能位于来源中")
    files = sorted(origin.rglob("*")) if bundle else [origin]
    if any(item.is_symlink() for item in files):
        raise ValueError("搬移验证要求自包含普通文件，不接受符号链接")
    expected = {
        str(item.relative_to(origin)) if bundle else item.name: file_digest(item)
        for item in files
        if item.is_file()
    }
    if bundle:
        shutil.copytree(origin, destination)
        moved = destination / path.name
        actual = {
            str(item.relative_to(destination)): file_digest(item)
            for item in sorted(destination.rglob("*"))
            if item.is_file()
        }
    else:
        if destination.exists():
            raise FileExistsError(destination)
        shutil.copy2(origin, destination)
        moved = destination
        actual = {origin.name: file_digest(destination)}
    if expected != actual:
        raise AssertionError("搬移副本逐文件内容摘要不一致")
    return moved, {
        "source": str(path),
        "destination": str(moved),
        "bundle": bundle,
        "source_sha256": file_digest(path),
        "destination_sha256": file_digest(moved),
        "files_sha256": expected,
        "content_identical": True,
        "source_preserved": True,
    }


def installed_paths(environment):
    """核对实际包来源，拒绝源码路径或其他环境的Dojo副本。"""
    result = {"python": sys.executable, "prefix": sys.prefix, "pid": os.getpid(), "modules": {}}
    if Path(sys.prefix).resolve() != environment:
        raise RuntimeError(f"不是指定独立环境: {sys.prefix}")
    for name in ("ai4e_spec", "ai4e_core", "ai4e_contrib", "ai4e_task"):
        module = importlib.import_module(name)
        path = Path(module.__file__).resolve()
        if not path.is_relative_to(environment):
            raise RuntimeError(f"{name}并非来自独立wheel环境: {path}")
        result["modules"][name] = str(path)
    return result


def add_worker_probe(source, evidence, environment):
    """在复制后的入口记录实际执行者，Task捕获同一普通用户文件。"""
    probe = source / "installed_runtime_probe.py"
    probe.write_text(
        '"""验证脚本生成的执行来源探针，不参与数值计算。"""\n'
        "import importlib, json, os, sys\nfrom pathlib import Path\n\n"
        "def verify():\n"
        f"    root = Path({str(environment)!r})\n"
        "    if Path(sys.prefix).resolve() != root:\n"
        "        raise RuntimeError('worker interpreter escaped installed environment')\n"
        "    modules = {}\n"
        "    for name in ('ai4e_spec', 'ai4e_core', 'ai4e_contrib', 'ai4e_task'):\n"
        "        path = Path(importlib.import_module(name).__file__).resolve()\n"
        "        if not path.is_relative_to(root):\n"
        "            raise RuntimeError('worker module escaped installed environment: '+str(path))\n"
        "        modules[name] = str(path)\n"
        "    result = dict(pid=os.getpid(), python=sys.executable, prefix=sys.prefix, modules=modules)\n"
        f"    destination = Path({str(evidence)!r}) / ('runtime-'+str(os.getpid())+'.json')\n"
        "    destination.write_text(json.dumps(result, indent=2))\n"
    )
    path = source / "pipeline.py"
    body = path.read_text()
    marker = 'if __name__ == "__main__":\n'
    if body.count(marker) != 1:
        raise ValueError("复制案例缺少唯一公开入口")
    path.write_text(
        body.replace(
            marker, marker + "    from installed_runtime_probe import verify\n    verify()\n"
        )
    )


def check_summary(path, updates, *, derived):
    """读真实训练/推理/后处理产物，不以进程退出或import代替功能证据。"""
    import numpy as np
    import torch

    from ai4e_core.abilities.data.save.array_manifest import read_arrays

    summary = json.loads(path.read_text())
    if summary["failed"] or summary["research_status"] != "completed":
        raise AssertionError(f"运行未完整成功: {path}")
    reports = summary["reports"]
    if not {"train", "infer", "post"} <= reports.keys():
        raise AssertionError("缺少真实三阶段报告")
    checkpoint = Path(reports["train"]["checkpoint"])
    state = torch.load(checkpoint, map_location="cpu", weights_only=False)
    if state["updates"] != updates or len(state["history"]) != updates:
        raise AssertionError("检查点未达到指定累计更新数")
    if not state["optimizer"]["state"] or not all(
        torch.isfinite(value).all() for value in state["model"].values()
    ):
        raise AssertionError("参数非有限或没有真实优化器状态")
    record, arrays = read_arrays(reports["infer"]["results"], kind="classic-results-v1")
    if (
        arrays["prediction"].shape != arrays["target"].shape
        or not np.isfinite(arrays["prediction"]).all()
    ):
        raise AssertionError("完整固定预测不合法")
    if len(reports["post"]["rows"]) != len(record["metadata"]["ids"]):
        raise AssertionError("后处理样本不完整")
    if derived and (not record["metadata"]["derived"] or not reports["post"].get("derived")):
        raise AssertionError("用户派生输出未完成保存与消费")
    if record["metadata"]["case"] == "shapenet_volume" and "original_mesh" not in reports["post"]:
        raise AssertionError("缺少原网格回贴评价")
    metrics = json.loads((path.parent / "artifacts/metrics.json").read_text())["items"]
    if len(metrics) != len(record["metadata"]["fields"]):
        raise AssertionError("逐字段科学指标未登记")
    return {
        "summary": str(path),
        "checkpoint": str(checkpoint),
        "updates": updates,
        "results": reports["infer"]["results"],
        "post": reports["post"],
        "metrics": metrics,
    }


def check_post_summary(path, expected, results):
    """核对post-only真实writer报告、科学指标及新的固定结果引用。"""
    summary = json.loads(path.read_text())
    if summary["failed"] or summary["research_status"] != "completed":
        raise AssertionError("独立固定结果后处理未成功")
    if summary["stage_events"] != [{"stage": "post", "status": "succeeded"}]:
        raise AssertionError("独立post运行了非后处理阶段")
    if set(summary["reports"]) != {"post"} or summary["reports"]["post"] != expected["post"]:
        raise AssertionError("搬移后评价、original_mesh或derived报告改变")
    metrics = json.loads((path.parent / "artifacts/metrics.json").read_text())["items"]
    if metrics.keys() != expected["metrics"].keys():
        raise AssertionError("搬移后的逐字段指标集合改变")
    for name, metric in metrics.items():
        for key in ("name", "value", "stage", "semantics"):
            if metric[key] != expected["metrics"][name][key]:
                raise AssertionError(f"搬移后指标或科学口径改变: {name}/{key}")
        if metric["assets"] != [str(results)]:
            raise AssertionError("独立post仍引用旧结果")
    if (path.parent / "checkpoints").exists():
        raise AssertionError("独立post不应产生检查点")
    return {
        "summary": str(path),
        "results": str(results),
        "post": summary["reports"]["post"],
        "metrics": metrics,
        "post_identical": True,
        "training_preparation_checkpoint_inputs_disabled": True,
    }


def direct(source, cfg, destination, *, derived, post_expected=None):
    """运行复制目录的原pipeline正文，保留其launch、stage和writer行为。"""
    import yaml

    destination.mkdir()
    cfg["run_root"] = str(destination / "runs")
    cfg["data_root"] = str(destination / "data")
    config = source / "config.yaml"
    config.write_text(yaml.safe_dump(cfg, sort_keys=False))
    before_argv, before_cwd = sys.argv, Path.cwd()
    sys.path.insert(0, str(source))
    entry = source / ("post.py" if post_expected is not None else "pipeline.py")
    sys.argv = [str(entry), "--config", str(config)]
    try:
        os.chdir(source)
        with (
            (destination / "console.log").open("w") as log,
            contextlib.redirect_stdout(log),
            contextlib.redirect_stderr(log),
        ):
            try:
                runpy.run_path(str(entry), run_name="__main__")
            except SystemExit as exc:
                if exc.code not in (None, 0):
                    raise RuntimeError(f"复制入口失败: {destination / 'console.log'}") from exc
    finally:
        sys.argv = before_argv
        os.chdir(before_cwd)
        sys.path.remove(str(source))
    summaries = list((destination / "runs").glob("*/summary.json"))
    if len(summaries) != 1:
        raise AssertionError("direct-core运行摘要数量不符")
    if post_expected is not None:
        return check_post_summary(summaries[0], post_expected, cfg["inputs"]["post"]["results"])
    return check_summary(summaries[0], cfg["train"]["updates"], derived=derived)


def main():
    """单项串行执行；所有失败留下报告，Task必须到终态且清理本次worker。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--environment", type=Path, required=True)
    parser.add_argument("--case-id", choices=CASE_IDS, required=True)
    parser.add_argument("--preparation", type=Path, required=True)
    parser.add_argument("--configuration", type=Path, help="可选完整模型配置覆盖；不读取仓库默认值")
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--seconds", type=float, required=True)
    parser.add_argument(
        "--budget-identity", required=True, help="主控BudgetLedger中此次收费的组合身份"
    )
    parser.add_argument("--with-task", action="store_true")
    args = parser.parse_args()
    if not 0 < args.seconds <= 10800:
        parser.error("seconds须来自组合剩余预算且不超过10800")
    root, environment = args.root.resolve(), args.environment.resolve()
    root.mkdir(parents=True, exist_ok=False)
    report = {
        "status": "running",
        "case_id": args.case_id,
        "budget_identity": args.budget_identity,
        "budget_accounting": "external BudgetLedger.measure",
        "phases": {},
        "relocations": {},
    }
    started = time.monotonic()
    deadline = started + args.seconds
    task_api = None
    active = None

    def interrupted(signum, frame):
        raise TimeoutError("installed replay deadline or termination signal")

    previous = {sig: signal.signal(sig, interrupted) for sig in (signal.SIGTERM, signal.SIGALRM)}
    signal.setitimer(signal.ITIMER_REAL, args.seconds)
    try:
        import ai4e_task as task_api
        import torch
        import yaml
        from omegaconf import OmegaConf

        torch.set_num_threads(2)
        report["runtime"] = installed_paths(environment)
        report["help"] = {
            "run_task": task_api.read_help_topic("capability:run-task"),
            "manage": task_api.read_help_topic("getting-started:manage-with-task"),
        }
        for name in ("copy_example", "create_project", "new_task", "submit_run", "wait_run"):
            report["help"][name] = task_api.describe_help_symbol("ai4e_task." + name)
        write_json(root / "report.json", report)
        source = root / "copied-case"
        report["copy"] = task_api.copy_example(args.case_id, source)
        add_worker_probe(source, root, environment)
        prepared, report["relocations"]["preparation"] = copy_asset(
            args.preparation, root / "moved-preparation", bundle=True
        )
        cfg = yaml.safe_load((source / "config.yaml").read_text())
        if args.configuration:
            cfg = OmegaConf.to_container(
                OmegaConf.merge(cfg, OmegaConf.load(args.configuration)), resolve=True
            )
        cfg["inputs"]["rawprep"]["source"] = None
        cfg["inputs"]["trainprep"]["dataset"] = None
        cfg["inputs"]["train"]["preparation"] = str(prepared)
        cfg["inputs"]["infer"]["preparation"] = str(prepared)
        cfg["inputs"]["train"]["resume"] = None
        cfg["inputs"]["infer"]["checkpoint"] = None
        cfg["inputs"]["post"]["results"] = None
        cfg["pipeline"]["stages"] = ["train", "infer", "post"]
        cfg["train"].update(updates=1, checkpoint_every=1, device=args.device)
        cfg["infer"]["device"] = args.device
        derived = cfg["components"]["derived"] is not None

        for name, updates in (("direct", 1), ("resumed", 2)):
            cfg["train"]["updates"] = updates
            cfg["train"]["seconds"] = min(9000, deadline - time.monotonic())
            if updates == 2:
                moved, report["relocations"]["checkpoint"] = copy_asset(
                    report["phases"]["direct"]["checkpoint"], root / "moved-checkpoint.pt"
                )
                cfg["inputs"]["train"]["resume"] = str(moved)
            value = direct(source, cfg, root / name, derived=derived)
            report["phases"][name] = value
            write_json(root / "report.json", report)
        first = torch.load(
            report["phases"]["direct"]["checkpoint"], weights_only=False, map_location="cpu"
        )
        resumed = torch.load(
            report["phases"]["resumed"]["checkpoint"], weights_only=False, map_location="cpu"
        )
        if resumed["history"][:1] != first["history"] or resumed["contract"] != first["contract"]:
            raise AssertionError("恢复未保留历史或科学契约")
        if not any(
            not torch.equal(first["model"][key], value) for key, value in resumed["model"].items()
        ):
            raise AssertionError("恢复后没有真实权重更新")

        fixed, report["relocations"]["results"] = copy_asset(
            report["phases"]["resumed"]["results"], root / "moved-results", bundle=True
        )
        post_cfg = copy.deepcopy(cfg)
        post_cfg["pipeline"]["stages"] = ["post"]
        post_cfg["inputs"] = {
            stage: dict.fromkeys(values) for stage, values in post_cfg["inputs"].items()
        }
        post_cfg["inputs"]["post"]["results"] = str(fixed)
        report["phases"]["independent_post"] = direct(
            source,
            post_cfg,
            root / "independent-post",
            derived=derived,
            post_expected=report["phases"]["resumed"],
        )
        write_json(root / "report.json", report)

        if args.with_task:
            cfg["inputs"]["train"]["resume"] = None
            cfg["train"].update(updates=1, seconds=min(9000, deadline - time.monotonic()))
            (source / "config.yaml").write_text(yaml.safe_dump(cfg, sort_keys=False))
            project = root / "task-project"
            task_api.create_project(project, name=args.case_id)
            record = task_api.new_task(project, "installed-replay", source=source)
            submitted = task_api.submit_run(project, record["id"])
            active = (project, submitted["id"])
            report["task"] = {"project": str(project), "task": record, "submitted": submitted}
            write_json(root / "report.json", report)
            while True:
                finished = task_api.wait_run(
                    project, submitted["id"], timeout=min(30, max(0, deadline - time.monotonic()))
                )
                if finished["status"] in {"succeeded", "failed", "stopped", "unknown"}:
                    break
            report["task"]["finished"] = finished
            if finished["status"] != "succeeded":
                raise RuntimeError(f"Task未成功: {finished}")
            probe = root / f"runtime-{finished['pid']}.json"
            if not probe.is_file():
                raise AssertionError("缺少Task worker自身安装模块证据")
            report["task"]["runtime"] = json.loads(probe.read_text())
            report["phases"]["task"] = check_summary(
                project / finished["run_path"] / "summary.json", 1, derived=derived
            )
            active = None
        report["status"] = "passed"
    except BaseException as exc:
        report.update(status="failed", error=repr(exc), traceback=traceback.format_exc())
        raise
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        if active is not None and task_api is not None:
            try:
                report["cleanup"] = task_api.stop_run(*active, timeout=10)
            except Exception as exc:  # noqa: BLE001 - 清理失败须保留原始失败及证据
                report["cleanup_error"] = repr(exc)
        for sig, handler in previous.items():
            signal.signal(sig, handler)
        report["elapsed_seconds"] = time.monotonic() - started
        write_json(root / "report.json", report)
    print(
        json.dumps(
            {"status": report["status"], "report": str(root / "report.json")}, ensure_ascii=False
        )
    )


if __name__ == "__main__":
    main()
