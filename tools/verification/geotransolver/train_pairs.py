"""基于正式网络测速冻结两侧更新目标，串行训练并比较完整状态与预测。"""

import json

import yaml

from .budget import DEFAULT_LEDGER, Budget
from .run_acceptance import ROOT, WORK, checked


def main():
    """各5轮，正式结构/全部节点；每个子进程及失败统一计费。"""
    paths = json.loads((WORK / "implementation/preparations.json").read_text())
    frozen = {}
    for case, prepared in paths.items():
        cfg = yaml.safe_load((ROOT / "recipes/geotransolver" / case / "config.yaml").read_text())
        cfg["pipeline"]["stages"] = ["train", "infer", "post"]
        for stage in ("train", "infer"):
            cfg["inputs"][stage]["preparation"] = prepared
        cfg["train"].update(
            updates=1250 if case == "darcy" else 620,
            device="mps",
            seconds=1800,
            checkpoint_every=250 if case == "darcy" else 124,
        )
        cfg["infer"]["device"] = "mps"
        cfg["run_root"] = str(WORK / case / "paired-runs")
        cfg["data_root"] = str(WORK / case / "paired-data")
        path = WORK / "implementation" / f"{case}-frozen.yaml"
        if path.exists() and yaml.safe_load(path.read_text()) != cfg:
            raise ValueError("已冻结协议不能覆盖")
        path.write_text(yaml.safe_dump(cfg, sort_keys=False))
        frozen[case] = str(path)
    protocol = {
        "updates": {"darcy": 1250, "bumper_beam": 620},
        "epochs": 5,
        "device": "mps",
        "precision": "float32",
        "training_grid": {"darcy": [85, 85], "bumper_beam": 13676},
        "margin": 0.5,
        "frozen_configs": frozen,
        "preparations": paths,
    }
    (WORK / "implementation/frozen-protocol.json").write_text(json.dumps(protocol, indent=2) + "\n")
    budget = Budget(DEFAULT_LEDGER)
    for case, config in frozen.items():
        checked(
            budget,
            case + "-reference-five-epochs",
            [
                "-m",
                "tools.verification.geotransolver.reference_train",
                "--case",
                case,
                "--preparation",
                paths[case],
                "--config",
                config,
                "--output",
                str(WORK / case / "reference"),
            ],
            training=True,
        )
        checked(
            budget,
            case + "-dojo-five-epochs",
            [str(ROOT / "recipes/geotransolver" / case / "pipeline.py"), "--config", config],
            training=True,
        )


if __name__ == "__main__":
    main()
