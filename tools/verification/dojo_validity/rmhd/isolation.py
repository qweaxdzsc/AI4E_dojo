"""RMHD 整进程 Seatbelt 边界；推理工作进程另用完全断网策略。"""

import json
import os
import subprocess
from pathlib import Path

from ..io import digest, write_json


def policy(writable, readonly=(), *, proxy_port=None):
    """只开放显式材料路径与系统运行时；不授予父目录枚举或宿主用户资料。"""
    folder = Path(__file__).parents[1] / "policies"
    platform = (folder / "platform.sbpl").read_text()
    # 上游宽泛软件目录与动态扩展不适合双组实验；只允许已登记的具体运行时。
    platform = "\n".join(
        line
        for line in platform.splitlines()
        if not any(
            token in line
            for token in (
                "/opt/homebrew/lib",
                "/usr/local/lib",
                "(extension ",
                "network-outbound",
                "dt.automationmode.reader",
            )
        )
    )
    body = (folder / "base.sbpl").read_text() + "\n" + platform
    for path in readonly:
        resolved = Path(path).resolve(strict=True)
        matcher = "subpath" if resolved.is_dir() else "literal"
        body += f"\n(allow file-read* file-map-executable ({matcher} {json.dumps(str(resolved))}))"
        body += f"\n(allow file-read-metadata (path-ancestors {json.dumps(str(resolved))}))"
        body += f"\n(allow file-read-metadata (path-ancestors {json.dumps(str(Path(path).absolute()))}))"
    for path in writable:
        resolved = Path(path).resolve(strict=True)
        body += f"\n(allow file-read* file-write* file-map-executable (subpath {json.dumps(str(resolved))}))"
        body += f"\n(allow file-read-metadata (path-ancestors {json.dumps(str(resolved))}))"
    body += """
(allow file-read* (subpath "/System/Library/Extensions"))
(allow iokit-open
  (iokit-user-client-class "AGXDeviceUserClient")
  (iokit-user-client-class "IOAccelSharedUserClient2")
  (iokit-user-client-class "IOAccelContext2"))
(allow mach-lookup
  (global-name "com.apple.MTLCompilerService")
  (global-name "com.apple.GPUCompilerService")
  (global-name "com.apple.CARenderServer"))
"""
    if proxy_port is not None:
        if type(proxy_port) is not int or not 1024 <= proxy_port <= 65535:
            raise ValueError("非法公网代理端口")
        body += "\n" + (folder / "network.sbpl").read_text()
        # Seatbelt 的 remote 地址语法不支持 CIDR。唯一连接口由主控代理校验解析后的IP。
        body += f'\n(allow network-outbound (remote tcp "localhost:{proxy_port}"))\n'
    return body


def clean_environment(experiment, extra=None):
    """白名单环境：不复制宿主 os.environ，不暴露无关 key、代理或源码路径。"""
    root = Path(experiment).resolve()
    result = {
        "HOME": str(root / "home"),
        "CODEX_HOME": str(root / "agent-state"),
        "TMPDIR": str(root / "tmp"),
        "XDG_CACHE_HOME": str(root / "cache"),
        "UV_CACHE_DIR": str(root / "cache/uv"),
        "UV_LINK_MODE": "copy",
        "PATH": f"{root}/environment/bin:{root}/tools:/usr/bin:/bin:/usr/sbin:/sbin",
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONNOUSERSITE": "1",
        "OMP_NUM_THREADS": "6",
        "MKL_NUM_THREADS": "6",
        "LANG": "en_US.UTF-8",
        "NO_PROXY": "*",
        "no_proxy": "*",
        "PYTORCH_ENABLE_MPS_FALLBACK": "0",
    }
    if extra:
        result.update(extra)
    return result


def execute(body, command, cwd, env=None, timeout=30):
    """外层沙箱覆盖全部子进程，使用参数数组，不经过 shell 拼接。"""
    return subprocess.run(
        ["/usr/bin/sandbox-exec", "-p", body, *map(str, command)],
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


def probe(root, readonly, forbidden, output, *, python=None, proxy_port=None):
    """在实际工作根测试读写、父目录、链接、子进程与网络；记录每项证据。"""
    root, output = Path(root).resolve(), Path(output)
    body = policy([root], readonly, proxy_port=proxy_port)
    rows = []
    own = root / ".isolation-probe"
    own.mkdir(exist_ok=False)
    for name in ("home", "tmp", "cache", "agent-state"):
        (own / name).mkdir()
    environment = clean_environment(own)

    def check(name, args, success):
        proc = execute(body, args, root, env=environment)
        passed = (proc.returncode == 0) == success
        rows.append(
            {
                "name": name,
                "command": list(map(str, args)),
                "expected_success": success,
                "returncode": proc.returncode,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
                "passed": passed,
            }
        )

    try:
        check("own-write", ["/usr/bin/touch", own / "allowed"], True)
        check("own-read", ["/bin/cat", own / "allowed"], True)
        check("parent-list", ["/bin/ls", root.parent], False)
        for i, target in enumerate(forbidden):
            target = Path(target).resolve(strict=True)
            sentinel = target if target.is_file() else target / ".isolation-sentinel"
            made = target.is_dir() and not sentinel.exists()
            if made:
                sentinel.write_text("controller-private sentinel")
            try:
                check(f"forbidden-read-{i}", ["/bin/cat", sentinel], False)
                check(f"forbidden-write-{i}", ["/usr/bin/touch", sentinel], False)
                link = own / f"link-{i}"
                link.symlink_to(sentinel)
                check(f"symlink-{i}", ["/bin/cat", link], False)
                check(f"hardlink-{i}", ["/bin/ln", sentinel, own / f"hard-{i}"], False)
                check(f"subprocess-{i}", ["/bin/sh", "-c", 'cat "$1"', "probe", sentinel], False)
            finally:
                if made:
                    sentinel.unlink()
        if proxy_port:
            check(
                "public-internet",
                [
                    "/usr/bin/curl",
                    "--noproxy",
                    "",
                    "--proxy",
                    f"http://127.0.0.1:{proxy_port}",
                    "--max-time",
                    "15",
                    "-I",
                    "https://pypi.org",
                ],
                True,
            )
        check(
            "direct-network-denied",
            ["/usr/bin/curl", "--noproxy", "*", "--max-time", "3", "https://1.1.1.1"],
            False,
        )
        if python:
            check(
                "mps",
                [
                    python,
                    "-c",
                    "import torch; assert torch.backends.mps.is_available(); x=torch.ones(4,device='mps'); assert float((x*x).sum().cpu())==4; torch.mps.synchronize()",
                ],
                True,
            )
    finally:
        for path in own.iterdir():
            if path.is_dir() and not path.is_symlink():
                import shutil

                shutil.rmtree(path)
            else:
                path.unlink()
        own.rmdir()
    output.parent.mkdir(parents=True, exist_ok=True)
    policy_file = output.with_suffix(".sbpl")
    policy_file.write_text(body)
    result = {
        "passed": all(r["passed"] for r in rows),
        "checks": rows,
        "mps_probed": python is not None,
        "workspace_root": str(root),
        "policy_sha256": digest(policy_file),
        "pid": os.getpid(),
    }
    write_json(output, result)
    return result
