"""服务、数据库和磁盘健康检查，与业务数据质量检测严格分离。"""

from __future__ import annotations

import shutil
import socket
import urllib.parse
from datetime import datetime
from pathlib import Path
import os

from infrastructure.config import runtime_paths
from infrastructure.persistence.sqlite import connect


def runtime_health() -> dict[str, object]:
    """检查运行目录磁盘空间和SQLite连接，不解析任何业务数据。"""

    paths = runtime_paths().ensure()
    usage = shutil.disk_usage(paths.root)
    with connect(paths.database) as connection:
        connection.execute("SELECT 1").fetchone()
    return {"status": "ok", "database": "ready", "disk_free_bytes": usage.free}


def _port_live(port: int) -> bool:
    """以短超时探测本机服务端口；失败只表示当前进程不可达。"""

    try:
        with socket.create_connection(("127.0.0.1", port), timeout=0.25):
            return True
    except OSError:
        return False


def renderer_health(repository_root: Path) -> dict[str, object]:
    """返回无业务含义的渲染运行时健康状态。

    此检查只验证浏览器端资源是否存在和 Trame 端口是否可达，不读取业务数据，也不把
    URL、Server 或健康协议放进 ``visEngine``。
    """

    trame_base = os.environ.get("QODER_TRAME_BASE", "http://127.0.0.1:8090")
    trame_port = urllib.parse.urlparse(trame_base).port or 8090
    o3dv_bundle = repository_root / "frontend" / "public" / "3dviewer" / "o3dv.min.js"
    return {
        "updated_at": datetime.now().astimezone().isoformat(),
        "renderers": {
            "echarts-svg": {"state": "live", "mode": "client"},
            "perspective": {"state": "live", "mode": "client"},
            "o3dv": {"state": "live" if o3dv_bundle.exists() else "offline", "mode": "self-hosted"},
            "trame-vtkjs": {
                "state": "live" if _port_live(trame_port) else "offline",
                "mode": "service", "fallback": "data-derived-inline",
            },
        },
    }
