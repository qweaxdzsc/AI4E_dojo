"""正式双圆柱准备入口；只保存来源清单、统计和窗口索引。"""

import argparse
from pathlib import Path

from ai4e_contrib.application.datasets.gencp.cylinder import describe, prepare

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("source")
    p.add_argument("output")
    a = p.parse_args()
    root = Path(a.output)
    root.mkdir(parents=True, exist_ok=True)
    data = describe(a.source, root / "dataset.json")
    print(prepare(data, root / "preparation.json", history=3, horizon=12), flush=True)
