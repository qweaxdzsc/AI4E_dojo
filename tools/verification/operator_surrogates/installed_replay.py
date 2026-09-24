"""独立 wheel 的外复制、恢复/状态读回、搬移后处理及 Task 重放。

只编写工具不意味着运行验收。主控必须把本脚本与原 classic installed_replay.py
一同复制到仓库外，后者命名 classic_installed_replay.py；固定 SHA256 后动态
读取其公共 helper。本文件不导入 tools 或读取仓库 recipe，案例只从安装包复制。
一次调用消费一个父组合的剩余 seconds；重试和扩展仍计入主控同一预算账本。
算子执行1更新→恢复至2→搬移post→Task1；传统代理拟合/读回→搬移post→Task拟合，
不制造优化器或resume语义。用户POD-MLP扩展保留其真实fit实现和诊断。
"""

from __future__ import annotations

import argparse
import contextlib
import copy
import importlib
import importlib.util
import json
import os
import runpy
import signal
import sys
import textwrap
import time
import traceback
from pathlib import Path

HELPER_SHA256 = "c84e904c34af68deb2af6935cc886dc791c37a3d8717aca9d8fff9f201cafa90"
OPERATOR_CASES = (
    "operator_learning.darcy",
    "operator_learning.shapenet_volume",
    "operator_learning.double_cylinder",
    "recipe_extensions.operator_branch_replacement",
    "recipe_extensions.operator_physical_loss",
)
SURROGATE_CASES = (
    "surrogate_modeling.nasa_crm",
    "surrogate_modeling.double_cylinder",
    "recipe_extensions.pod_surrogate_replacement",
)


def load_helper():
    """只加载随验证器复制的已核验脚本，不回退仓库或任意导入路径。"""
    import hashlib

    path = Path(__file__).resolve().with_name("classic_installed_replay.py")
    with path.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    if digest != HELPER_SHA256:
        raise ValueError("classic 安装验证 helper 摘要不符，须复制本次锁定原文件")
    spec = importlib.util.spec_from_file_location("_installed_classic_helper", path)
    if spec is None or spec.loader is None:
        raise ImportError("无法加载安装验证 helper")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module, {
        "path": str(path),
        "sha256": digest,
        "origin": "tools/verification/classic_networks/installed_replay.py",
    }


def installed_modules(environment):
    """核对所有已加载 ai4e 模块的实际文件/命名空间路径，不只查顶层包。"""
    environment = Path(environment).resolve()
    if Path(sys.prefix).resolve() != environment:
        raise RuntimeError("当前解释器不在声明的独立安装环境")
    for name in ("ai4e_spec", "ai4e_core", "ai4e_contrib", "ai4e_task"):
        importlib.import_module(name)
    result = {}
    for name, module in list(sys.modules.items()):
        if not name.startswith(("ai4e_spec", "ai4e_core", "ai4e_contrib", "ai4e_task")):
            continue
        paths = []
        if getattr(module, "__file__", None):
            paths.append(Path(module.__file__).resolve())
        paths.extend(Path(path).resolve() for path in getattr(module, "__path__", ()))
        if any(not path.is_relative_to(environment) for path in paths):
            raise RuntimeError(f"已加载模块不来自独立 wheel 环境: {name}: {paths}")
        if paths:
            result[name] = sorted({str(path) for path in paths})
    return {"pid": os.getpid(), "python": sys.executable, "prefix": sys.prefix, "modules": result}


