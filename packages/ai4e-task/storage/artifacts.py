"""只读 core 自包含运行产物，不读取训练对象。"""

from pathlib import Path

from .files import read_json


def read_run(directory) -> dict:
    """读取稳定记录，未完成时不伪造摘要。"""
    directory = Path(directory)
    result = {}
    for name in ("summary", "lineage"):
        path = directory / f"{name}.json"
        if path.exists():
            result[name] = read_json(path)
    return result
