"""多包解压：只认压缩格式，不认数据集。"""

from __future__ import annotations

import tarfile
import zipfile
from pathlib import Path

_ARCHIVE_ENDINGS = (".zip", ".tar", ".tar.gz", ".tgz", ".tar.bz2")


def is_archive(path: str | Path) -> bool:
    """判断路径是否为支持的压缩包。"""
    name = Path(path).name.lower()
    return name.endswith(_ARCHIVE_ENDINGS)


def extract_archives(
    directory: str | Path,
    *,
    recursive: bool = False,
) -> list[Path]:
    """解开目录中的多个压缩包，不删除原包，也不解释内容。

    Args:
        directory: 存放压缩包的目录。
        recursive: 是否进入子目录查找压缩包。

    Returns:
        已解开的压缩包路径列表，按路径排序。

    Raises:
        FileNotFoundError: 目录不存在。
    """
    root = Path(directory)
    if not root.is_dir():
        raise FileNotFoundError(f"解压目录不存在: {root}")

    candidates = root.rglob("*") if recursive else root.iterdir()
    archives = sorted(path for path in candidates if path.is_file() and is_archive(path))
    for archive in archives:
        _extract_one(archive, archive.parent)
    return archives


def _extract_one(archive: Path, dest: Path) -> None:
    """把单个压缩包解到目标目录。"""
    dest.mkdir(parents=True, exist_ok=True)
    name = archive.name.lower()
    if name.endswith(".zip"):
        with zipfile.ZipFile(archive) as handle:
            handle.extractall(dest)
        return
    with tarfile.open(archive) as handle:
        handle.extractall(dest, filter="data")
