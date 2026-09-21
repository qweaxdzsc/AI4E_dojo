"""接续已完成Darcy检查点，修复报告交接后继续保险杠成对对照。"""

import json

import yaml

from .budget import DEFAULT_LEDGER, Budget
from .run_acceptance import ROOT, WORK, checked


def main():
    budget = Budget(DEFAULT_LEDGER)
    original = WORK / "darcy/paired-runs/2026-09-20T18-06-42_ed6c40/summary.json"
    state = json.loads(original.read_text())
    assert state["reports"]["train"]["updates"] == 1250
    cfg = yaml.safe_load((WORK / "implementation/darcy-frozen.yaml").read_text())
    cfg["inputs"]["train"]["resume"] = state["reports"]["train"]["checkpoint"]
    path = WORK / "implementation/darcy-completed-resume.yaml"
    path.write_text(yaml.safe_dump(cfg, sort_keys=False))
    checked(
        budget,
        "darcy-completed-checkpoint-recovery-and-post",
        [str(ROOT / "recipes/geotransolver/darcy/pipeline.py"), "--config", str(path)],
    )
    checked(
        budget,
        "darcy-full-independent-evaluation",
        ["-m", "tools.verification.geotransolver.evaluate_pairs", "--case", "darcy"],
    )
    paths = json.loads((WORK / "implementation/preparations.json").read_text())
    case = "bumper_beam"
    config = WORK / "implementation/bumper_beam-frozen.yaml"
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
            str(config),
            "--output",
            str(WORK / case / "reference"),
        ],
        training=True,
    )
    checked(
        budget,
        case + "-dojo-five-epochs",
        [str(ROOT / "recipes/geotransolver" / case / "pipeline.py"), "--config", str(config)],
        training=True,
    )
    checked(
        budget,
        case + "-full-independent-evaluation",
        ["-m", "tools.verification.geotransolver.evaluate_pairs", "--case", case],
    )


if __name__ == "__main__":
    main()
