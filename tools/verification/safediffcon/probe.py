"""在独立进程中执行原版准入探针；不把小网络诊断当成论文复现。

原版顶层导入名相互冲突，因此每个调用只导入一个案例。全部源码来自已固定
快照；路径连接只在内存中设置，不编辑快照和外部原仓库。
"""

import argparse
import importlib.metadata
import json
import os
import sys
import time
import traceback
from pathlib import Path


def burgers_probe(snapshot: Path, dataset: Path) -> dict:
    """执行原数值求解器，并真实实例化后训练/推理类定位启动故障。"""
    import h5py
    import numpy as np
    import torch

    sys.path.insert(0, str(snapshot / "1D"))
    os.environ["ACCELERATE_USE_CPU"] = "true"
    from accelerate.state import AcceleratorState
    from configs.inference_config import InferenceConfig
    from configs.posttrain_config import PostTrainConfig
    from data.burgers import BurgersDataset
    from data.generate_burgers import burgers_numeric_solve_free
    from inference.inference_ft import InferenceFT
    from posttrain.post_train import PostTrainPipeline
    from utils.common import build_model, set_seed

    with h5py.File(dataset / "burgers_test.h5", "r") as source:
        states = torch.tensor(source["test"]["pde_11-128"][:], dtype=torch.float32)
        controls = torch.tensor(source["test"]["pde_11-128_f"][:], dtype=torch.float32)
    torch.set_num_threads(4)
    start = time.monotonic()
    response = burgers_numeric_solve_free(states[:, 0], controls, visc=0.01, T=1, dt=1e-4, num_t=10)
    response = response.cpu()
    report = {
        "solver": {
            "samples": len(states),
            "seconds": time.monotonic() - start,
            "max_abs": float((response - states).abs().max()),
            "finite": bool(torch.isfinite(response).all()),
        },
        "constructors": {},
        "scope": "solver replay and tiny model constructor diagnosis",
    }
    for name, cls, base in (
        ("posttrain", PostTrainPipeline, PostTrainConfig),
        ("inference", InferenceFT, InferenceConfig),
    ):

        class LocalConfig(base):
            @property
            def datasets_dir(self):
                return str(dataset.parent)

        config = LocalConfig(tuning_id="admission", dataset=dataset.name, device="cpu", dim=8)
        set_seed(42)
        data = BurgersDataset(
            root_path=str(dataset.parent), dataset=dataset.name, split="test", config=config
        )
        model = build_model(config, data)
        AcceleratorState._reset_state(reset_partial_state=True)
        try:
            pipeline = cls(config, model, mixed_precision_type="no")
            report["constructors"][name] = {"status": "passed", "steps": pipeline.step}
        except Exception as error:  # noqa: BLE001 - 探针须记录原程序任何失败及完整堆栈
            report["constructors"][name] = {
                "status": "failed",
                "type": type(error).__name__,
                "error": str(error),
                "traceback": traceback.format_exc(),
            }
        del model, data
    report["solver"]["matches_dataset"] = bool(
        np.isclose(report["solver"]["max_abs"], 0, atol=2e-6)
    )
    return report


def kstar_probe(snapshot: Path, request: Path, output: Path) -> dict:
    """以发布模型回放原控制，保存完整响应与逐场差值。"""
    import numpy as np

    sys.path.insert(0, str(snapshot / "tokamak"))
    # 原模块按 argv[0] 寻找其模型资源，仅修正进程定位，不改计算。
    sys.argv[0] = str(snapshot / "tokamak" / "kstar_solver.py")
    import kstar_solver

    values = np.load(request, allow_pickle=False)
    actions, expected = values["actions"], values["outputs"]
    responses, timings = [], []
    for action in actions:
        start = time.monotonic()
        solver = kstar_solver.KSTARSolver(random_seed=0)
        response = solver.simulate(action)
        timings.append(time.monotonic() - start)
        responses.append(response)
    responses = np.asarray(responses)
    output.parent.mkdir(parents=True, exist_ok=True)
    np.save(output.with_suffix(".npy"), responses, allow_pickle=False)
    delta = responses - expected
    return {
        "samples": len(actions),
        "seconds_per_sample": timings,
        "shape": list(responses.shape),
        "finite": bool(np.isfinite(responses).all()),
        "max_abs_by_field": np.abs(delta).max(axis=(0, 1)).tolist(),
        "rtol_1e4_atol_1e6_match": bool(np.allclose(responses, expected, rtol=1e-4, atol=1e-6)),
        "q95_decisions_identical": bool(
            np.array_equal(responses[:, :, 4] < 4.98, expected[:, :, 4] < 4.98)
        ),
    }


def main() -> int:
    """将成功与失败均写入明确诊断记录。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case", choices=("burgers", "kstar"))
    parser.add_argument("--snapshot", type=Path, required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("不覆盖已有诊断证据")
    report = {
        "status": "running",
        "python": sys.version,
        "packages": {d.metadata["Name"]: d.version for d in importlib.metadata.distributions()},
    }
    try:
        if args.case == "burgers":
            report["result"] = burgers_probe(args.snapshot, args.input)
            failures = any(
                x["status"] == "failed" for x in report["result"]["constructors"].values()
            )
            solver_ok = report["result"]["solver"]["matches_dataset"]
            report["status"] = (
                "source_blocked" if failures else ("passed" if solver_ok else "mismatch")
            )
        else:
            report["result"] = kstar_probe(args.snapshot, args.input, args.output)
            report["status"] = (
                "passed" if report["result"]["rtol_1e4_atol_1e6_match"] else "mismatch"
            )
    except Exception as error:  # noqa: BLE001 - 子进程入口把失败交付给调用方
        report.update(status="failed", error=str(error), traceback=traceback.format_exc())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False))
    print(
        json.dumps(
            {k: v for k, v in report.items() if k != "packages"}, ensure_ascii=False, indent=2
        )
    )
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
