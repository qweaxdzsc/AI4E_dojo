"""正式 Codex CLI 会话：显式权限、禁用宿主资料注入、逐事件原始留档。"""

import json
import os
import shutil
import subprocess
import time
import tomllib
from pathlib import Path

from .io import read_json, write_json

CODEX = Path("/Applications/ChatGPT.app/Contents/Resources/codex")
DISABLED = (
    "apps",
    "browser_use",
    "browser_use_external",
    "browser_use_full_cdp_access",
    "computer_use",
    "in_app_browser",
    "hooks",
    "memories",
    "multi_agent",
    "multi_agent_v2",
    "plugins",
    "remote_plugin",
    "shell_snapshot",
    "skill_search",
    "skill_mcp_dependency_install",
    "workspace_dependencies",
)


def seatbelt(protocol):
    """由主控代码生成整进程策略；不信任实验目录内可写的策略副本。"""
    policies = Path(__file__).with_name("policies")
    body = "\n".join(
        (policies / f"{name}.sbpl").read_text() for name in ("base", "platform", "network")
    )
    body += "\n(allow file-read* file-map-executable "
    for root in (
        "/bin",
        "/sbin",
        "/usr/bin",
        "/usr/sbin",
        "/Applications/ChatGPT.app/Contents/Resources",
        "/opt/homebrew",
    ):
        body += f"(subpath {json.dumps(root)}) "
    body += ")\n"
    body += f"(allow file-read* file-write* file-map-executable (subpath {json.dumps(protocol['session_workspace_root'])}))\n"
    body += '(allow network-outbound) (deny network-outbound (remote ip "localhost:*"))\n'
    return body


def toml(value):
    """编码 CLI 的 TOML 内联值，不使用 shell 插值。"""
    if isinstance(value, dict):
        return "{" + ",".join(f"{json.dumps(k)}={toml(v)}" for k, v in value.items()) + "}"
    if isinstance(value, list):
        return "[" + ",".join(toml(v) for v in value) + "]"
    return json.dumps(value)


def command(protocol, output, session=None):
    """仅继承认证路由和当前模型设置；不读取用户的插件、规则或记忆。"""
    user = tomllib.loads((Path.home() / ".codex/config.toml").read_text())
    root = protocol["session_workspace_root"]
    experiment = Path(protocol["experiment_root"])
    filesystem = {":minimal": "read", root: "write"}
    for path in protocol.get("runtime_readonly_roots", []) + protocol.get(
        "shared_readonly_roots", []
    ):
        filesystem[path] = "read"
    settings = {
        "model": protocol.get("model") or user["model"],
        "model_reasoning_effort": protocol.get("reasoning")
        or user.get("model_reasoning_effort", "high"),
        "model_provider": user.get("model_provider", "openai"),
        "approval_policy": "never",
        "default_permissions": "neumann-isolated",
        "permissions.neumann-isolated.filesystem": filesystem,
        "permissions.neumann-isolated.network": {"enabled": True},
        "features.network_proxy": False,
        "project_doc_max_bytes": 0,
        "skills.config": [
            {"path": str(p), "enabled": False}
            for base in (Path.home() / ".codex/skills", Path.home() / ".agents/skills")
            for p in sorted(set(base.rglob("SKILL.md")) | set(base.glob("*/SKILL.md")))
        ]
        + [
            {
                "path": str(experiment / "agent-state/skills/.system" / name / "SKILL.md"),
                "enabled": False,
            }
            for name in (
                "imagegen",
                "openai-docs",
                "plugin-creator",
                "skill-creator",
                "skill-installer",
            )
        ],
        "web_search": "live",
        "log_dir": str(experiment / "agent-state/logs"),
        "sqlite_home": str(experiment / "agent-state"),
        "shell_environment_policy.inherit": "none",
        "shell_environment_policy.set": {
            "PATH": f"{experiment}/environment/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin",
            "TMPDIR": str(experiment / "tmp"),
            "XDG_CACHE_HOME": str(experiment / "cache"),
            "UV_CACHE_DIR": str(experiment / "cache/uv"),
            "PYTHONDONTWRITEBYTECODE": "1",
            "OMP_NUM_THREADS": "1",
            "MKL_NUM_THREADS": "1",
        },
    }
    provider = settings["model_provider"]
    if provider in user.get("model_providers", {}):
        settings[f"model_providers.{provider}"] = user["model_providers"][provider]
    args = [
        "/usr/bin/sandbox-exec",
        "-p",
        seatbelt(protocol),
        str(CODEX),
        "exec",
        "--ignore-user-config",
        "--ignore-rules",
        "--dangerously-bypass-approvals-and-sandbox",
        "--skip-git-repo-check",
        "--json",
        "-C",
        root,
    ]
    for feature in DISABLED:
        args += ["--disable", feature]
    args += ["--enable", "skip_host_skill_discovery"]
    for key, value in settings.items():
        args += ["-c", f"{key}={toml(value)}"]
    if session:
        args += ["resume", session]
    args += ["-o", str(output), "-"]
    return args


def invoke(protocol, prompt, output, session=None):
    """流式保存 CLI 事件和接收时刻，第一条 thread.started 即持久化 ID。"""
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    (output / "prompt.txt").write_text(prompt)
    started = time.monotonic()
    with (output / "stderr.log").open("w") as err, (output / "events.jsonl").open("w") as log:
        environment = os.environ.copy()
        environment["NO_PROXY"] = "*"
        environment["no_proxy"] = "*"
        # CODEX_HOME 在这里保留其官方含义：该子进程专用的 Codex 状态目录。
        # 不修改宿主变量或用户配置，不复用已有会话和记忆。
        state = Path(protocol["experiment_root"]) / "agent-state"
        state.mkdir(exist_ok=True)
        auth = state / "auth.json"
        if not auth.exists():
            shutil.copyfile(Path.home() / ".codex/auth.json", auth)
            auth.chmod(0o600)
        environment["CODEX_HOME"] = str(state)
        environment["TMPDIR"] = str(Path(protocol["experiment_root"]) / "tmp")
        process = subprocess.Popen(
            command(protocol, output / "answer.txt", session),
            cwd=protocol["session_workspace_root"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=err,
            text=True,
            env=environment,
        )
        process.stdin.write(prompt)
        process.stdin.close()
        for line in process.stdout:
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                event = {"type": "unparsed", "text": line}
            log.write(json.dumps({"received": time.monotonic(), "event": event}) + "\n")
            log.flush()
            if event.get("type") == "thread.started":
                session = event["thread_id"]
                write_json(output / "session.json", {"session_id": session})
            if event.get("type") in ("thread.started", "turn.completed", "turn.failed", "error"):
                print(json.dumps(event), flush=True)
        returncode = process.wait()
    result = {
        "session_id": session,
        "started": started,
        "ended": time.monotonic(),
        "returncode": returncode,
    }
    write_json(output / "process.json", result)
    return result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--experiment", type=Path, required=True)
    parser.add_argument("--prompt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--session")
    args = parser.parse_args()
    invoke(
        read_json(args.experiment / "protocol.json"),
        args.prompt.read_text(),
        args.output,
        args.session,
    )
