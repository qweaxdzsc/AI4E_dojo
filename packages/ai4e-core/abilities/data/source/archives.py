"""压缩来源安全物化，内容校验后复用已有文件。"""

import shutil
import zipfile
import zlib
from pathlib import Path


def extract_archives(root, destination, *, execute=True):
    """已有数据引用不搬动；压缩数据只解压到独立目标，不覆盖源文件。"""
    root = Path(root).resolve()
    archives = sorted(root.glob("*.zip"))
    if not root.is_dir():
        raise FileNotFoundError(root)
    if not archives:
        return str(root)
    destination = Path(destination).resolve()
    if destination == root or root in destination.parents:
        raise ValueError("处理目标不得位于原数据内")
    if not execute:
        return str(destination)
    destination.mkdir(parents=True, exist_ok=True)
    for archive in archives:
        with zipfile.ZipFile(archive) as stream:
            for item in stream.infolist():
                if item.is_dir() or "__MACOSX" in item.filename:
                    continue
                relative = Path(item.filename)
                if relative.is_absolute() or ".." in relative.parts:
                    raise ValueError("不安全的压缩成员路径")
                target = destination / relative
                if target.exists():
                    if target.stat().st_size != item.file_size:
                        raise FileExistsError(f"已有解压产物不相符: {target}")
                    checksum = 0
                    with target.open("rb") as existing:
                        for block in iter(lambda: existing.read(4 * 1024 * 1024), b""):
                            checksum = zlib.crc32(block, checksum)
                    if checksum != item.CRC:
                        raise FileExistsError(f"已有解压内容 CRC 不符: {target}")
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                temp = target.with_suffix(target.suffix + ".extracting")
                try:
                    with stream.open(item) as src, temp.open("wb") as dst:
                        shutil.copyfileobj(src, dst)
                    temp.replace(target)
                finally:
                    temp.unlink(missing_ok=True)
    return str(destination)
