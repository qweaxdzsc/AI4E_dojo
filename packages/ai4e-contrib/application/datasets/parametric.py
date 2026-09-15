"""参数化 PDE 的数据生成交接与读取；不依赖模型或训练器。"""

import importlib
import json
from pathlib import Path

import numpy as np
import torch

from ai4e_core.abilities.data.save.bundle import (
    digest,
    file_digest,
    load_bundle,
    save_bundle,
    save_json,
)
from ai4e_core.base.events import event

CASES = {
    "convection_diffusion": {"train": 40, "test": 1, "nx": 101, "nt": 101},
    "neumann_diffusion": {"train": 50, "test": 10, "nx": 128, "nt": 128},
    "advection": {"train": 100, "test": 30, "nx": 100, "nt": 100},
    "burgers": {"train": 100, "test": 20, "nx": 1000, "nt": 320},
    "diffusion_trapezoid": {"train": 10, "test": 10, "nx": 21, "ny": 21, "nt": 1001},
}


def component(case):
    """按明确案例名加载生成/真值模块，不猜测文件名。"""
    if case not in CASES:
        raise ValueError(f"未知 PDE 案例: {case}")
    return importlib.import_module(f"ai4e_contrib.application.datasets.{case}.generate")


def validate_sample(sample):
    """校验时空轴、场布局与实例参数；保留物理身份。"""
    axes = sample["axes"]
    names = sample["axis_names"]
    if names not in (["t", "x"], ["t", "eta", "xi"]):
        raise ValueError("未知物理数组轴顺序")
    for name in names:
        axis = axes[name]
        if axis.ndim != 1 or len(axis) < 2 or not torch.isfinite(axis).all():
            raise ValueError(f"{sample['id']}/{name}: 坐标轴无效")
        if not (axis[1:] > axis[:-1]).all():
            raise ValueError(f"{sample['id']}/{name}: 坐标必须严格递增")
    if tuple(sample["u"].shape) != tuple(len(axes[n]) for n in names):
        raise ValueError(f"{sample['id']}: u 与坐标轴不对齐")
    if not torch.isfinite(sample["u"]).all():
        raise ValueError(f"{sample['id']}: 真值非有限")
    if not all(np.isfinite(v) for v in sample["parameters"].values()):
        raise ValueError(f"{sample['id']}: 参数非有限")
    return sample


def generate_dataset(case, config):
    """独立生成到新目录，逐实例提交；完整清单仅在全部成功后发布。

    默认生成器以 train/test 两条独立随机流采样；案例可声明连续流协议。
    不启动训练。已有非空目录
    明确拒绝，避免覆盖后把旧完整清单误当成本次结果。
    """
    cfg = {**CASES[case], "seed": 42, **dict(config)}
    unknown = set(cfg) - set(CASES[case]) - {"seed", "output", "rtol", "atol", "parameters"}
    if unknown:
        raise ValueError(f"未知数据生成参数: {sorted(unknown)}")
    root = Path(cfg["output"]).expanduser().resolve()
    if root.exists() and any(root.iterdir()):
        raise FileExistsError(f"数据输出目录必须为空: {root}")
    for key in ("train", "test", "nx", "nt"):
        if not isinstance(cfg[key], int) or cfg[key] < (2 if key in {"nx", "nt"} else 1):
            raise ValueError(f"{key}: 数据规模无效")
    root.mkdir(parents=True, exist_ok=True)
    module = component(case)
    records = []
    specification = {k: v for k, v in cfg.items() if k != "output"}
    source = file_digest(module.__file__)
    save_json(
        root / "generation.json",
        {"case": case, "config": specification, "generator_sha256": source, "status": "running"},
    )
    try:
        streams = (
            module.parameter_streams(cfg)
            if hasattr(module, "parameter_streams")
            else (
                (split, np.random.default_rng(stream))
                for split, stream in zip(
                    ("train", "test"), np.random.SeedSequence(cfg["seed"]).spawn(2)
                )
            )
        )
        for split, rng in streams:
            for index in range(cfg[split]):
                identity = f"{split}-{index:05d}"
                sample = module.make_sample(rng, cfg, index=index, split=split)
                sample.update(id=identity, case=case)
                sample = validate_sample(sample)
                relative = f"{split}/{identity}.pt"
                save_bundle(root / relative, sample)
                records.append(
                    {
                        "id": identity,
                        "split": split,
                        "path": relative,
                        "sha256": file_digest(root / relative),
                    }
                )
                event("数据生成", "样本完成", 样本=identity, 案例=case)
    except Exception as exc:
        save_json(
            root / "generation.json",
            {
                "case": case,
                "config": specification,
                "status": "failed",
                "success": records,
                "error": str(exc),
            },
        )
        raise
    manifest = {
        "schema": 1,
        "case": case,
        "config": specification,
        "generator_sha256": source,
        "samples": records,
        "status": "complete",
    }
    manifest["content_id"] = digest(manifest)
    save_json(root / "manifest.json", manifest)
    save_json(
        root / "generation.json",
        {
            "case": case,
            "config": specification,
            "status": "complete",
            "content_id": manifest["content_id"],
        },
    )
    return str(root / "manifest.json")


class Dataset:
    """按冻结清单逐样本读取物理场，读取时检查内容摘要。"""

    def __init__(self, manifest):
        self.path = Path(manifest).resolve()
        self.manifest = json.loads(self.path.read_text())
        content = {k: v for k, v in self.manifest.items() if k != "content_id"}
        if (
            self.manifest.get("status") != "complete"
            or digest(content) != self.manifest["content_id"]
        ):
            raise ValueError("数据集不是完整有效清单")
        ids = [r["id"] for r in self.manifest["samples"]]
        if len(ids) != len(set(ids)) or not ids:
            raise ValueError("样本身份重复或为空")

    def records(self, split):
        """返回指定分片的有序身份清单，不自动替代空分片。"""
        records = [r for r in self.manifest["samples"] if r["split"] == split]
        if not records:
            raise ValueError(f"空数据分片: {split}")
        return records

    def read(self, record):
        """安全读回一个已登记样本并验证字段和身份。"""
        path = (self.path.parent / record["path"]).resolve()
        if not path.is_relative_to(self.path.parent) or file_digest(path) != record["sha256"]:
            raise ValueError(f"{record['id']}: 数据路径或内容摘要失效")
        sample = validate_sample(load_bundle(path))
        if sample["id"] != record["id"] or sample["case"] != self.manifest["case"]:
            raise ValueError("数据样本身份不一致")
        return sample


def tensor_sample(axes, values, parameters, bounds, *, mapping="identity"):
    """数值生成器的物理张量交接；统一双精度真值以便独立验证。"""
    return {
        "axis_names": list(axes),
        "axes": {k: torch.as_tensor(v.copy(), dtype=torch.float64) for k, v in axes.items()},
        "u": torch.as_tensor(values.copy(), dtype=torch.float64),
        "parameters": parameters,
        "bounds": bounds,
        "mapping": mapping,
    }
