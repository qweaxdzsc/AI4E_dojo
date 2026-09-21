"""真实 CLI 的五轮执行、冻结推理重放与供应商请求留档。"""

import json
import shutil
import subprocess
import time
import uuid
from pathlib import Path

import numpy as np

from .cli import invoke, seatbelt
from .io import read_json, write_json
from .metrics import evaluate
from .runner import finalize, run, summarize


def delivery_prompt(protocol, number):
    """明确交付格式与测量入口，不限制研究方法或计算预算。"""
    experiment = protocol["experiment_id"]
    return f"""
本轮编号 {number:02d}。已经完成共同 baseline round-00，不必重新跑。请自主完成本轮实质改进和实际运行，勿只提出计划。
本实验的 environment/bin/ 已由主控补齐独立 uv、rg 可执行文件（准备问题已修复），可以继续使用相同会话和已有工作。
本实验已有独立 Python：{experiment}/environment/bin/python；所有 Python 命令使用
uv run --no-project --no-sync --cache-dir {experiment}/cache/uv --python {experiment}/environment/bin/python python ...
测量约定：所有训练、推理评价、安装和数据准备命令，使用本实验 activity.py 包裹：
... python {experiment}/activity.py training -- <实际命令及参数>（其他阶段 evaluation/environment_setup/data_preparation）。
每次训练含失败重试都单独包裹。编码读写搜索可直接执行，后台训练时仍可编码；不要删改计时器和证据。
日志与训练诊断请保存更新数、参数量/层数、checkpoint字节、设备/线程、峰值内存、损失定义和权重，未测字段保留 null。
只用自己的 baseline 及 workspace；不读取 agent-state 内凭证、预检或其他会话记录。
模型与 checkpoint 必须能由冻结源码独立重建。提交的 source 目录必须自包含并包含 infer.py，命令约定：
python source/infer.py --checkpoint <冻结权重> --config <冻结配置文件> --inputs <输入NPZ> --output <新的预测目录>
输入NPZ包含 nu/test_nu（十个参数）、x、t、basis、basis_d1、basis_d2，不提供真值。
推理必须仅依靠提交源码、checkpoint、配置和上述输入；输出 test-00000.npy 至 test-00009.npy（形状128x128，时间在前）和 predictions.json。
predictions.json={{"samples":[{{"id":"test-00000","path":"test-00000.npy","sha256":"实际文件SHA256"}},...]}}。
使用的数值定义与 baseline 的差异须逐项记录。禁止直接读取测试真值充当模型预测；这属于评价有效性要求。
本轮结束写 {experiment}/workspace/submission-round-{number:02d}.json：
{{"source":"workspace/候选源码目录","config":"workspace/配置文件","checkpoint":"workspace/权重文件","predictions":"workspace/预测目录","training":"workspace/训练诊断JSON","summary":"workspace/本轮总结MD","diff":"workspace/本轮代码差异文件"}}。
所有路径相对于实验目录，文件必须真实存在，不使用软链接。不要提前开始下一轮。
第5轮同时在 {experiment}/workspace/final-choice.json 写 {{"round":1到5中最终选择的轮次,"reason":"理由"}}。
如果使用了框架，在总结中列明实际读取的入口、文档和采用组件；如果未使用也明确记录。
"""


def rollout_path(protocol, session):
    """仅定位本组专用状态中的正式会话。"""
    paths = list(
        (Path(protocol["experiment_root"]) / "agent-state/sessions").rglob(f"*{session}.jsonl")
    )
    if len(paths) != 1:
        raise ValueError("正式会话原始记录缺失或不唯一")
    return paths[0]


def usage_records(protocol, session, target):
    """保留真实 request ID 和原始 usage，不把 cached/reasoning 子计数重复加总。"""
    source = rollout_path(protocol, session)
    shutil.copyfile(source, target / "rollout.jsonl")
    records = []
    for line in source.read_text().splitlines():
        event = json.loads(line)
        if event["type"] == "token_usage_record":
            p = event["payload"]
            u = p["usage"]
            records.append(
                {
                    "request_id": p["response_id"],
                    "phase": "mixed",
                    "input_tokens": u["input_tokens"],
                    "output_tokens": u["output_tokens"],
                    "cache_read_tokens": u.get("cached_input_tokens"),
                    "cache_write_tokens": u.get("cache_write_input_tokens"),
                    "tool_calls": None,
                    "retry_count": None,
                    "input_includes_cache": True,
                    "output_includes_reasoning": True,
                    "raw": p,
                    "timestamp": event["timestamp"],
                }
            )
    return records