def add_runtime_probe(helper, source, root, environment):
    """复用基础探针并增加执行后全模块来源；Task 自己写 worker 最终证据。"""
    helper.add_worker_probe(source, root, environment)
    probe = source / "installed_runtime_probe.py"
    # 安装测试本身生成普通用户文件；不把验证器路径或仓库代码放入模型计算。
    extra = f"""

def verify(phase="initial"):
    root = Path({str(environment)!r})
    if Path(sys.prefix).resolve() != root:
        raise RuntimeError("worker interpreter escaped installed environment")
    for name in ("ai4e_spec", "ai4e_core", "ai4e_contrib", "ai4e_task"):
        importlib.import_module(name)
    modules = {{}}
    for name, module in list(sys.modules.items()):
        if not name.startswith(("ai4e_spec", "ai4e_core", "ai4e_contrib", "ai4e_task")):
            continue
        paths = []
        if getattr(module, "__file__", None):
            paths.append(Path(module.__file__).resolve())
        paths.extend(Path(p).resolve() for p in getattr(module, "__path__", ()))
        if any(not path.is_relative_to(root) for path in paths):
            raise RuntimeError("worker module escaped installed environment: "+name)
        if paths:
            modules[name] = sorted({{str(path) for path in paths}})
    evidence = dict(pid=os.getpid(), python=sys.executable, prefix=sys.prefix,
                    phase=phase, modules=modules)
    destination = Path({str(root)!r}) / ("runtime-"+str(os.getpid())+"-"+phase+".json")
    destination.write_text(json.dumps(evidence, indent=2))
"""
    probe.write_text(probe.read_text() + extra, encoding="utf-8")
    for filename in ("pipeline.py", "post.py"):
        path = source / filename
        marker = 'if __name__ == "__main__":\n'
        body = path.read_text()
        if body.count(marker) != 1:
            raise ValueError(f"复制入口没有唯一 main: {filename}")
        prefix, entry = body.split(marker)
        path.write_text(
            prefix
            + marker
            + "    try:\n"
            + textwrap.indent(entry, "    ")
            + "\n    finally:\n        from installed_runtime_probe import verify\n"
            '        verify("final")\n',
            encoding="utf-8",
        )


@contextlib.contextmanager
def source_imports(source):
    """隔离可复制案例的局部模块缓存，退出恢复调用者原有模块和搜索路径。"""
    source = Path(source).resolve()
    local_names = {path.stem for path in source.glob("*.py")}
    previous = {name: sys.modules.pop(name) for name in local_names if name in sys.modules}
    sys.path.insert(0, str(source))
    try:
        yield
    finally:
        sys.path.remove(str(source))
        for name in local_names:
            sys.modules.pop(name, None)
        sys.modules.update(previous)


def run_source(source, cfg, destination, *, post_only=False):
    """执行仓库外复制的真实正文，只返回唯一运行摘要，随后按模型类型检查。"""
    import yaml

    destination.mkdir(parents=True, exist_ok=False)
    cfg = copy.deepcopy(cfg)
    cfg.update(run_root=str(destination / "runs"), data_root=str(destination / "data"))
    config = source / "config.yaml"
    config.write_text(yaml.safe_dump(cfg, sort_keys=False), encoding="utf-8")
    before_argv, before_cwd = sys.argv, Path.cwd()
    entry = source / ("post.py" if post_only else "pipeline.py")
    sys.argv = [str(entry), "--config", str(config)]
    try:
        os.chdir(source)
        with (
            source_imports(source),
            (destination / "console.log").open("w") as log,
            contextlib.redirect_stdout(log),
            contextlib.redirect_stderr(log),
        ):
            try:
                runpy.run_path(str(entry), run_name="__main__")
            except SystemExit as exc:
                if exc.code not in (None, 0):
                    raise RuntimeError(f"复制入口执行失败: {destination / 'console.log'}") from exc
    finally:
        sys.argv = before_argv
        os.chdir(before_cwd)
    summaries = list((destination / "runs").glob("*/summary.json"))
    if len(summaries) != 1:
        raise AssertionError("复制入口没有产生唯一运行摘要")
    return summaries[0]


def check_surrogate_summary(path, cfg):
    """拟合状态与固定结果真实读回；传统算法不检查或伪造神经优化器。"""
    import numpy as np

    from ai4e_core.abilities.data.save.array_manifest import read_arrays
    from ai4e_core.abilities.data.save.surrogate import read_state

    summary = json.loads(path.read_text())
    if summary["failed"] or summary["research_status"] != "completed":
        raise AssertionError("代理复制入口未完整成功")
    reports = summary["reports"]
    if not {"train", "infer", "post"} <= reports.keys():
        raise AssertionError("代理缺拟合/预测/后处理报告")
    state, context = read_state(reports["train"]["checkpoint"])
    if context["model"] != cfg["model"] or context["components"] != cfg["components"]:
        raise AssertionError("拟合模型与组件上下文未按本次配置保存")
    record, arrays = read_arrays(reports["infer"]["results"], kind="classic-results-v1")
    if (
        arrays["prediction"].shape != arrays["target"].shape
        or not np.isfinite(arrays["prediction"]).all()
    ):
        raise AssertionError("代理完整固定预测不合法")
    if len(reports["post"]["rows"]) != len(record["metadata"]["ids"]):
        raise AssertionError("代理后处理样本不完整")
    metrics = json.loads((path.parent / "artifacts/metrics.json").read_text())["items"]
    if len(metrics) != len(record["metadata"]["fields"]):
        raise AssertionError("代理逐字段指标未登记")
    return {
        "summary": str(path),
        "checkpoint": reports["train"]["checkpoint"],
        "state_kind": state["kind"],
        "context": context,
        "diagnostics": reports["train"]["diagnostics"],
        "results": reports["infer"]["results"],
        "post": reports["post"],
        "metrics": metrics,
        "resume": "not requested; fitted predictor state readback is checked separately",
    }


