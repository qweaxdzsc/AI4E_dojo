"""原 Burgers Torch 字典的只读适配与代表轨迹划分校验。"""

import json
from pathlib import Path

import numpy as np
import torch

from ai4e_core.abilities.data.save.array_manifest import digest


def read(options: dict) -> tuple[dict, dict]:
    """按冻结来源摘要和索引读取；重复半区不能再次成为独立样本。"""
    protocol = json.loads(Path(options["protocol"]).read_text())
    indices = json.loads(Path(options["indices"]).read_text())
    if set(indices) != {"train", "validation", "test"}:
        raise ValueError("划分须包含 train/validation/test")
    for split, ids in indices.items():
        limit = 4000 if split == "test" else 20000
        if (
            not ids
            or len(ids) != len(set(ids))
            or any(type(i) is not int or not 0 <= i < limit for i in ids)
        ):
            raise ValueError("划分含空集、重复或非代表索引")
    if set(indices["train"]) & set(indices["validation"]):
        raise ValueError("训练与验证轨迹泄漏")
    raw, fingerprints = {}, {}
    for split in ("train", "test"):
        item = protocol["sources"][split]
        filename = (Path(options["protocol"]).resolve().parent / item["file"]).resolve()
        fingerprint = digest(filename)
        if fingerprint != item["sha256"]:
            raise ValueError("原始数据摘要变化")
        arrays = torch.load(filename, map_location="cpu", mmap=True, weights_only=True)
        if arrays["u"].shape[1:] != (81, 120) or arrays["f"].shape[1:] != (80, 120):
            raise ValueError("基础 Burgers 数据形状不兼容")
        raw[split] = arrays
        fingerprints[split] = fingerprint
    selected = {}
    for split, ids in indices.items():
        source = raw["test" if split == "test" else "train"]
        selected[split] = {
            "u": source["u"][ids].numpy(),
            "f": source["f"][ids].numpy(),
            "ids": np.array(ids, dtype=np.int64),
        }
    return selected, {
        "source_sha256": fingerprints,
        "indices_sha256": digest(options["indices"]),
        "case": "burgers-base",
        "units": {"u": "source units", "f": "source units"},
        "axes": ["sample", "time", "x"],
        "version": 1,
    }
