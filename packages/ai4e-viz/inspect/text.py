"""文本与 CSV 的有限读取，CSV 首行作为显示列名。"""

import csv
from pathlib import Path


def inspect_text(path: Path) -> dict:
    """读取 CSV 真实表头；文本无字段，不执行内容。"""
    fields = []
    if path.suffix.lower() == ".csv":
        with path.open(encoding="utf-8-sig", errors="replace") as stream:
            header = next(csv.reader(stream), [])
        fields = [
            {"id": str(i), "name": name, "association": "column", "shape": [], "dtype": "text"}
            for i, name in enumerate(header[:64])
        ]
    return {"kind": "text", "fields": fields, "size": path.stat().st_size}
