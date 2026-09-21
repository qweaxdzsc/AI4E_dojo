"""Codex 本机命令沙箱探针；命令通过不等于整个会话已隔离。"""

import json
import subprocess
from pathlib import Path

from .io import write_json


class IsolationUnavailable(RuntimeError):
    """尚无覆盖全部会话工具和上下文的隔离执行器。"""


def sandbox_command(codex, workspace, command, readonly=()):
    """创建仅本组可写的 Codex 权限配置；默认读权限不扩大到项目父目录。"""
    filesystem = {":minimal": "read", str(Path(workspace).resolve()): "write"}
    for path in readonly:
        filesystem[str(Path(path).resolve())] = "read"
    # TOML inline table 与命令 argv 分开；从不经过 shell 插值。
    table = "{" + ",".join(f"{json.dumps(k)}={json.dumps(v)}" for k, v in filesystem.items()) + "}"
    return [
        str(codex),
        "sandbox",
        "-C",
        str(workspace),
        "-P",
        "neumann-isolated",
        "-c",
        f"permissions.neumann-isolated.filesystem={table}",
        "-c",
        "permissions.neumann-isolated.network.enabled=true",
        "--",
        *command,
    ]


def probe_commands(codex, workspace, forbidden, output, readonly=()):
    """以无敏感内容的探针核对本组、父目录、跨组及共享只读行为。"""
    workspace = Path(workspace).resolve()
    marker = workspace / ".isolation-probe"
    checks = {}

    def check(name, command, expected_success):
        result = subprocess.run(
            sandbox_command(codex, workspace, command, readonly),
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        checks[name] = {
            "passed": (result.returncode == 0)
            if expected_success
            else (
                result.returncode != 0
                and any(
                    message in result.stderr
                    for message in ("Operation not permitted", "Permission denied")
                )
            ),
            "exit_code": result.returncode,
            "stderr": result.stderr[-2000:],
        }

    try:
        check("own_write", ["/usr/bin/touch", str(marker)], True)
        check("own_read", ["/bin/cat", str(marker)], True)
        check("parent_listing_denied", ["/bin/ls", str(workspace.parent)], False)
        for index, root in enumerate(forbidden):
            root = Path(root)
            if not root.is_dir():
                raise ValueError("拒绝探针目标必须存在，不能把 ENOENT 当作隔离")
            sentinel = root / f".probe-from-{workspace.name}"
            sentinel.write_text("isolation sentinel\n")
            link = workspace / f".probe-link-{index}"
            try:
                link.symlink_to(sentinel)
                check(f"outside_read_{index}", ["/bin/cat", str(sentinel)], False)
                check(f"outside_write_{index}", ["/usr/bin/touch", str(sentinel)], False)
                check(f"symlink_read_{index}", ["/bin/cat", str(link)], False)
            finally:
                link.unlink(missing_ok=True)
                sentinel.unlink(missing_ok=True)
        for index, root in enumerate(readonly):
            check(f"shared_read_{index}", ["/bin/ls", str(root)], True)
            path = Path(root) / ".neumann-readonly-probe"
            if path.exists():
                raise FileExistsError(path)
            try:
                check(f"shared_write_denied_{index}", ["/usr/bin/touch", str(path)], False)
            finally:
                path.unlink(missing_ok=True)
        check(
            "public_network",
            [
                "/usr/bin/curl",
                "--fail",
                "--silent",
                "--max-time",
                "15",
                "https://developers.openai.com/robots.txt",
            ],
            True,
        )
    finally:
        marker.unlink(missing_ok=True)
    result = {
        "scope": "command_sandbox_only",
        "workspace": str(workspace),
        "checks": checks,
        "command_checks_passed": all(v["passed"] for v in checks.values()),
        "session_isolation_verified": False,
        "remaining": [
            "新会话实际 cwd 与权限绑定",
            "初始记忆/skills/项目规则注入审计",
            "文件工具、MCP、浏览器与连接器覆盖",
            "本机网络服务旁路检查",
            "完整供应商请求 usage 和活动时间流",
        ],
    }
    write_json(output, result)
    return result


class DesktopRunner:
    """桌面能力门禁；当前接口不能传入任意 cwd 或全工具读取策略。"""

    simulation = False

    def preflight(self, protocol):
        """拒绝在不可保证目录限制时创建会话，而非改用不受控目录。"""
        raise IsolationUnavailable(
            "桌面 create_thread 当前仅接收已登记 projectId 或 projectless；"
            "没有每会话读取白名单、上下文注入隔离及完整 usage/时间流参数。"
            "命令级 sandbox probe 不能替代整个会话覆盖。正式实验未启动。"
        )
