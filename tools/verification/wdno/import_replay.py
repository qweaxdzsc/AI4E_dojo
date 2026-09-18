"""经公开 source 权重导入入口重放原版两组首批，固定样本且独立输出。"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import yaml

from ai4e_core import run
from ai4e_core.abilities.data.save.array_manifest import read_arrays, save_arrays
from tools.verification.wdno.protocol import write_json


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    code = Path(__file__).resolve().parents[3] / "recipes/wdno"
    sys.path.insert(0, str(code))
    from infer import infer
    from post import post

    from ai4e_contrib.application.spatiotemporal_pde.wdno.migration import migrate_legacy

    config_path = root / "dojo-final/config.yaml"
    cfg = migrate_legacy(yaml.safe_load(config_path.read_text()), base=config_path.parent)
    output = root / "source-import-current"
    cfg["run_root"] = str(output / "runs")
    cfg["data_root"] = str(output / "data")
    cfg["infer"]["checkpoint_format"] = "source"
    cfg["inputs"]["infer"]["checkpoint"] = str(root / "reference-current-2/checkpoints/latest.pt")
    for split in ("validation", "test"):
        record, arrays = read_arrays(
            cfg["inputs"]["infer"][split], kind="spatiotemporal-physical-v1"
        )
        cfg["inputs"]["infer"][split] = save_arrays(
            output / "physical" / split,
            {key: value[:16] for key, value in arrays.items()},
            kind="spatiotemporal-physical-v1",
            metadata=record["metadata"],
        )
    path = output / "config.yaml"

    cfg["inputs"]["post"] = {"validation": None, "test": None}
    cfg["pipeline"] = {"stages": ["infer", "post"]}
    path.write_text(yaml.safe_dump(cfg, sort_keys=False))

    def replay(current):
        results = run.stage("infer", infer, current)
        return run.stage("post", post, current, results)

    status = run.run_recipe(
        cfg,
        stages=replay,
        script=code / "infer.py",
        only=["infer", "post"],
        source_config=path,
    )
    if status:
        raise RuntimeError("原权重导入重放失败")
    summary = json.loads(
        max(
            (output / "runs").glob("*/summary.json"), key=lambda p: p.stat().st_mtime_ns
        ).read_text()
    )
    report = {}
    for split, path in summary["reports"]["infer"].items():
        _, arrays = read_arrays(path, kind="spatiotemporal-result-v1")
        with np.load(root / f"reference-current-2/{split}-results.npz") as reference:
            np.testing.assert_array_equal(arrays["ids"], reference["ids"][:16])
            error = float(np.max(np.abs(arrays["prediction"] - reference["prediction"][:16])))
        report[split] = {"samples": 16, "max_abs": error, "passed": error == 0}
    write_json(output / "replay.json", report)
    if not all(x["passed"] for x in report.values()):
        raise AssertionError("原检查点导入采样未逐值一致")


if __name__ == "__main__":
    main()
