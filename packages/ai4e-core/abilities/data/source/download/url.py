"""普通网址下载，不解释文件内容。"""

from __future__ import annotations

import urllib.request
from collections.abc import Callable
from pathlib import Path

FetchFn = Callable[[str, Path], None]


def _default_fetch(url: str, dest: Path) -> None:
    """用标准库把网址写到本地文件。"""
    urllib.request.urlretrieve(url, dest)


def download_url(
    url: str,
    dest: str | Path,
    *,
    fetch: FetchFn | None = None,
) -> Path:
    """把一个网址下载为本地文件。

    Args:
        url: 下载地址。
        dest: 本地文件路径，不是目录。
        fetch: 可替换的取回函数，测试用替身。

    Returns:
        写好的本地文件路径。
    """
    if not url:
        raise ValueError("下载地址不能为空")
    path = Path(dest)
    path.parent.mkdir(parents=True, exist_ok=True)
    writer = fetch or _default_fetch
    writer(url, path)
    if not path.is_file():
        raise FileNotFoundError(f"下载未写出文件: {path}")
    return path
