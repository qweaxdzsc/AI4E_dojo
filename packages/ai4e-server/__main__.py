"""本机单用户启动，显式授权数据根。"""

import argparse
from pathlib import Path

import uvicorn

from .bootstrap.app import create_app
from .bootstrap.settings import Settings


def main():
    """从命令行装配路径，默认仅监听回环地址。"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.home() / ".dojo/platform")
    parser.add_argument("--template", type=Path, required=True)
    parser.add_argument("--data-root", type=Path, action="append", default=[])
    parser.add_argument("--web-dist", type=Path)
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    settings = Settings(
        args.root.resolve(),
        args.template.resolve(),
        [p.resolve() for p in args.data_root],
        args.web_dist.resolve() if args.web_dist else None,
    )
    uvicorn.run(create_app(settings), host="127.0.0.1", port=args.port)


if __name__ == "__main__":
    main()
