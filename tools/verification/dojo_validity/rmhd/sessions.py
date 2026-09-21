"""正式新 CLI 会话与可信父进程采集；不复用主会话或 Neumann 初始化流程。"""

import json
import shutil
import subprocess
import threading
import time
import tomllib
import uuid
from pathlib import Path

from ..cli import CODEX, DISABLED, toml
from ..io import digest, inside, read_json, write_json
from .isolation import clean_environment, policy
from .network import PublicProxy


def prompt(protocol, number):
    """共同任务只含本组材料；第一轮正式执行包括全部安装、编写和准备成本。"""
    root = protocol["experiment_root"]
    task = f"""你在进行 JOREK RMHD 预测研究。工作根为 {protocol["session_workspace_root"]}，
本次实验全部工作和产物保存在 {root}。只能访问本组根和登记的只读系统运行时；
不能访问其他工作根、宿主资料、本机服务或从公网获取隐藏轨迹真值。
先读本实验 SUBMISSION.md、protocol.json、baseline/scientific.json 和 data/manifest.json。
目标：完整未来40帧预测 P95<=50ms，精度第一，分别降低编码时间和token。
原始 train/validation 数据包尚未处理。模型源码和初始化在 baseline/。
现有公共科学包仅为 installation/ 下的安装材料，你需要自行建立 environment 并安装。
解释器系统前提为 {protocol["python_executable"]}，通用安装工具 tools/uv。
全部 Python 命令使用 tools/uv run --no-project --no-sync --python environment/bin/python。
安装、数据准备、训练和评价分别经本实验 activity.py 指定相应阶段执行；脚本编写、
搜索、分析和调试计编码。所有失败尝试保留。科学进程前台执行，结束前等待完成，
不留后台训练或定时进程。读完规则就实际编码、执行并交付，不只给计划。
本次是 round-{number:02d}。"""
    if number == 0:
        task += "\n你必须自行编写原始数据读取、校验、统计、窗口构造、训练和评价流程，并完整执行固定500epoch baseline。不能改动科学设置或初始权重。提交 round-00/submission/ 及 baseline-evidence.json。"
    else:
        task += f"\n基于本组已有工作完成第{number}次实质优化。架构、训练预算和尝试次数自由，记录全部成本。只用训练和开发验证选择候选。提交 round-{number:02d}/submission/；结束后等待下一轮指令。"
    if protocol["group"] == "dojo":
        task += "\n你可以使用 Dojo。入口 dojo-resources/DOJO_AGENT_GUIDE.md，skill 为 dojo-resources/.agents/skills/dojo-research/SKILL.md。选择使用前，先阅读能力分支教程与现行API；按需使用单工具、已有代码或完整案例接入。兼容能力优先复用，不兼容允许自写并记录原因。是否使用由研究需要决定。初次学习和检索计编码成本；dojo-resources/wheels/ 是同版安装包。"
    return task


def cli_command(protocol, answer, body, environment, session=None):
    """外层 Seatbelt 已生效；CLI 不再叠加另一个沙箱，禁宿主规则与个人能力。"""
    host = tomllib.loads((Path.home() / ".codex/config.toml").read_text())
    provider = host.get("model_provider", "openai")
    settings = {
        "model": protocol["model"],
        "model_reasoning_effort": protocol["reasoning"],
        "model_provider": provider,
        "approval_policy": "never",
        "project_doc_max_bytes": 0,
        "web_search": "live",
        "features.network_proxy": False,
        "log_dir": str(Path(protocol["experiment_root"]) / "agent-state/logs"),
        "sqlite_home": str(Path(protocol["experiment_root"]) / "agent-state"),
        "shell_environment_policy.inherit": "none",
        "shell_environment_policy.set": environment,
    }
    if provider in host.get("model_providers", {}):
        settings[f"model_providers.{provider}"] = host["model_providers"][provider]
    args = [
        "/usr/bin/sandbox-exec",
        "-p",
        body,
        str(CODEX),
        "exec",
        "--ignore-user-config",
        "--ignore-rules",
        "--dangerously-bypass-approvals-and-sandbox",
        "--skip-git-repo-check",
        "--json",
        "-C",
        protocol["session_workspace_root"],
    ]
    for feature in DISABLED:
        args += ["--disable", feature]
    args += ["--enable", "skip_host_skill_discovery"]
    for key, value in settings.items():
        args += ["-c", f"{key}={toml(value)}"]
    if session:
        args += ["resume", session]
    return args + ["-o", str(answer), "-"]


