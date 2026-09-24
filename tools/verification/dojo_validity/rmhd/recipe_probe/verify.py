"""真实 MPS 对照：原始科学更新、独立前处理与跨进程完整恢复。"""

import argparse
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from uuid import uuid4

import numpy as np
import torch


def load_module(name, path):
    """独立加载可信冻结参考，避免同名模块污染。"""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_train(root, preparation, label, updates, resume=None):
    """每个恢复段在新的解释器运行，仍通过复制案例的 pipeline。"""
    label = label + "-" + uuid4().hex[:8]
    records = root / "verification" / label
    args = [
        "uv",
        "run",
        "--no-sync",
        "python",
        str(root / "case/pipeline.py"),
        "--set",
        "pipeline.stages=[train]",
        "--set",
        f"run_root={records}",
        "--set",
        f"inputs.train.preparation={preparation}",
        "--set",
        f"train.updates={updates}",
        "--set",
        "train.evaluate_every=10000",
    ]
    if resume:
        args += ["--set", f"inputs.train.resume={resume}"]
    with (root / f"{label}.log").open("w") as log:
        subprocess.run(args, stdout=log, stderr=subprocess.STDOUT, check=True)
    summaries = list(records.glob("*/summary.json"))
    if len(summaries) != 1:
        raise RuntimeError("验证运行身份不唯一")
    summary = json.loads(summaries[0].read_text())
    if summary["failed"]:
        raise RuntimeError(summary)
    return summary["reports"]["train"]


def main(root, source):
    """按预先给定误差门槛验证，并保存完整差值而非只保存通过布尔值。"""
    root, source = Path(root), Path(source)
    sys.path.insert(0, str(root / "case"))
    from baseline_model import UNet
    from local_training import WindowStream, block_mse, predict_blocks

    from ai4e_core.abilities.data.save.array_manifest import read_arrays

    torch.set_num_threads(6)
    assert torch.backends.mps.is_available()
    summaries = [json.loads(p.read_text()) for p in (root / "records").glob("*/summary.json")]
    prepared = [
        r["reports"]["trainprep"]["preparation"]
        for r in summaries
        if not r["failed"] and "trainprep" in r["reports"]
    ]
    if len(prepared) != 1:
        raise RuntimeError("需要唯一成功的独立准备")
    preparation = Path(prepared[0])
    data = json.loads(preparation.read_text())
    old = json.loads((source / "round-00/prepared/statistics.json").read_text())
    for key in ["mean", "std"]:
        np.testing.assert_allclose(data["statistics"][key], old[key], rtol=1e-11, atol=1e-14)
    _, arrays = read_arrays(data["train"][0]["manifest"], kind="rmhd-normalized-v1")
    original = np.load(source / "round-00/prepared/train-001.npy", mmap_mode="r")
    normalized_max = float(np.max(np.abs(arrays["values"] - original)))
    np.testing.assert_allclose(arrays["values"], original, rtol=1e-6, atol=1e-6)
    reference = load_module("reference_predictor", source / "round-00/submission/predictor.py")
    initial = torch.load(root / "assets/initial.pt", map_location="cpu", weights_only=True)
    models = [UNet().to("mps") for _ in range(2)]
    for model in models:
        model.load_state_dict(initial)
    values = torch.from_numpy(np.array(arrays["values"][:50])[None]).to("mps")
    p = reference.rollout(models[0], values[:, :10])
    q = predict_blocks(models[1], values[:, :10])
    torch.testing.assert_close(p, q, rtol=0, atol=0)
    losses = [(p - values[:, 10:]).square().mean(), block_mse(models[1], values)]
    optimizers = [torch.optim.Adam(model.parameters(), lr=0.001) for model in models]
    for loss, opt in zip(losses, optimizers, strict=True):
        opt.zero_grad()
        loss.backward()
    gradient_max = max(
        float((a.grad - b.grad).abs().max())
        for a, b in zip(models[0].parameters(), models[1].parameters(), strict=True)
    )
    for a, b in zip(models[0].parameters(), models[1].parameters(), strict=True):
        torch.testing.assert_close(a.grad, b.grad, rtol=1e-4, atol=1e-7)
    for opt in optimizers:
        opt.step()
    weight_max = max(
        float((a - b).abs().max())
        for a, b in zip(models[0].parameters(), models[1].parameters(), strict=True)
    )
    for a, b in zip(models[0].parameters(), models[1].parameters(), strict=True):
        torch.testing.assert_close(a, b, rtol=1e-4, atol=1e-6)
    stream = WindowStream(70, 16, seed=42)
    schedule = [stream.next() for _ in range(5)]
    assert list(map(len, schedule)) == [16, 16, 16, 16, 6]
    rng = np.random.Generator(np.random.PCG64(42))
    starts = rng.integers(0, 162, size=70)
    order = rng.permutation(70)
    assert [item for batch in schedule for item in batch] == [
        (int(i), int(starts[i])) for i in order
    ]
    del p, q, models, optimizers, values, losses
    torch.mps.empty_cache()
    continuous = run_train(root, preparation, "continuous", 10)
    first = run_train(root, preparation, "first", 5)
    resumed = run_train(root, preparation, "resumed", 10, first["checkpoint"])
    a = torch.load(continuous["checkpoint"], map_location="cpu", weights_only=False)
    b = torch.load(resumed["checkpoint"], map_location="cpu", weights_only=False)
    differences = []

    def equal(x, y, path=""):
        if isinstance(x, torch.Tensor):
            torch.testing.assert_close(x, y, rtol=0, atol=0)
            differences.append({"path": path, "max_abs": 0})
        elif isinstance(x, np.ndarray):
            np.testing.assert_array_equal(x, y)
        elif isinstance(x, dict):
            assert x.keys() == y.keys()
            for k in x:
                equal(x[k], y[k], path + "." + str(k))
        elif isinstance(x, (list, tuple)):
            assert len(x) == len(y)
            for i, (xx, yy) in enumerate(zip(x, y, strict=True)):
                equal(xx, yy, path + "." + str(i))
        else:
            assert x == y, (path, x, y)

    for key in [
        "model",
        "optimizer",
        "stream",
        "history",
        "python_rng",
        "numpy_rng",
        "torch_rng",
        "mps_rng",
    ]:
        equal(a[key], b[key], key)
    report = {
        "status": "passed",
        "device": "mps",
        "train_trajectories": len(data["train"]),
        "validation_trajectories": len(data["validation"]),
        "prepared": str(preparation),
        "normalized_max_abs": normalized_max,
        "forward_max_abs": 0,
        "gradient_max_abs": gradient_max,
        "one_update_weight_max_abs": weight_max,
        "tail_batch_sizes": list(map(len, schedule)),
        "resume_updates": 10,
        "resume_strategy": "10 continuous versus 5 then resume to 10 in fresh process",
        "compared_states": [
            "model",
            "optimizer",
            "stream",
            "history",
            "python_rng",
            "numpy_rng",
            "torch_rng",
            "mps_rng",
        ],
        "tensor_comparisons": differences,
        "continuous": continuous,
        "resumed": resumed,
    }
    (root / "verification.json").write_text(json.dumps(report, indent=2))
    print(
        json.dumps(
            {
                k: v
                for k, v in report.items()
                if k not in ["continuous", "resumed", "tensor_comparisons"]
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--source", required=True)
    args = parser.parse_args()
    main(args.root, args.source)
