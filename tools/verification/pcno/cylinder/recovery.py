"""完整原网格真实窗口的中断恢复，覆盖数据预热和物理爬升边界。"""

import argparse
import json
import time
from pathlib import Path

import torch
import yaml

from ai4e_contrib.application.spatiotemporal_pde.pcno.configuration import validate
from ai4e_contrib.application.spatiotemporal_pde.pcno.training import train_branch
from ai4e_core import run


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("config")
    parser.add_argument("output")
    args = parser.parse_args()
    root = Path(args.output)
    root.mkdir(parents=True, exist_ok=False)
    cfg = yaml.safe_load(Path(args.config).read_text())
    cfg["train"]["updates"] = 10
    cfg["run_root"] = str(root / "runs")
    cfg["data_root"] = str(root / "data")
    preparation = cfg["inputs"]["train"]["preparation"]
    evidence = {}
    started = time.monotonic()
    for branch in ("fluid", "structure"):
        results = {}
        for label, stop, parent in (
            ("continuous", 10, None),
            ("warmup", 2, None),
            ("ramp", 4, "warmup"),
            ("restored", 10, "ramp"),
        ):

            def flow(c, branch=branch, stop=stop, parent=parent, label=label, results=results):
                item = train_branch(
                    validate(c),
                    preparation,
                    branch,
                    "physics" if branch == "fluid" else "supervised",
                    session=run.TrainingRun(),
                    stop_after=stop,
                    resume=results[parent]["checkpoint"] if parent else None,
                )
                results[label] = item
                return item

            assert run.run_recipe(cfg, stages=flow, script=__file__) == 0
        a = torch.load(results["continuous"]["checkpoint"], weights_only=False)
        b = torch.load(results["restored"]["checkpoint"], weights_only=False)
        for key in a["model"]:
            torch.testing.assert_close(a["model"][key], b["model"][key], rtol=1e-5, atol=1e-6)
        assert a["history"] == b["history"]
        for key in a["optimizer"]["state"]:
            for field in a["optimizer"]["state"][key]:
                torch.testing.assert_close(
                    a["optimizer"]["state"][key][field],
                    b["optimizer"]["state"][key][field],
                    rtol=1e-5,
                    atol=1e-6,
                )
        assert (
            torch.equal(a["torch_rng"], b["torch_rng"])
            and a["stream"]["updates"] == b["stream"]["updates"]
        )
        evidence[branch] = {
            "passed": True,
            "steps": [2, 4, 10],
            "checkpoints": {k: v["checkpoint"] for k, v in results.items()},
        }
    evidence["seconds"] = time.monotonic() - started
    (root / "recovery.json").write_text(json.dumps(evidence, indent=2) + "\n")


if __name__ == "__main__":
    main()