def invoke(protocol, message, evidence, session=None, session_record=None):
    """原始 stream、原始 rollout 增量、进程观察由父进程写到主控目录。"""
    evidence = Path(evidence)
    evidence.mkdir(parents=True, exist_ok=False)
    experiment = Path(protocol["experiment_root"])
    state = experiment / "agent-state"
    auth = state / "auth.json"
    if not auth.exists():
        shutil.copyfile(Path.home() / ".codex/auth.json", auth)
        auth.chmod(0o600)
    (evidence / "prompt.txt").write_text(message)
    answer = experiment / "evidence" / f"answer-{uuid.uuid4()}.txt"
    started = time.monotonic()
    stop = threading.Event()
    with PublicProxy(evidence / "network.jsonl") as proxy:
        env = clean_environment(
            experiment,
            {
                "HTTPS_PROXY": f"http://127.0.0.1:{proxy.port}",
                "HTTP_PROXY": f"http://127.0.0.1:{proxy.port}",
                "https_proxy": f"http://127.0.0.1:{proxy.port}",
                "http_proxy": f"http://127.0.0.1:{proxy.port}",
                "NO_PROXY": "",
                "no_proxy": "",
            },
        )
        body = policy(
            [protocol["session_workspace_root"]],
            [*protocol["runtime_readonly_roots"], CODEX, CODEX.with_name("codex-code-mode-host")],
            proxy_port=proxy.port,
        )
        (evidence / "policy.sbpl").write_text(body)
        with (
            (evidence / "stderr.log").open("w") as error,
            (evidence / "events.jsonl").open("w") as log,
        ):
            process = subprocess.Popen(
                cli_command(protocol, answer, body, env, session),
                cwd=protocol["session_workspace_root"],
                env=env,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=error,
                text=True,
                start_new_session=True,
            )

            def capture():
                offsets = {}
                while not stop.wait(0.25):
                    # 定时记录本次进程组；其他用户进程不写入实验日志。
                    ps = subprocess.run(
                        ["/bin/ps", "-axo", "pid=,ppid=,pgid=,etime=,command="],
                        capture_output=True,
                        text=True,
                        check=False,
                    )
                    selected = [
                        line
                        for line in ps.stdout.splitlines()
                        if len(line.split(None, 4)) == 5
                        and line.split(None, 4)[2] == str(process.pid)
                    ]
                    # 首条 CLI argv 含认证路由配置，因此仅保留其身份，子命令保留实际活动。
                    selected = [
                        line if int(line.split()[0]) != process.pid else f"{process.pid} CLI parent"
                        for line in selected
                    ]
                    with (evidence / "process-observations.jsonl").open("a") as stream:
                        stream.write(
                            json.dumps({"time": time.monotonic(), "processes": selected}) + "\n"
                        )
                    for path in (state / "sessions").rglob("*.jsonl"):
                        if path.is_symlink() or not path.resolve().is_relative_to(state.resolve()):
                            continue
                        key = path.name
                        offset = offsets.get(key, 0)
                        with path.open("rb") as source:
                            if path.stat().st_size < offset:
                                (evidence / "rollout-tamper.txt").write_text(
                                    "会话文件被截短，证据不完整"
                                )
                                continue
                            source.seek(offset)
                            data = source.read()
                        if data:
                            target = evidence / "raw-rollouts" / key
                            target.parent.mkdir(exist_ok=True)
                            with target.open("ab") as stream:
                                stream.write(data)
                            offsets[key] = offset + len(data)

            thread = threading.Thread(target=capture, daemon=True)
            thread.start()
            process.stdin.write(message)
            process.stdin.close()
            for line in process.stdout:
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    event = {"type": "unparsed", "text": line}
                log.write(json.dumps({"received": time.monotonic(), "event": event}) + "\n")
                log.flush()
                if event.get("type") == "thread.started":
                    sid = event["thread_id"]
                    if session is not None and sid != session:
                        raise RuntimeError("续接返回不同会话ID")
                    session = sid
                    write_json(evidence / "session.json", {"session_id": session})
                    if session_record is not None:
                        write_json(session_record, {"session_id": session})
                if event.get("type") in {
                    "thread.started",
                    "turn.completed",
                    "turn.failed",
                    "error",
                }:
                    print(json.dumps(event), flush=True)
            returncode = process.wait()
            # 留一次增量抓取机会；可信 stream 不依赖这一补充副本。
            time.sleep(0.3)
            stop.set()
            thread.join(timeout=5)
    result = {
        "session_id": session,
        "returncode": returncode,
        "started": started,
        "ended": time.monotonic(),
    }
    write_json(evidence / "process.json", result)
    if answer.exists():
        shutil.copyfile(answer, evidence / "answer.txt")
    return result