def check_complete_results(fixed, prepared, *, surrogate):
    """对照完整 test 的样本、字段、真值、mask、实体和真实时间，不能仅核形状。"""
    import numpy as np

    from ai4e_core.abilities.data.save.array_manifest import read_arrays

    if surrogate:
        from ai4e_contrib.application.surrogate_modeling.preparation import read_prepared
    else:
        from ai4e_contrib.application.operator_learning.preparation import read_prepared
    original_record, original = read_prepared(prepared, "test")
    record, arrays = read_arrays(fixed, kind="classic-results-v1")
    for key in ("ids", "fields", "units", "statistics", "case"):
        if record["metadata"][key] != original_record["metadata"][key]:
            raise AssertionError(f"固定结果元数据改变: {key}")
    for name, source in (
        ("target", "physical_target"),
        ("valid", "valid"),
        ("entity_ids", "entity_ids"),
        ("physical_input", "physical_input"),
    ):
        np.testing.assert_array_equal(arrays[name], original[source], err_msg=name)
    if "times" in original:
        np.testing.assert_array_equal(arrays["times"], original["times"], err_msg="times")
    return {
        "samples": len(original_record["metadata"]["ids"]),
        "prediction_shape": list(arrays["prediction"].shape),
        "all_prepared_test_identities": True,
        "all_array_hashes_checked": True,
    }


@contextlib.contextmanager
def unavailable_owned_paths(paths):
    """只临时隐藏本次生成副本以排除旧路径回读，任何退出都恢复；不动用户原件。"""
    moved = []
    try:
        for path in paths:
            path = Path(path)
            if not path.exists():
                continue
            hidden = path.with_name(path.name + ".replay-unavailable")
            if hidden.exists():
                raise FileExistsError(hidden)
            path.rename(hidden)
            moved.append((path, hidden))
        yield
    finally:
        for original, hidden in reversed(moved):
            hidden.rename(original)


def moved_post(helper, source, cfg, root, expected, report, *, hidden_paths):
    """只用搬移结果执行 post，显式禁用训练/准备/检查点输入及本次旧副本路径。"""
    fixed, report["relocations"]["results"] = helper.copy_asset(
        expected["results"],
        root / "moved-results",
        bundle=True,
    )
    post_cfg = copy.deepcopy(cfg)
    post_cfg["pipeline"]["stages"] = ["post"]
    post_cfg["inputs"] = {stage: dict.fromkeys(values) for stage, values in cfg["inputs"].items()}
    post_cfg["inputs"]["post"]["results"] = str(fixed)
    with unavailable_owned_paths(hidden_paths):
        summary = run_source(source, post_cfg, root / "independent-post", post_only=True)
        evidence = helper.check_post_summary(summary, expected, fixed)
    evidence["prior_owned_paths_temporarily_unavailable"] = [str(path) for path in hidden_paths]
    return evidence


def remaining(deadline):
    """从同一父组合截止时间取剩余预算，不对各阶段重新给三小时。"""
    seconds = deadline - time.monotonic()
    if seconds <= 0:
        raise TimeoutError("安装重放累计预算已耗尽")
    return min(seconds, 10800)


def equal_recovery_state(left, right):
    """连续与断点路径的模型、优化器、随机及数据流状态逐值相同。"""
    import numpy as np
    import torch

    if isinstance(left, torch.Tensor):
        torch.testing.assert_close(left, right, rtol=0, atol=0)
    elif isinstance(left, np.ndarray):
        np.testing.assert_array_equal(left, right)
    elif isinstance(left, dict):
        if left.keys() != right.keys():
            raise AssertionError("恢复状态键不一致")
        for key in left:
            equal_recovery_state(left[key], right[key])
    elif isinstance(left, (tuple, list)):
        if type(left) is not type(right) or len(left) != len(right):
            raise AssertionError("恢复序列不一致")
        for a, b in zip(left, right, strict=True):
            equal_recovery_state(a, b)
    elif left != right:
        raise AssertionError("恢复标量不一致")


