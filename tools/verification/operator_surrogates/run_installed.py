"""八项独立安装重放的主控串行包装器，沿用既有十一组合预算。

不构建或安装包，不触碰源验证结果，也不根据旧通过记录跳过本次安装验证。
默认顺序执行八项；--case-id 只重试指定项。失败、重试及旧报告全部保留。
子进程只消费 root/installed 的 wheel，验证器/helper 固定复制到仓库外。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import shutil
import signal
import subprocess
import time
import uuid
from pathlib import Path

from tools.verification.classic_networks.budget import BudgetExceeded, BudgetLedger
from tools.verification.operator_surrogates.installed_replay import HELPER_SHA256

CASES = (
    ("operator_learning.darcy", "darcy", "fno-darcy"),
    ("operator_learning.shapenet_volume", "shapenet_volume", "fno-shape"),
    ("operator_learning.double_cylinder", "double_cylinder", "fno-double"),
    ("surrogate_modeling.nasa_crm", "nasa_global", "rsm-nasa"),
    ("surrogate_modeling.double_cylinder", "double_cylinder_pod", "pod-rbf-double"),
    ("recipe_extensions.operator_branch_replacement", "shapenet_volume", "deeponet-shape"),
    ("recipe_extensions.operator_physical_loss", "darcy", "fno-darcy"),
    ("recipe_extensions.pod_surrogate_replacement", "double_cylinder_pod", "pod-rbf-double"),
)
SURROGATE_IDS = {CASES[i][0] for i in (3, 4, 7)}


def digest(path):
    """固定验证器及helper真实文件修订，不用导入路径代替来源。"""
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def write(path, record):
    """原子更新汇总；历史尝试与日志保留，不写框架run目录。"""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    try:
        with temporary.open("w", encoding="utf-8") as stream:
            json.dump(record, stream, ensure_ascii=False, indent=2, allow_nan=False)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def stop(process):
    """只停止本次新进程组，先给验证器清理Task的机会，超时再强制结束。"""
    if process is None or process.poll() is not None:
        return
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        process.wait(timeout=5)
        return
    try:
        process.wait(timeout=12)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.wait(timeout=5)


def _runtime(value, environment, *, worker=False):
    if Path(value["prefix"]).resolve() != environment:
        raise AssertionError("报告解释器不是本次独立环境")
    if worker and value.get("phase") != "final":
        raise AssertionError("缺少Task实际执行后的模块来源")
    modules = value["modules"]
    if not {"ai4e_spec", "ai4e_core", "ai4e_contrib", "ai4e_task"} <= modules.keys():
        raise AssertionError("报告未覆盖四个正式安装包")
    for name, paths in modules.items():
        if not isinstance(paths, list) or not paths:
            raise AssertionError(f"模块来源记录不完整: {name}")
        for path in paths:
            resolved = Path(path).resolve()
            if not resolved.is_relative_to(environment) or not resolved.exists():
                raise AssertionError(f"安装模块来源越界或缺失: {name}: {path}")


def assert_result(report, *, identity, budget, environment):
    """逐项核完整重放证据，不能仅以返回码或顶层passed替代功能验收。"""
    if report.get("status") != "passed" or report.get("case_id") != identity:
        raise AssertionError("安装案例身份或完成状态不符")
    if report.get("budget_identity") != budget:
        raise AssertionError("安装重放未计入声明的父组合")
    seconds = report.get("elapsed_seconds")
    if (
        not isinstance(seconds, (int, float))
        or not math.isfinite(seconds)
        or not 0 <= seconds <= 10800
    ):
        raise AssertionError("安装重放耗时缺失、非有限或越界")
    if report["helper"]["sha256"] != HELPER_SHA256:
        raise AssertionError("实际安装helper不是本次固定修订")
    _runtime(report["runtime_final"], environment)
    task = report["task"]
    if task["finished"]["status"] != "succeeded":
        raise AssertionError("Task未实际成功")
    _runtime(task["runtime"], environment, worker=True)
    surrogate = identity in SURROGATE_IDS
    expected = {"direct", "independent_post", "task", "state_readback" if surrogate else "resumed"}
    phases = report["phases"]
    if not expected <= phases.keys():
        raise AssertionError("安装重放步骤不完整")
    checked = ("direct", "task") if surrogate else ("direct", "resumed", "task")
    for name in checked:
        phase = phases[name]
        complete = phase["complete_results"]
        if (
            complete.get("all_prepared_test_identities") is not True
            or complete.get("all_array_hashes_checked") is not True
        ):
            raise AssertionError(f"未核对全部固定test产物: {name}")
        if complete.get("samples", 0) < 1 or not phase["metrics"]:
            raise AssertionError(f"未交付实际样本或指标: {name}")
        for key in ("summary", "checkpoint", "results"):
            if not Path(phase[key]).is_file():
                raise AssertionError(f"步骤产物缺失: {name}/{key}")
    post = phases["independent_post"]
    if post.get("post_identical") is not True or not post.get(
        "prior_owned_paths_temporarily_unavailable"
    ):
        raise AssertionError("搬移后post没有排除旧副本依赖或结果发生变化")
    if post.get("training_preparation_checkpoint_inputs_disabled") is not True:
        raise AssertionError("独立post仍启用训练/准备/检查点输入")
    if any(not Path(post[key]).is_file() for key in ("summary", "results")):
        raise AssertionError("独立post报告或搬移固定结果缺失")
    relocations = report["relocations"]
    for name in ("preparation", "results", "fitted_state" if surrogate else "checkpoint"):
        moved = relocations[name]
        if moved.get("content_identical") is not True or moved.get("source_preserved") is not True:
            raise AssertionError(f"搬移未证明原件保留与逐文件一致: {name}")
    if surrogate:
        state = phases["state_readback"]
        if (
            state.get("all_arrays_identical") is not True
            or state.get("context_identical") is not True
        ):
            raise AssertionError("代理状态读回没有保留预测和上下文")
        if state.get("original_fitted_directory_unavailable") is not True:
            raise AssertionError("代理读回仍可能依赖原拟合目录")
        if (
            identity.endswith("pod_surrogate_replacement")
            and state["state_kind"] != "local-pod-mlp-v1"
        ):
            raise AssertionError("POD用户代理替换未实际生效")
    else:
        for name, updates in (("direct", 1), ("resumed", 2), ("task", 1)):
            if phases[name]["updates"] != updates:
                raise AssertionError(f"算子有效更新次数不同: {name}")
        for key in (
            "history_prefix_identical",
            "contract_identical",
            "optimizer_advanced_once",
            "stream_advanced_once",
            "weights_updated",
        ):
            if report["recovery"].get(key) is not True:
                raise AssertionError(f"算子恢复证据缺失: {key}")
        if identity.startswith("recipe_extensions."):
            for name in checked:
                if not phases[name]["post"].get("derived"):
                    raise AssertionError(f"用户派生结果未消费: {name}")
    return {
        "task_succeeded": True,
        "all_modules_installed": True,
        "complete_fixed_results": True,
        "relocated_post": True,
        "recovery": "fitted_state_readback" if surrogate else "optimizer_and_stream_resume",
    }


def _record_attempt(summary, identity, attempt):
    previous = summary.get(identity, {})
    history = list(previous.get("attempts", []))
    if previous and not history:
        # 兼容只含最新记录的旧汇总，但不抹掉它对应的原报告/日志。
        history.append({key: value for key, value in previous.items() if key != "attempts"})
    if history and history[-1].get("attempt_id") == attempt["attempt_id"]:
        history[-1] = dict(attempt)
    else:
        history.append(dict(attempt))
    summary[identity] = {**attempt, "attempts": history}


def run(root, *, case_id=None):
    """顺序调用八项或单项重试；调用方必须已经完成安装并持有现有预算记录。"""
    root = Path(root).resolve()
    if not (root / "budget/budget.json").is_file():
        raise FileNotFoundError("缺少本轮既有 budget/budget.json；禁止为安装重建预算")
    environment_root = root / "installed"
    interpreter = environment_root / "bin/python"
    if not interpreter.is_file():
        raise FileNotFoundError(f"缺少已安装独立环境解释器: {interpreter}")
    selected = [item for item in CASES if case_id is None or item[0] == case_id]
    if not selected:
        raise ValueError(f"未知安装案例: {case_id}")
    preparation = json.loads((root / "evidence/preparation.json").read_text())
    for _, case, _ in selected:
        path = preparation[case]
        if not isinstance(path, str) or not Path(path).is_file():
            raise ValueError(f"准备入口须为真实manifest字符串: {case}")
    ledger = BudgetLedger(root / "budget")
    ledger.snapshot()  # 只读核账本版本/上限，禁止把旧账当不存在。
    summary_path = root / "evidence/installed.json"
    summary = json.loads(summary_path.read_text()) if summary_path.exists() else {}
    runtime = root / "installed-validation"
    runtime.mkdir(parents=True, exist_ok=True)
    harness = runtime / ("harness-" + str(time.time_ns()))
    harness.mkdir()
    script = Path(__file__).with_name("installed_replay.py")
    helper = Path(__file__).parents[1] / "classic_networks/installed_replay.py"
    if digest(helper) != HELPER_SHA256:
        raise ValueError("待复制classic helper与安装脚本锁定修订不一致")
    shutil.copy2(script, harness / "installed_replay.py")
    shutil.copy2(helper, harness / "classic_installed_replay.py")
    sources = {
        name: digest(harness / name)
        for name in ("installed_replay.py", "classic_installed_replay.py")
    }
    (root / "cache").mkdir(exist_ok=True)
    (root / "tmp").mkdir(exist_ok=True)
    environment = {
        **os.environ,  # 尤其保留父进程配置的 DYLD_LIBRARY_PATH 原值。
        "PYTHONPATH": "",
        "PYTHONDONTWRITEBYTECODE": "1",
        "UV_CACHE_DIR": str(root / "cache"),
        "TMPDIR": str(root / "tmp"),
        "OPENBLAS_NUM_THREADS": "2",
        "OMP_NUM_THREADS": "2",
    }
    for identity, case, budget in selected:
        attempt_id = str(time.time_ns())
        destination = runtime / (identity + "-" + attempt_id)
        # case ID 含点号，不能用 with_suffix 吞掉案例名与重试身份。
        log = destination.parent / (destination.name + ".log")
        report_path = destination / "report.json"
        attempt = {
            "attempt_id": attempt_id,
            "status": "running",
            "report": str(report_path),
            "log": str(log),
            "budget_identity": budget,
            "started_at": time.time(),
            "harness": str(harness),
            "harness_sha256": sources,
        }
        process = None
        worker = {"process": None}
        started = time.monotonic()
        _record_attempt(summary, identity, attempt)
        write(summary_path, summary)
        try:
            with ledger.measure(
                budget,
                "installed-" + identity,
                training=True,
                on_timeout=lambda worker=worker: stop(worker["process"]),
            ):
                remaining = ledger.remaining(budget)
                if remaining <= 60:
                    raise BudgetExceeded(f"{budget} 剩余不足60秒，无法为Task清理留出余量")
                command = [
                    "uv",
                    "run",
                    "--no-project",
                    "--no-sync",
                    "--python",
                    str(interpreter),
                    str(harness / "installed_replay.py"),
                    "--root",
                    str(destination),
                    "--environment",
                    str(environment_root),
                    "--case-id",
                    identity,
                    "--preparation",
                    preparation[case],
                    "--seconds",
                    str(remaining - 45),
                    "--budget-identity",
                    budget,
                    "--device",
                    "cpu",
                    "--with-task",
                ]
                attempt["command"] = command
                with log.open("w", encoding="utf-8") as stream:
                    process = subprocess.Popen(
                        command,
                        cwd=harness,
                        env=environment,
                        stdout=stream,
                        stderr=subprocess.STDOUT,
                        start_new_session=True,
                    )
                    worker["process"] = process
                    try:
                        code = process.wait(timeout=max(1, ledger.remaining(budget) - 20))
                    finally:
                        stop(process)
                attempt["returncode"] = code
                if code:
                    raise RuntimeError(f"安装重放退出码 {code}: {log}")
                report = json.loads(report_path.read_text())
                attempt["verification"] = assert_result(
                    report,
                    identity=identity,
                    budget=budget,
                    environment=environment_root,
                )
                attempt["replay_elapsed_seconds"] = report["elapsed_seconds"]
                attempt["status"] = "passed"
        except BaseException as error:
            attempt.update(status="failed", error=repr(error))
            try:
                stop(process)
            except Exception as cleanup_error:  # noqa: BLE001 - 原始失败与清理失败分别保留
                attempt["cleanup_error"] = repr(cleanup_error)
            if report_path.is_file():
                try:
                    child_report = json.loads(report_path.read_text())
                    attempt["child_status"] = child_report.get("status")
                    attempt["child_error"] = child_report.get("error")
                except (ValueError, OSError) as parse_error:
                    attempt["report_read_error"] = repr(parse_error)
            raise
        finally:
            attempt["elapsed_seconds"] = time.monotonic() - started
            _record_attempt(summary, identity, attempt)
            write(summary_path, summary)
        print(
            json.dumps(
                {
                    "case_id": identity,
                    "status": attempt["status"],
                    "report": str(report_path),
                    "budget_identity": budget,
                },
                ensure_ascii=False,
            ),
            flush=True,
        )
    return summary


def main():
    """显式主控调用入口；导入本模块不会训练、安装或初始化新账本。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument(
        "--case-id", choices=[item[0] for item in CASES], help="仅重试此项，其他结果保持原样"
    )
    args = parser.parse_args()
    run(args.root, case_id=args.case_id)


if __name__ == "__main__":
    main()
