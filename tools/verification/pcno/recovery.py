"""真实PCNO中断恢复：公开run入口，固定两次更新目标，分支分别核对。"""

import argparse
import json
from pathlib import Path

import torch
import yaml

from ai4e_contrib.application.geothermal.pcno.configuration import component, load_configuration
from ai4e_contrib.application.geothermal.pcno.training import train_branch
from ai4e_core import run


def equal(a, b):
    if isinstance(a, torch.Tensor):
        torch.testing.assert_close(a, b, rtol=0, atol=0)
    elif isinstance(a, dict):
        assert a.keys() == b.keys()
        for key in a:
            equal(a[key], b[key])
    elif isinstance(a, (list, tuple)):
        assert len(a) == len(b)
        for x, y in zip(a, b):
            equal(x, y)
    else:
        assert a == b


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("config", type=Path)
    p.add_argument("preparation", type=Path)
    p.add_argument("output", type=Path)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    reports = {}
    for branch in ["pres", "temp"]:
        saved = {}
        for mode in ["full", "interrupted", "resumed"]:
            cfg = yaml.safe_load(a.config.read_text())
            cfg["train"]["updates"] = 2
            cfg["run_root"] = str(a.output / branch / mode / "runs")
            cfg["data_root"] = str(a.output / branch / mode / "data")
            cfg["pipeline"]["stages"] = ["train"]
            cfg["inputs"]["train"]["preparation"] = str(a.preparation)
            file = a.output / (branch + "-" + mode + ".yaml")
            file.write_text(yaml.safe_dump(cfg))

            def pipeline(config, mode=mode, branch=branch, saved=saved):
                session = run.TrainingRun()
                calls = []

                def stop():
                    calls.append(1)
                    return mode == "interrupted" and len(calls) > 1

                return train_branch(
                    config,
                    a.preparation,
                    branch,
                    construct=component(config["components"]["network"]),
                    objective=component(config["components"]["objective"]),
                    session=session,
                    resume=saved.get("interrupted") if mode == "resumed" else None,
                    cancelled=stop,
                )

            result = run.launch(
                pipeline,
                script=__file__,
                config_loader=load_configuration,
                argv=["--config", str(file)],
            )
            assert result == (1 if mode == "interrupted" else 0), result
            saved[mode] = next(Path(cfg["run_root"]).glob("*/checkpoints/" + branch + "/latest.pt"))
        before = torch.load(saved["interrupted"], weights_only=False)
        assert before["status"] == "interrupted" and before["updates"] == 1
        full = torch.load(saved["full"], weights_only=False)
        resumed = torch.load(saved["resumed"], weights_only=False)
        for key in [
            "model",
            "optimizer",
            "scheduler",
            "stream",
            "history",
            "python_rng",
            "torch_rng",
        ]:
            equal(full[key], resumed[key])
        reports[branch] = {
            "passed": True,
            "interrupted_updates": 1,
            "target_updates": 2,
            "rtol": 0,
            "atol": 0,
            "files": {k: str(v) for k, v in saved.items()},
        }
    (a.output / "comparison.json").write_text(json.dumps(reports, indent=2))


if __name__ == "__main__":
    main()