def replay_operator(helper, source, cfg, root, prepared, report, *, deadline, device):
    """公开 direct1→resume2→完整infer/post→搬移post，返回Task1的配置。"""
    import torch

    from ai4e_core.abilities.training.iteration_stream import IterationStream

    cfg["train"].update(updates=1, checkpoint_every=1, device=device)
    cfg["infer"]["device"] = device
    cfg["inputs"]["train"]["resume"] = None
    derived = cfg["components"].get("derived") is not None
    for name, updates in (("direct", 1), ("resumed", 2)):
        cfg["train"].update(updates=updates, seconds=remaining(deadline))
        if updates == 2:
            moved, report["relocations"]["checkpoint"] = helper.copy_asset(
                report["phases"]["direct"]["checkpoint"],
                root / "moved-checkpoint.pt",
            )
            cfg["inputs"]["train"]["resume"] = str(moved)
        summary = run_source(source, cfg, root / name)
        checked = helper.check_summary(summary, updates, derived=derived)
        checked["complete_results"] = check_complete_results(
            checked["results"], prepared, surrogate=False
        )
        report["phases"][name] = checked
        helper.write_json(root / "report.json", report)
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
        raise AssertionError("恢复后没有真实参数更新")
    stream = IterationStream(first["stream"]["count"], first["stream"]["batch_size"])
    stream.load_state_dict(first["stream"])
    stream.next()
    for key, value in stream.state_dict().items():
        actual = resumed["stream"][key]
        if isinstance(value, torch.Tensor):
            torch.testing.assert_close(value, actual, rtol=0, atol=0)
        elif value != actual:
            raise AssertionError(f"恢复取批状态未推进一批: {key}")
    for key, state in first["optimizer"]["state"].items():
        if resumed["optimizer"]["state"][key]["step"] != state["step"] + 1:
            raise AssertionError("Adam优化器没有从保存步骤接续")
    report["recovery"] = {
        "history_prefix_identical": True,
        "contract_identical": True,
        "optimizer_advanced_once": True,
        "stream_advanced_once": True,
        "weights_updated": True,
    }
    continuous_cfg = copy.deepcopy(cfg)
    continuous_cfg["inputs"]["train"]["resume"] = None
    continuous_cfg["train"]["seconds"] = remaining(deadline)
    continuous_summary = run_source(source, continuous_cfg, root / "continuous")
    continuous = helper.check_summary(continuous_summary, 2, derived=derived)
    continuous_state = torch.load(continuous["checkpoint"], weights_only=False, map_location="cpu")
    # 实际运行路径与有效配置快照自然不同；科学状态不因此排除。
    keys = set(resumed) - {"effective_config"}
    if keys != set(continuous_state) - {"effective_config"}:
        raise AssertionError("连续与恢复检查点字段不同")
    equal_recovery_state({k: resumed[k] for k in keys}, {k: continuous_state[k] for k in keys})
    report["phases"]["continuous"] = continuous
    report["recovery"]["continuous_state_exact"] = True
    report["phases"]["independent_post"] = moved_post(
        helper,
        source,
        cfg,
        root,
        report["phases"]["resumed"],
        report,
        hidden_paths=[
            root / "direct",
            root / "resumed",
            root / "moved-preparation",
            root / "moved-checkpoint.pt",
        ],
    )
    cfg["inputs"]["train"]["resume"] = None
    cfg["train"].update(updates=1, seconds=remaining(deadline))
    return cfg


