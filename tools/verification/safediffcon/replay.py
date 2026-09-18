"""最终安装包重放适配和采样，与已求解的固定控制逐值核对。"""

import argparse
import json
from pathlib import Path

import numpy as np
import torch


def main():
    """当保护性检查或边界算术修正后，证明既有响应仍对应同一控制。"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    from ai4e_contrib.application.pde_control.safediffcon.configuration import (
        component,
        load_configuration,
    )
    from ai4e_contrib.application.pde_control.safediffcon.inference import adapt, generate, inputs
    from ai4e_core import run
    from ai4e_core.applications.pde_control.contracts import read_arrays

    prior = json.loads(Path(args.summary).read_text())
    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=False)

    def verify(config):
        from ai4e_contrib.application.pde_control.safediffcon.configuration import (
            application_parameters,
        )

        cfg = application_parameters(config, stage="infer")
        session = run.TrainingRun()
        values = inputs(cfg, prior["prepared"])
        model, checkpoint, q = adapt(
            cfg,
            prior["prepared"],
            prior["posttrain_checkpoint"],
            values,
            construct=component(cfg["components"]["model"]),
            guide=component(cfg["components"]["guide"]),
            session=session,
        )
        controls, prediction = generate(
            cfg, model, values, q=q, guide=component(cfg["components"]["guide"])
        )
        record, arrays = read_arrays(prior["results"], kind="control_results_v1")
        np.testing.assert_array_equal(controls, arrays["controls"])
        np.testing.assert_array_equal(prediction, arrays["prediction"])
        assert q == record["metadata"]["q"]
        old = torch.load(record["metadata"]["checkpoint"], map_location="cpu", weights_only=False)
        new = torch.load(checkpoint, map_location="cpu", weights_only=False)
        for key, value in old["model"].items():
            torch.testing.assert_close(value, new["model"][key], rtol=0, atol=0)
        payload = {
            "status": "passed",
            "scope": "current installed code generates exactly the same controls, predictions and adapted parameters; fixed physical response need not be recomputed",
            "prior_results": prior["results"],
            "current_checkpoint": checkpoint,
            "q": q,
            "controls_max_abs": 0.0,
            "prediction_max_abs": 0.0,
        }
        session.artifact("replay.json", payload)
        (output / "replay.json").write_text(json.dumps(payload, indent=2))

    return run.launch(
        {"verify": verify},
        script=__file__,
        only=["verify"],
        config_loader=load_configuration,
        argv=["--config", args.config],
    )


if __name__ == "__main__":
    raise SystemExit(main())
