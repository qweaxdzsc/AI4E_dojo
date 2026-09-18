"""在仓库外以真实准备数据运行公开网络/损失/派生输出变体。"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import yaml

from ai4e_core.abilities.data.save.array_manifest import read_arrays
from tools.verification.wdno.protocol import write_json

REPO = Path(__file__).resolve().parents[3]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    directory = root / "variant"
    code = directory / "recipe"
    shutil.copytree(REPO / "recipes/wdno", code, ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copy2(REPO / "examples/recipe_extensions/wdno/variants.py", code / "variants.py")
    # 可编辑的实际研究顺序，不复制数值算法或训练循环。
    (code / "experiment.py").write_text("""from configuration import load_configuration
from train import train
from infer import infer
from post import post
from ai4e_core import run

def experiment(cfg):
    trained = run.stage("train", train, cfg)
    predicted = run.stage("infer", infer, cfg, None, trained)
    return run.stage("post", post, cfg, predicted)

if __name__ == "__main__":
    raise SystemExit(run.launch(experiment, script=__file__, config_loader=load_configuration))
""")
    from ai4e_contrib.application.spatiotemporal_pde.wdno.migration import migrate_legacy

    source_config = root / "dojo-final/config.yaml"
    cfg = migrate_legacy(yaml.safe_load(source_config.read_text()), base=source_config.parent)
    cfg["run_root"] = str(directory / "runs")
    cfg["data_root"] = str(directory / "data")
    cfg["model"].update(dim=8, dim_mults=[1, 2], ddim_steps=2)
    cfg["train"].update(device="cpu", updates=2, lr=0.0002, seconds=60)
    cfg["infer"].update(device="cpu", checkpoint_format="dojo")
    cfg["inputs"]["post"] = {"validation": None, "test": None}
    cfg["inputs"]["train"]["resume"] = None
    cfg["inputs"]["infer"]["checkpoint"] = None
    cfg["pipeline"] = {"stages": ["train", "infer", "post"]}
    cfg["components"].update(
        network="variants.custom_network",
        objective="variants.custom_loss",
        derived="variants.energy",
    )
    config_path = directory / "config.yaml"
    config_path.write_text(yaml.safe_dump(cfg, sort_keys=False))
    with (directory / "console.txt").open("w") as log:
        result = subprocess.run(
            [
                "uv",
                "run",
                "--no-project",
                "--python",
                sys.executable,
                "python",
                str(code / "experiment.py"),
                "--config",
                str(config_path),
            ],
            cwd=directory,
            env={**os.environ},
            stdout=log,
            stderr=subprocess.STDOUT,
            check=False,
            timeout=180,
        )
    if result.returncode:
        raise RuntimeError("真实数据变体失败，见console.txt")
    summary = json.loads(
        max(
            (directory / "runs").glob("*/summary.json"), key=lambda p: p.stat().st_mtime_ns
        ).read_text()
    )
    scores = {}
    for split, path in summary["reports"]["infer"].items():
        record, arrays = read_arrays(path, kind="spatiotemporal-result-v1")
        expected = np.mean(arrays["prediction"] ** 2, axis=-1)
        np.testing.assert_array_equal(expected, arrays["energy"])
        assert record["metadata"]["derived_fields"]["energy"]["axes"] == ["sample", "time"]
        scores[split] = {
            "samples": len(arrays["ids"]),
            "mse": summary["reports"]["post"][split]["mse"],
            "energy_readback": True,
        }
    write_json(
        directory / "acceptance.json",
        {
            "passed": True,
            "real_original_data": True,
            "updates": summary["reports"]["train"]["updates"],
            "configuration": str(config_path),
            "network": "variants.custom_network",
            "objective": "variants.custom_loss",
            "derived": "variants.energy",
            "evaluation": scores,
            "paper_reproduced": False,
        },
    )


if __name__ == "__main__":
    main()
