"""主控唯一串行队列：准备、测速、参考/Dojo、扩展与重试共享组合总预算。"""

import argparse
import json
import time
from pathlib import Path

import torch
import yaml

from tools.verification.classic_networks.budget import BudgetLedger

REPOSITORY = Path(__file__).resolve().parents[3]
COMBINATIONS = (
    ("rsm-nasa", "rsm", "nasa_global"),
    ("rbf-nasa", "rbf", "nasa_global"),
    ("kriging-nasa", "kriging", "nasa_global"),
    ("lightgbm-nasa", "lightgbm", "nasa_global"),
    ("pod-rbf-double", "rbf", "double_cylinder_pod"),
    ("pod-kriging-double", "kriging", "double_cylinder_pod"),
    ("deeponet-darcy", "deeponet", "darcy"),
    ("fno-darcy", "fno", "darcy"),
    ("fno-double", "fno", "double_cylinder"),
    ("deeponet-shape", "deeponet", "shapenet_volume"),
    ("fno-shape", "fno", "shapenet_volume"),
)


def write(path, value):
    """验证器自身记录位于实验根，不绕过框架writer写run目录。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2))


def prepare(root, classic, nasa_train, nasa_test):
    """NASA属性物化和POD拟合只执行一次；共享耗时按相关组合等分。"""
    from ai4e_contrib.application.surrogate_modeling.preparation import (
        prepare_nasa,
        prepare_pod_data,
    )

    ledger = BudgetLedger(root / "budget")
    output = root / "evidence/preparation.json"
    sources = json.loads(Path(classic).read_text())
    record = (
        json.loads(output.read_text())
        if output.exists()
        else {key: value["prepared"] for key, value in sources.items()}
    )
    for case, combo, others in (
        ("nasa_global", "rsm-nasa", ["rbf-nasa", "kriging-nasa", "lightgbm-nasa"]),
        ("double_cylinder_pod", "pod-rbf-double", ["pod-kriging-double"]),
    ):
        if case in record:
            continue
        start = time.monotonic()
        with ledger.measure(combo, "shared-preparation-owner", training=True):
            directory = root / "shared" / (case + "-" + str(time.time_ns()))
            if case == "nasa_global":
                record[case] = prepare_nasa(nasa_train, nasa_test, directory)
            else:
                record[case] = prepare_pod_data(record["double_cylinder"], directory, rank=2)
        elapsed = time.monotonic() - start
        # 保守完整计入每个消费者，比平均分摊严格；不重复声称实际总计算。
        for other in others:
            ledger.record_charge(
                other,
                "shared-preparation-conservative",
                elapsed,
                details={"owner": combo, "actual_once": True},
            )
        write(output, record)
    return record


def operator_configuration(family, case, prepared, root, physical_weight=0):
    """冻结小模型配置；Shape传感器为参考格索引，并携带各例物理坐标。"""
    cfg = yaml.safe_load(
        (REPOSITORY / "recipes/operator_learning" / case / "config.yaml").read_text()
    )
    cfg["model"]["family"] = family
    if family == "deeponet":
        cfg["model"]["parameters"] = {
            "latent_dim": 16,
            "sensor_stride": 8,
            "branch_hidden": [32, 32],
            "trunk_hidden": [32, 32],
        }
    cfg["inputs"]["train"]["preparation"] = str(prepared)
    cfg["inputs"]["infer"]["preparation"] = str(prepared)
    cfg["train"]["physical_weight"] = physical_weight
    cfg["verification"] = {"reference_cache": str(root / "cache/upstream")}
    return cfg


def execute(root, combo, *, updates=100, phase="formal", physical_weight=0):
    """一次仅一个组合；失败保留结果与累计收费，不抹去重试历史。"""
    family, case = next((f, c) for name, f, c in COMBINATIONS if name == combo)
    ledger = BudgetLedger(root / "budget")
    prepared = json.loads((root / "evidence/preparation.json").read_text())[case]
    output = root / "runs" / combo / (phase + "-" + str(time.time_ns()))
    start = time.monotonic()
    result = {"status": "failed", "output": str(output), "phase": phase}
    try:
        with ledger.measure(combo, phase, training=True):
            deadline = time.monotonic() + ledger.remaining(combo) - 15
            if family in {"deeponet", "fno"}:
                from .serial_operators import run_combo

                cfg = operator_configuration(family, case, prepared, root, physical_weight)
                detail = run_combo(cfg, output, deadline=deadline, updates=updates)
            else:
                from .serial_classical import run_classical

                detail = run_classical(family, prepared, output, deadline)
            result.update(status="passed", result=detail)
    except BaseException as exc:
        result["error"] = repr(exc)
        raise
    finally:
        result["seconds"] = time.monotonic() - start
        record = root / "evidence" / f"{combo}-{phase}-{time.time_ns()}.json"
        write(record, result)
        print(
            json.dumps(
                {
                    "combo": combo,
                    "phase": phase,
                    "status": result["status"],
                    "seconds": result["seconds"],
                    "record": str(record),
                }
            ),
            flush=True,
        )
    return result


def main():
    """准备/单项/统一顺序入口，外部包环境与设备来源另由验收记录核验。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--combo", choices=[item[0] for item in COMBINATIONS])
    parser.add_argument("--updates", type=int, default=100)
    parser.add_argument("--phase", default="formal")
    parser.add_argument("--physical-weight", type=float, default=0)
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--classic-preparation")
    parser.add_argument("--nasa-train")
    parser.add_argument("--nasa-test")
    args = parser.parse_args()
    torch.set_num_threads(2)
    root = args.root.resolve()
    if args.prepare:
        prepare(root, args.classic_preparation, args.nasa_train, args.nasa_test)
    else:
        for combo, _, _ in COMBINATIONS:
            if args.combo is None or args.combo == combo:
                execute(
                    root,
                    combo,
                    updates=args.updates,
                    phase=args.phase,
                    physical_weight=args.physical_weight,
                )


if __name__ == "__main__":
    main()
