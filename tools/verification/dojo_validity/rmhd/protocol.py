"""冻结科学参数和主控私有整轨迹分片；正式材料只复制允许字段。"""

import uuid
from pathlib import Path

import numpy as np

from ..io import digest, read_json, write_json

FIELDS = ("Psi", "u", "zj", "omega", "rho", "T")
STARTS = (0, 80, 161)
SCIENTIFIC = {
    "version": "jorek-rmhd-v1",
    "fields": FIELDS,
    "shape": [211, 100, 100],
    "history": 10,
    "future": 40,
    "block": 5,
    "seed": 42,
    "epochs": 500,
    "batch_size": 16,
    "learning_rate": 0.001,
    "optimizer": "Adam",
    "device": "mps",
    "dtype": "float32",
    "cpu_threads": 6,
    "validation_every": 10,
    "evaluation_starts": STARTS,
    "parameter_count": 495998,
    "latency_limit_seconds": 0.050,
    "normalization": "train_all_points_population_float64_std_floor_1e-12",
    "sampling": "PCG64(42); each epoch integers(0,162,size=70), then permutation(70)",
    "selection": "round_00_to_05_validation_only_before_any_hidden_evaluation",
}


def prepare_private(base, data_root):
    """创建仅主控访问的分片与预实验目录，不创建组会话或派生训练数据。"""
    data_root = Path(data_root).resolve()
    check = read_json(data_root / "data-inspection.json")
    if not check.get("complete") or check.get("errors") or len(check["samples"]) != 100:
        raise ValueError("原始数据未完整通过100轨迹核验")
    samples = sorted(check["samples"], key=lambda x: int(x["id"].removeprefix("jorek_run")))
    for key in ("trajectory_values_sha256", "initial10_values_sha256"):
        values = [s[key] for s in samples]
        if len(set(values)) != 100:
            raise ValueError(f"重复轨迹或历史输入: {key}")
    order = np.random.Generator(np.random.PCG64(42)).permutation(100)
    split = {}
    for name, indices in (
        ("train", order[:70]),
        ("validation", order[70:85]),
        ("test", order[85:]),
    ):
        split[name] = []
        for index in indices:
            sample = samples[int(index)]
            path = data_root / "raw" / f"{sample['id']}.h5"
            if digest(path) != sample["sha256"]:
                raise ValueError(f"来源摘要变化: {path.name}")
            split[name].append({"id": sample["id"], "path": str(path), "sha256": sample["sha256"]})
    root = Path(base).resolve() / "jorek-rmhd-comparison" / f"comparison-{uuid.uuid4()}"
    root.mkdir(parents=True, exist_ok=False)
    write_json(root / "scientific.json", SCIENTIFIC)
    write_json(root / "private-split.json", {"numpy_version": np.__version__, "splits": split})
    write_json(root / "state.json", {"phase": "prepared", "formal_sessions_started": False})
    return root


def gate(result):
    """真实完整 baseline 的数值、时间与延迟门槛；缺证据即不通过。"""
    checks = {
        "complete_500_epochs": result.get("epochs") == 500,
        "mps": result.get("device") == "mps",
        "training_under_1800s": 0 < result.get("training_seconds", float("inf")) < 1800,
        "latency_at_most_50ms": 0 < result.get("latency_p95_seconds", float("inf")) <= 0.050,
        "accuracy_improves": False,
        "rho_improves": False,
        "T_improves": False,
    }
    if "validation" in result and "persistence" in result:
        model, persistence = result["validation"], result["persistence"]
        checks["accuracy_improves"] = (
            model["mean_field_relative_l2"] < persistence["mean_field_relative_l2"]
        )
        for field in ("rho", "T"):
            checks[f"{field}_improves"] = (
                model["per_field_relative_l2"][field] < persistence["per_field_relative_l2"][field]
            )
    return {"passed": all(checks.values()), "checks": checks}