class CliRunner:
    """同组复用一个已创建的全新 CLI 会话，状态在本组根内。"""

    simulation = False

    def preflight(self, protocol):
        """仅消费主控已完成的整进程隔离证据。"""
        proof = read_json(
            Path(protocol["experiment_root"]) / "evidence/whole-process-isolation.json"
        )
        if not proof["all_tools_isolated"]:
            raise ValueError("隔离预检未通过")
        activity = Path(protocol["experiment_root"]) / "activity.py"
        if not activity.exists():
            shutil.copyfile(Path(__file__).with_name("activity.py"), activity)
        return proof

    def create_session(self, protocol):
        """取本轮正式初始化返回的真实会话 ID，不冒充生成 UUID。"""
        target = Path(protocol["experiment_root"]) / "evidence/formal-initialization"
        if not target.exists():
            invoke(
                protocol,
                f"这是全新实验会话。工作根为 {protocol['session_workspace_root']}。"
                "只执行 pwd 确认工作根并等待第一轮指令；不读取实验材料、历史会话或凭证。",
                target,
            )
        return read_json(target / "session.json")["session_id"]

    def turn(self, protocol, session_id, round_number, prompt, attempt):
        """执行一轮，保存全部请求及测量事件，失败由上层保留。"""
        root = Path(protocol["experiment_root"])
        result = invoke(
            protocol, prompt + delivery_prompt(protocol, round_number), attempt / "cli", session_id
        )
        if result["returncode"]:
            raise RuntimeError(f"CLI退出码 {result['returncode']}，详见 {attempt}/cli")
        usage = usage_records(protocol, session_id, attempt)
        # 每轮只取新增请求，旧轮次请求已落在各自账本。
        prior = set()
        for path in root.glob("round-*/attempts/*/response.json"):
            prior.update(r["request_id"] for r in read_json(path)["usage"])
        usage = [r for r in usage if r["request_id"] not in prior]
        activities = [read_json(p) for p in root.glob("evidence/activities/*/completed.json")]
        events = [
            r for r in activities if result["started"] <= r["start"] <= r["end"] <= result["ended"]
        ]
        submission = read_json(root / f"workspace/submission-round-{round_number:02d}.json")
        return {**result, "usage": usage, "events": events, "submission": submission}


def evaluator(protocol, truth):
    """在只读候选/运行库和可写输出范围内重放推理，真值不进入子进程。"""
    experiment = Path(protocol["experiment_root"])

    def replay(frozen):
        result = experiment / "evidence/evaluations" / str(uuid.uuid4())
        result.mkdir(parents=True)
        with np.load(experiment / "baseline/dataset.npz") as data:
            np.savez(
                result / "inputs.npz",
                nu=data["test_nu"],
                **{k: data[k] for k in ("test_nu", "x", "t", "basis", "basis_d1", "basis_d2")},
            )
        policy = seatbelt(protocol)
        grant = f"(allow file-read* file-write* file-map-executable (subpath {json.dumps(protocol['session_workspace_root'])}))"
        readonly = [str(frozen.resolve()), str(experiment / "environment")]
        replacement = "\n".join(
            f"(allow file-read* file-map-executable (subpath {json.dumps(p)}))" for p in readonly
        )
        replacement += f"\n(allow file-read* file-write* (subpath {json.dumps(str(result))}))"
        policy = policy.replace(grant, replacement)
        command = [
            str(experiment / "environment/bin/python"),
            str(frozen / "source/infer.py"),
            "--checkpoint",
            str(frozen / "checkpoint"),
            "--config",
            str(frozen / "config"),
            "--inputs",
            str(result / "inputs.npz"),
            "--output",
            str(result / "predictions"),
        ]
        started = time.monotonic()
        with (result / "stdout.log").open("w") as log:
            child = subprocess.run(
                ["/usr/bin/sandbox-exec", "-p", policy, *command],
                cwd=result,
                stdout=log,
                stderr=subprocess.STDOUT,
                check=False,
                env={
                    "PATH": "/usr/bin:/bin",
                    "TMPDIR": str(result),
                    "PYTHONDONTWRITEBYTECODE": "1",
                    "OMP_NUM_THREADS": "1",
                },
            )
        metrics = None
        if child.returncode == 0:
            metrics = evaluate(
                result / "predictions/predictions.json", truth, result / "metrics.json"
            )
        write_json(
            result / "execution.json",
            {
                "command": command,
                "exit_code": child.returncode,
                "start": started,
                "end": time.monotonic(),
                "includes_fp64_evaluation": child.returncode == 0,
            },
        )
        if child.returncode:
            raise RuntimeError(f"冻结推理失败: {result}/stdout.log")
        return metrics

    return replay


def main():
    """串行运行两组五轮，保留已有完成轮次，不设置预算上限。"""
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--comparison", type=Path, required=True)
    args = parser.parse_args()
    config = read_json(args.comparison / "comparison-protocol.json")
    for location in config["experiments"].values():
        root = Path(location)
        protocol = read_json(root / "protocol.json")
        shutil.copyfile(Path(__file__).with_name("activity.py"), root / "activity.py")
        replay = evaluator(protocol, args.comparison / "baseline/truth/manifest.json")
        run(root, CliRunner(), replay)
        selection = read_json(root / "workspace/final-choice.json")
        finalize(root, selection["round"], replay)
        summarize(args.comparison)
    from .finish import seal

    seal(args.comparison)


if __name__ == "__main__":
    main()
