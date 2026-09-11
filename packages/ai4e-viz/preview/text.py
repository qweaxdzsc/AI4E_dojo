"""分页显示真实文本或 CSV 行，不推断科学数据类型。"""

import csv
from itertools import islice
from pathlib import Path


def preview_text(path: Path, offset: int = 0, limit: int = 100, **_) -> dict:
    """最多两百行，文本每行最多一万字符；CSV 最多六十四列。"""
    start = max(0, offset)
    count = min(max(1, limit), 200)
    with path.open(encoding="utf-8-sig", errors="replace") as stream:
        if path.suffix.lower() == ".csv":
            reader = csv.reader(stream)
            header = next(reader, [])
            rows = [[v[:10000] for v in row[:64]] for row in islice(reader, start, start + count)]
            return {
                "kind": "text",
                "offset": start,
                "columns": header[:64],
                "rows": rows,
                "columns_truncated": len(header) > 64,
            }
        lines = [line[:10000].rstrip("\n") for line in islice(stream, start, start + count)]
    return {"kind": "text", "offset": start, "lines": lines}