def replay_surrogate(helper, source, cfg, root, prepared, report, *, deadline):
    """公开拟合后搬移状态并重建预测；不为直接代数拟合伪造resume。"""
    import numpy as np

    from ai4e_contrib.application.surrogate_modeling.prediction import predict_prepared
    from ai4e_contrib.application.surrogate_modeling.preparation import read_prepared
    from ai4e_core.abilities.data.save.array_manifest import read_arrays
    from ai4e_core.abilities.data.save.surrogate import read_state

    cfg["train"]["seconds"] = remaining(deadline)
    summary = run_source(source, cfg, root / "direct")
    checked = check_surrogate_summary(summary, cfg)
    checked["complete_results"] = check_complete_results(
        checked["results"], prepared, surrogate=True
    )
    report["phases"]["direct"] = checked
    moved, report["relocations"]["fitted_state"] = helper.copy_asset(
        checked["checkpoint"],
        root / "moved-fitted-state",
        bundle=True,
    )
    remaining(deadline)
    with unavailable_owned_paths([root / "direct"]), source_imports(source):
        configuration = importlib.import_module("configuration")
        state, context = read_state(moved)
        prepared_record, _ = read_prepared(prepared, "test")
        if context != configuration.fit_context(cfg, prepared, prepared_record["metadata"]):
            raise AssertionError("搬移状态内容与准备合同不一致")
        predictor = configuration.component(cfg["components"]["rebuild"])(state)
        replayed = predict_prepared(
            state,
            prepared,
            root / "readback-results",
            batch_size=cfg["infer"]["batch_size"],
            predictor=predictor,
        )
    original_record, original = read_arrays(checked["results"], kind="classic-results-v1")
    replayed_record, replayed_arrays = read_arrays(replayed, kind="classic-results-v1")
    if (
        original_record["metadata"] != replayed_record["metadata"]
        or original.keys() != replayed_arrays.keys()
    ):
        raise AssertionError("状态读回改变完整输出或元数据")
    for key in original:
        np.testing.assert_array_equal(original[key], replayed_arrays[key], err_msg=key)
    report["phases"]["state_readback"] = {
        "checkpoint": str(moved),
        "results": replayed,
        "all_arrays_identical": True,
        "context_identical": True,
        "original_fitted_directory_unavailable": True,
        "state_kind": state["kind"],
    }
    if cfg["components"]["fit"].startswith("pod_mlp.") and state["kind"] != "local-pod-mlp-v1":
        raise AssertionError("用户POD系数代理没有成为实际拟合状态")
    report["phases"]["independent_post"] = moved_post(
        helper,
        source,
        cfg,
        root,
        checked,
        report,
        hidden_paths=[
            root / "direct",
            root / "moved-preparation",
            root / "moved-fitted-state",
            root / "readback-results",
        ],
    )
    report["recovery"] = {"mode": "fitted state readback", "optimizer_resume": "not requested"}
    cfg["train"]["seconds"] = remaining(deadline)
    return cfg


