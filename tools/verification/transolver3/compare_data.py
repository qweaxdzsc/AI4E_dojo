"""全量 NPY 物理数据逐元素对照，检查分片、字段、统计和参考元数据。"""

import argparse
import json
from pathlib import Path

import numpy as np

from tools.verification.transolver3.compare import require


def main():
    """输出轻量最大误差记录，不把大型数据加入代码目录。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--actual", type=Path, required=True)
    parser.add_argument("--expected", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    left = json.loads((args.actual / "manifest.json").read_text())
    right = json.loads((args.expected / "manifest.json").read_text())
    for key in ("fields", "input_fields", "splits", "statistics", "point_count", "chunk_count"):
        if left[key] != right[key]:
            raise AssertionError(f"manifest/{key}")
    reports = []
    for split, names in right["splits"].items():
        for name in names:
            prefix = Path(split) / name
            a = json.loads((args.actual / prefix / "metadata.json").read_text())
            b = json.loads((args.expected / prefix / "metadata.json").read_text())
            if a != b:
                raise AssertionError(f"{prefix}/metadata")
            files = sorted((args.expected / prefix).glob("*.npy"))
            if {p.name for p in (args.actual / prefix).glob("*.npy")} != {p.name for p in files}:
                raise AssertionError(f"{prefix}/files")
            for path in files:
                reports.append(
                    require(
                        np.load(args.actual / prefix / path.name),
                        np.load(path),
                        identity=str(prefix / path.name),
                    )
                )
    result = {
        "passed": True,
        "arrays": len(reports),
        "split_counts": {k: len(v) for k, v in right["splits"].items()},
        "statistics": left["statistics"],
        "max_absolute_error": max(r["max_absolute_error"] for r in reports),
        "actual": str(args.actual),
        "expected": str(args.expected),
        "mismatch_count": 0,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2))
    print(json.dumps(result))


if __name__ == "__main__":
    main()
