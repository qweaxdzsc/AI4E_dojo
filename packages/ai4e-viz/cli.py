"""独立可视化应用入口，旧模块名只在专属进程中解析。"""

from __future__ import annotations

import argparse
import os
import sys
from importlib.util import find_spec
from pathlib import Path


def check_workbench_dependencies() -> None:
    """启动前核对工作台依赖，避免只返回缺模块堆栈或空白 iframe。"""
    required = (
        "trame",
        "trame_vtk",
        "trame_vuetify",
        "vtk",
        "pandas",
        "fastapi",
        "uvicorn",
        "pyarrow",
        "multipart",
        "trimesh",
        "PIL",
        "imageio",
        "imageio_ffmpeg",
        "httpx",
        "jsonschema",
        "aiohttp",
    )
    missing = [name for name in required if find_spec(name) is None]
    if missing:
        raise RuntimeError(
            "可视化工作台缺少依赖："
            + ", ".join(missing)
            + "。请在当前运行环境安装 ai4e-viz[workbench]；"
            "Dojo 工作区使用既有 visualization 依赖组（uv sync --group visualization）。"
        )


def main() -> None:
    """启动独立 API 与静态前端，不导入 Dojo task/core。"""
    parser = argparse.ArgumentParser(description="AI4E 可视化工作台")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8091)
    parser.add_argument("--runtime-root", type=Path)
    parser.add_argument("--context", type=Path, help="可信来源绑定与任务输出位置 JSON")
    args = parser.parse_args()
    try:
        check_workbench_dependencies()
    except RuntimeError as exc:
        parser.exit(2, str(exc) + "\n")
    if args.runtime_root:
        os.environ["AI4E_VIS_RUNTIME_DIR"] = str(args.runtime_root.resolve())
    sys.path.insert(0, str(Path(__file__).parent / "backend"))
    import uvicorn
    from server.api import app

    if args.context:
        import json

        context = app.state.runtime.register(json.loads(args.context.read_text()))
        print(
            f"工作台：http://{args.host}:{args.port}/workspace/#/phys?context={context['context_id']}",
            flush=True,
        )
    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
