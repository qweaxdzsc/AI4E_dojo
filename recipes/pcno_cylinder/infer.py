"""显式加载冻结分支、组装读取与预测、交付独立结果。"""

import json
from pathlib import Path

from configuration import load_configuration, validate

from ai4e_contrib.application.spatiotemporal_pde.pcno.inference import (
    evaluation_records,
    load_networks,
    predictor,
    reader,
)
from ai4e_core import run
from ai4e_core.applications.spatiotemporal_pde.window_results import predict_windows
from ai4e_core.base.config.conventions import resolve_input


def infer(cfg, preparation=None, checkpoints=None):
    cfg = validate(cfg)
    session = run.TrainingRun()
    if session.dry_run:
        return None
    prepared = resolve_input(
        preparation, cfg["inputs"]["infer"]["preparation"], name="infer.preparation"
    )
    weights = resolve_input(
        checkpoints, cfg["inputs"]["infer"]["checkpoints"], name="infer.checkpoints"
    )
    record, networks, provenance = load_networks(cfg, prepared, weights)
    windows = evaluation_records(record, cfg["infer"]["split"])
    read = reader(record)
    predict = predictor(record, networks, provenance)
    result = predict_windows(windows, read, predict, session.output_dir("infer"))
    manifests = json.loads(Path(result).read_text())["windows"]
    arrays = [str(p) for m in manifests for p in Path(m).parent.glob("*.npy")]
    session.record_asset(
        "results",
        result,
        kind="other",
        stage="infer",
        dependencies=manifests + arrays,
        bundle_root=Path(result).parent,
    )
    session.report(
        {
            "results": result,
            "windows": len(windows),
            "scope": "held-out validation trajectory, not independent test",
        },
        stage="infer",
    )
    return result


if __name__ == "__main__":
    raise SystemExit(
        run.launch(
            {"infer": infer}, script=__file__, only=["infer"], config_loader=load_configuration
        )
    )