class CliDriver:
    """一组一个 session ID，任何失败继续原 session，调度不隐式换模型或重开。"""

    def __init__(self, comparison):
        self.root = Path(comparison)

    def trusted_protocol(self, group, location):
        """权限只来自主控配置；组内协议只作经初始摘要核验的科学说明。"""
        config = read_json(self.root / "comparison-protocol.json")
        if group not in {"plain", "dojo"}:
            raise ValueError("组非法")
        experiment = Path(config["experiments"][group])
        if Path(location) != experiment or experiment.resolve() != experiment:
            raise ValueError("实验路径与主控登记不一致")
        workspace = experiment.parent
        if workspace.name != f"jorek-rmhd-{group}":
            raise ValueError("会话工作根不是登记的组级目录")
        frozen = read_json(self.root / f"evidence/{group}-initial-materials.json")
        path = experiment / "protocol.json"
        if path.is_symlink() or digest(path) != frozen["protocol.json"]:
            raise ValueError("组内协议已修改，不能用于继续会话")
        protocol = read_json(path)
        protocol.update(
            group=group,
            experiment_id=experiment.name,
            experiment_root=str(experiment),
            session_workspace_root=str(workspace),
            runtime_readonly_roots=config["runtime_readonly_roots"],
            model=config["model"],
            reasoning=config["reasoning"],
        )
        return protocol

    def verify_startup(self, config):
        """重核主控冻结材料与本次真实预检；不能仅信组内布尔值。"""
        if not read_json(self.root / "evidence/worker-check.json").get("passed"):
            raise ValueError("隔离预测、同值复放或50ms门槛未通过")
        if not read_json(self.root / "evidence/cli-capability.json").get("passed"):
            raise ValueError("CLI工具、同会话续接、原始usage预检未通过")
        for group, location in config["experiments"].items():
            experiment = Path(location)
            frozen = read_json(self.root / f"evidence/{group}-initial-materials.json")
            for name, checksum in frozen.items():
                if digest(inside(experiment, name)) != checksum:
                    raise ValueError("正式启动前初始材料变化")
            proof = read_json(self.root / f"evidence/{group}-isolation.json")
            if (
                not proof["passed"]
                or not proof["mps_probed"]
                or not all(x["passed"] for x in proof["checks"])
            ):
                raise ValueError("整进程或 MPS 隔离未通过")

    def call(self, group, location, name, message):
        """主控目录保留每次尝试，失败不会覆盖上一条证据。"""
        protocol = self.trusted_protocol(group, location)
        session_file = self.root / "sessions" / f"{group}.json"
        session = read_json(session_file)["session_id"] if session_file.exists() else None
        evidence = self.root / "evidence/sessions" / group / name / str(uuid.uuid4())
        result = invoke(protocol, message, evidence, session, session_file)
        if result["session_id"]:
            write_json(session_file, {"session_id": result["session_id"]})
        if result["returncode"] or not result["session_id"]:
            raise RuntimeError(f"{group} CLI 未完成，证据: {evidence}")
        return evidence

    def round(self, group, number, location):
        """执行实际 round00 或优化轮；主控只核验协议，不代写研究代码。"""
        protocol = self.trusted_protocol(group, location)
        message = prompt(protocol, number)
        while True:
            self.call(group, location, f"round-{number:02d}", message)
            try:
                return self.check_round(group, number, location, protocol)
            except (ValueError, FileNotFoundError, KeyError) as error:
                message = f"本轮提交未通过协议核查：{error}。这仍是 round-{number:02d}，不进入下一轮。请在原会话修复本组提交并实跑验证，保留失败成本。不改变固定 baseline 设置；只使用训练/验证材料。"

    def check_round(self, group, number, location, protocol):
        """核查当前轮，仅开发验证失败可以回送本组修复。"""
        source = Path(location) / f"round-{number:02d}/submission"
        if number == 0:
            from .verification import verify_round_zero

            verify_round_zero(self.root, group, source)
        from .evaluate import evaluate_candidate

        splits = read_json(self.root / "private-split.json")["splits"]
        aliases = read_json(Path(location) / "data/manifest.json")["validation"]
        samples = [s | {"id": a["id"]} for s, a in zip(splits["validation"], aliases, strict=True)]
        validation_output = (
            self.root / "validation" / group / f"round-{number:02d}" / str(uuid.uuid4())
        )
        result = evaluate_candidate(
            source,
            Path(location) / "environment",
            protocol["runtime_readonly_roots"],
            samples,
            validation_output,
        )
        write_json(validation_output / "result.json", result)
        # 开发验证反馈可以进入本组；隐藏测试从不使用此调用路径。
        write_json(Path(location) / f"round-{number:02d}/validation.json", result)
        if result["status"] != "evaluated":
            raise ValueError("候选未通过开发验证接口；须在同轮同会话修复")
        return source

    def select_final(self, group, location):
        """最终只允许基于验证结果选择历史候选。"""
        self.call(
            group,
            location,
            "final-selection",
            "五轮已完成。仅根据本组验证结果，从已提交的 round-00..05 中选择一个最终候选。写 final/selection.json，字段 round 和 validation_reason。不得改动候选，不新增训练或优化，不使用隐藏测试。",
        )
        return read_json(Path(location) / "final/selection.json")
