"""用当前 Dojo 数值依赖加载指定 Noether 源码，仅服务于离线对照工具。"""

import argparse
import runpy
import sys
from pathlib import Path

# 先绑定当前安装环境的 Torch，避免参考环境的二进制与当前 PyG 扩展不匹配。
import torch  # noqa: F401


def main():
    """参考源码优先，缺少的纯 Python 依赖从指定环境追加，产品包不受影响。"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--noether", type=Path, required=True)
    parser.add_argument("--reference-site", type=Path)
    parser.add_argument("tool")
    args, forwarded = parser.parse_known_args()
    folder = Path(__file__).resolve().parent
    tool = (folder / args.tool).resolve()
    if tool.parent != folder or not tool.is_file() or tool == Path(__file__).resolve():
        raise ValueError("必须选择本目录的对照脚本")
    root = args.noether.resolve()
    site = (
        args.reference_site
        or root
        / ".venv/lib"
        / f"python{sys.version_info.major}.{sys.version_info.minor}"
        / "site-packages"
    )
    for path in (root / "src", root / "recipes/aero_cfd/src", site):
        if not path.is_dir():
            raise ValueError(f"参考环境路径不存在: {path}")
    sys.path[:0] = [str(folder), str(root / "src"), str(root / "recipes/aero_cfd/src")]
    sys.path.append(str(site))
    sys.argv = [str(tool), *forwarded]
    runpy.run_path(str(tool), run_name="__main__")


if __name__ == "__main__":
    main()