def main():
    """一次执行一个已安装案例，默认完整包含 Task；所有失败保留报告并清理worker。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--environment", type=Path, required=True)
    parser.add_argument("--case-id", choices=OPERATOR_CASES + SURROGATE_CASES, required=True)
    parser.add_argument("--preparation", type=Path, required=True)
    parser.add_argument(
        "--configuration", type=Path, help="可选完整配置或覆盖，来源也须复制到仓库外"
    )
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--seconds", type=float, required=True)
    parser.add_argument("--budget-identity", required=True)
    parser.add_argument(
        "--with-task", action="store_true", help="兼容旧调度参数；本工具始终验证 Task"
    )
    args = parser.parse_args()
    if not 0 < args.seconds <= 10800:
        parser.error("seconds须来自父组合剩余预算且不超过10800")
    root, environment = args.root.resolve(), args.environment.resolve()
    root.mkdir(parents=True, exist_ok=False)
    helper, provenance = load_helper()
    report = {
        "status": "running",
        "case_id": args.case_id,
        "budget_identity": args.budget_identity,
        "budget_accounting": "external parent combination ledger",
        "helper": provenance,
        "phases": {},
        "relocations": {},
    }
    started, task_api, active = time.monotonic(), None, None
    deadline = started + args.seconds

    def interrupted(signum, frame):
        raise TimeoutError("installed operator/surrogate replay deadline or termination signal")

    previous = {sig: signal.signal(sig, interrupted) for sig in (signal.SIGTERM, signal.SIGALRM)}
    signal.setitimer(signal.ITIMER_REAL, args.seconds)
    try:
        import ai4e_task as task_api
        import torch
        import yaml
        from omegaconf import OmegaConf

        torch.set_num_threads(2)
        report["runtime"] = helper.installed_paths(environment)
        report["runtime_all_modules"] = installed_modules(environment)
        report["help"] = {
            "run_task": task_api.read_help_topic("capability:run-task"),
            "manage": task_api.read_help_topic("getting-started:manage-with-task"),
        }
        for name in ("copy_example", "create_project", "new_task", "submit_run", "wait_run"):
            report["help"][name] = task_api.describe_help_symbol("ai4e_task." + name)
        source = root / "copied-case"
        report["copy"] = task_api.copy_example(args.case_id, source)
        add_runtime_probe(helper, source, root, environment)
        prepared, report["relocations"]["preparation"] = helper.copy_asset(
            args.preparation,
            root / "moved-preparation",
            bundle=True,
        )
        cfg = yaml.safe_load((source / "config.yaml").read_text())
        if args.configuration:
            overrides = OmegaConf.to_container(OmegaConf.load(args.configuration), resolve=True)
            previous_family = cfg["model"]["family"]
            cfg = OmegaConf.to_container(OmegaConf.merge(cfg, overrides), resolve=True)
            if cfg["model"]["family"] != previous_family:
                if "parameters" not in overrides.get("model", {}):
                    raise ValueError("切换模型族时必须给出完整 model.parameters")
                # 不让旧族的模式数/核参数静默残留到新构造器。
                cfg["model"]["parameters"] = copy.deepcopy(overrides["model"]["parameters"])
        for values in cfg["inputs"].values():
            for key in values:
                values[key] = None
        cfg["inputs"]["train"]["preparation"] = str(prepared)
        cfg["inputs"]["infer"]["preparation"] = str(prepared)
        cfg["pipeline"]["stages"] = ["train", "infer", "post"]
        surrogate = args.case_id in SURROGATE_CASES
        report["components"] = cfg["components"]
        helper.write_json(root / "report.json", report)
        if surrogate:
            cfg = replay_surrogate(helper, source, cfg, root, prepared, report, deadline=deadline)
        else:
            cfg = replay_operator(
                helper, source, cfg, root, prepared, report, deadline=deadline, device=args.device
            )
        report["runtime_after_direct"] = installed_modules(environment)
        # 同一复制案例交给公开 Task；Task 启动前重新保存完整三阶段配置。
        cfg["train"]["seconds"] = remaining(deadline)
        (source / "config.yaml").write_text(yaml.safe_dump(cfg, sort_keys=False), encoding="utf-8")
        project = root / "task-project"
        task_api.create_project(project, name=args.case_id)
        record = task_api.new_task(project, "installed-replay", source=source)
        submitted = task_api.submit_run(project, record["id"])
        active = (project, submitted["id"])
        report["task"] = {"project": str(project), "task": record, "submitted": submitted}
        helper.write_json(root / "report.json", report)
        while True:
            finished = task_api.wait_run(
                project, submitted["id"], timeout=min(30, remaining(deadline))
            )
            if finished["status"] in {"succeeded", "failed", "stopped", "unknown"}:
                break
        report["task"]["finished"] = finished
        if finished["status"] != "succeeded":
            raise RuntimeError(f"安装环境Task未成功: {finished}")
        probe = root / f"runtime-{finished['pid']}-final.json"
        if not probe.is_file():
            raise AssertionError("缺少Task worker执行后的全模块来源证据")
        report["task"]["runtime"] = json.loads(probe.read_text())
        summary = project / finished["run_path"] / "summary.json"
        checked = (
            check_surrogate_summary(summary, cfg)
            if surrogate
            else helper.check_summary(
                summary, 1, derived=cfg["components"].get("derived") is not None
            )
        )
        checked["complete_results"] = check_complete_results(
            checked["results"], prepared, surrogate=surrogate
        )
        report["phases"]["task"] = checked
        active = None
        remaining(deadline)
        report["runtime_final"] = installed_modules(environment)
        report["status"] = "passed"
    except BaseException as exc:
        report.update(status="failed", error=repr(exc), traceback=traceback.format_exc())
        raise
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        if active is not None and task_api is not None:
            try:
                report["cleanup"] = task_api.stop_run(*active, timeout=10)
            except Exception as exc:  # noqa: BLE001 - 保留原始错误与清理错误
                report["cleanup_error"] = repr(exc)
        for sig, handler in previous.items():
            signal.signal(sig, handler)
        report["elapsed_seconds"] = time.monotonic() - started
        helper.write_json(root / "report.json", report)
    print(
        json.dumps(
            {"status": report["status"], "report": str(root / "report.json")}, ensure_ascii=False
        )
    )


if __name__ == "__main__":
    main()
