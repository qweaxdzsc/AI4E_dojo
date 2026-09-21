"""共同起点与现有 Neumann 数值路径对照，以及独立环境 round-00 测量。"""

import importlib.util
import subprocess
import time
import uuid
from pathlib import Path

import numpy as np
import torch

from .baseline_runtime import model_and_data, objective
from .io import digest, read_json, write_json
from .metrics import evaluate
from .prepare import REPO
from .runner import validate_protocol


def verify_baseline(baseline, output):
    """逐值核对共同输入、原初始化、样条矩阵和一次完整更新；不替代精度训练。"""
    from ai4e_contrib.ability.model.pibsnet import source_cases
    from ai4e_contrib.application.datasets.neumann_diffusion.generate import make_sample

    baseline = Path(baseline)
    spec = importlib.util.spec_from_file_location(
        "neumann_configuration", REPO / "recipes/parametric_pde/configuration.py"
    )
    configuration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(configuration)
    config = configuration.defaults("neumann_diffusion")
    torch.set_num_threads(1)
    model, data, bases = model_and_data(baseline)
    torch.manual_seed(42)
    reference = source_cases.build(config)
    for name, value in model.state_dict().items():
        torch.testing.assert_close(value, reference.state_dict()[name], rtol=0, atol=0)
    for left, right in zip(bases, source_cases.basis("neumann_diffusion", 40, 5, 128), strict=True):
        torch.testing.assert_close(left, right, rtol=0, atol=0)
    rng = np.random.RandomState(42)
    samples = []
    for split, count in (("train", 50), ("test", 10)):
        for index in range(count):
            sample = make_sample(rng, {"nx": 128, "nt": 128}, index=index, split=split)
            torch.testing.assert_close(data[f"{split}_u"][index], sample["u"], rtol=0, atol=0)
            assert data[f"{split}_nu"][index].item() == sample["parameters"]["nu"]
            if split == "train":
                samples.append(sample)
    total, expected = 0.0, 0.0
    for index, sample in enumerate(samples):
        total = total + objective(model, data["train_nu"][index], data["train_u"][index], bases)[0]
        prepared = {"sample": sample, "grid_bases": [bases, bases], "sets": {}}
        expected = expected + source_cases.step(reference, prepared, config)["loss"]
    torch.testing.assert_close(total, expected, rtol=0, atol=0)
    total.backward()
    expected.backward()
    for left, right in zip(model.parameters(), reference.parameters(), strict=True):
        torch.testing.assert_close(left.grad, right.grad, rtol=0, atol=0)
    for network in (model, reference):
        torch.optim.Adam(network.parameters(), lr=0.001).step()
    for left, right in zip(model.parameters(), reference.parameters(), strict=True):
        torch.testing.assert_close(left, right, rtol=0, atol=0)
    result = {
        "status": "complete",
        "dataset_samples_exact": 60,
        "initial_weights_exact": True,
        "basis_exact": True,
        "loss_gradient_and_one_update_exact": True,
        "parameters": sum(p.numel() for p in model.parameters()),
        "scope": "initialization_and_one_update_not_full_training",
    }
    write_json(output, result)
    return result


def measure_baseline(experiment, truth_manifest, *, epochs=5000):
    """在本组独立解释器顺序训练和推理，保留重试；短训只能标 smoke。"""
    experiment = Path(experiment).resolve()
    protocol = validate_protocol(experiment)
    if not protocol["environment_ready"]:
        raise ValueError("环境尚未就绪")
    attempt = experiment / "round-00" / str(uuid.uuid4())
    attempt.mkdir()
    python = experiment / "environment/bin/python"
    script = experiment / "baseline/source/baseline.py"
    base = [
        "uv",
        "run",
        "--no-project",
        "--no-sync",
        "--python",
        str(python),
        "python",
        "-B",
        str(script),
    ]
    commands = [
        (
            "training",
            [
                *base,
                "train",
                "--baseline",
                str(experiment / "baseline"),
                "--output",
                str(attempt / "training"),
                "--epochs",
                str(epochs),
            ],
        ),
        (
            "evaluation",
            [
                *base,
                "predict",
                "--baseline",
                str(experiment / "baseline"),
                "--checkpoint",
                str(attempt / "training/checkpoint.pt"),
                "--output",
                str(attempt / "predictions"),
            ],
        ),
    ]
    events = []
    try:
        for phase, argv in commands:
            start = time.monotonic()
            with (attempt / f"{phase}.log").open("w") as log:
                result = subprocess.run(
                    argv,
                    cwd=protocol["session_workspace_root"],
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    check=False,
                )
            events.append(
                {
                    "event_id": str(uuid.uuid4()),
                    "phase": phase,
                    "start": start,
                    "end": time.monotonic(),
                    "command": argv,
                    "exit_code": result.returncode,
                }
            )
            write_json(attempt / "events.json", events)
            result.check_returncode()
        start = time.monotonic()
        metrics = evaluate(
            attempt / "predictions/predictions.json", truth_manifest, attempt / "metrics.json"
        )
        events.append(
            {
                "event_id": str(uuid.uuid4()),
                "phase": "evaluation",
                "start": start,
                "end": time.monotonic(),
                "operation": "independent_fp64_evaluator",
            }
        )
        write_json(attempt / "events.json", events)
        output = {
            "status": "complete" if epochs == 5000 else "smoke",
            "epochs": epochs,
            "attempt": str(attempt.relative_to(experiment)),
            "metrics": metrics,
            "training": read_json(attempt / "training/training.json"),
            "checkpoint_sha256": digest(attempt / "training/checkpoint.pt"),
            "events": events,
        }
        write_json(attempt / "result.json", output)
        if epochs == 5000:
            write_json(experiment / "round-00/result.json", output)
        return output
    except BaseException as exc:
        write_json(attempt / "failure.json", {"error": str(exc), "type": type(exc).__name__})
        raise
