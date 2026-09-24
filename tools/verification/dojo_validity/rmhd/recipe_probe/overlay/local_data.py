"""JOREK 发布包的字段适配；读取、统计、保存和校验复用公开能力。"""

import json
import shutil
import tarfile
from pathlib import Path

import numpy as np
import torch

from ai4e_core.abilities.data.save.array_manifest import read_arrays, save_arrays
from ai4e_core.abilities.data.save.arrays import save_json
from ai4e_core.abilities.data.source.array_read import read_array
from ai4e_core.abilities.data.stats.moments import accumulate_moments
from ai4e_core.abilities.data.validate.fingerprint import file_fingerprint
from ai4e_core.abilities.data.validate.trajectory import validate_layout, validate_pairing
from ai4e_core.abilities.transform.standardization import Standardization


def read_record(path):
    """读取本地 JSON 交接，数据数组另由摘要校验入口读取。"""
    return json.loads(Path(path).read_text())


class JorekSource:
    """每次读取一个已冻结 tar 成员，输出六场联合轨迹。"""

    def __init__(self, source, fields, output):
        self.source, self.fields, self.output = Path(source), fields, Path(output)

    def __call__(self, sample):
        split, entry = sample["split"], sample["entry"]
        scratch = self.output / (entry["id"] + ".h5")
        try:
            with tarfile.open(self.source / f"{split}.tar") as archive:
                member = archive.getmember(entry["file"])
                if not member.isfile():
                    raise ValueError("来源成员不是普通文件")
                with archive.extractfile(member) as src, scratch.open("wb") as dst:
                    shutil.copyfileobj(src, dst)
            if file_fingerprint(scratch) != entry["sha256"]:
                raise ValueError("原始成员内容变化")
            arrays = [read_array(scratch, key=field) for field in self.fields]
            if any(a.shape != (211, 100, 100) or a.dtype != np.float64 for a in arrays):
                raise ValueError("发布数组形状或精度改变")
            validate_pairing(
                [{"sample_ids": [entry["id"]], "time_indices": list(range(211))} for _ in arrays]
            )
            values = np.stack(arrays, axis=1)
            validate_layout(values.shape, ("T", "C", "R", "Z"))
            path = save_arrays(
                self.output / split / entry["id"],
                {"values": values},
                kind="rmhd-physical-v1",
                metadata={
                    "id": entry["id"],
                    "fields": self.fields,
                    "source_sha256": entry["sha256"],
                    "time_kind": "saved_frame_index",
                },
            )
            return {"id": entry["id"], "split": split, "manifest": path}
        finally:
            scratch.unlink(missing_ok=True)


def fit_normalization(records):
    """训练轨迹全时空总体 FP64 矩；验证不参与，保留 std floor。"""

    def arrays():
        for record in records:
            _, data = read_arrays(record["manifest"], kind="rmhd-physical-v1")
            yield np.moveaxis(data["values"], 1, -1).reshape(-1, 6)

    result = accumulate_moments(arrays())
    return {
        "mean": result["mean"].tolist(),
        "std": np.maximum(result["std"], 1e-12).tolist(),
        "count": result["count"],
        "dtype": "float64",
        "ddof": 0,
    }


class NormalizeSample:
    """按公开变换接口保存独立 FP32 训练缓存；原始物理量保留。"""

    def __init__(self, stats, output):
        self.transform = Standardization(
            tuple(stats["mean"]), tuple(stats["std"]), arithmetic="divide"
        )
        self.output = Path(output)

    def __call__(self, record):
        _, arrays = read_arrays(record["manifest"], kind="rmhd-physical-v1")
        values = torch.from_numpy(np.array(arrays["values"], dtype=np.float32))
        normalized = self.transform.apply(values.movedim(1, -1)).movedim(-1, 1).numpy()
        path = save_arrays(
            self.output / record["id"],
            {"values": normalized},
            kind="rmhd-normalized-v1",
            metadata={"physical": record["manifest"], "id": record["id"]},
        )
        return {**record, "manifest": path}


def save_preparation(output, physical, stats, normalized):
    """保存准备交接和来源引用，避免把缓存伪装成输入数据。"""
    path = Path(output) / "preparation.json"
    save_json(
        path,
        {
            "train": normalized,
            "validation": physical["validation"],
            "statistics": stats,
            "physical": physical,
        },
    )
    return str(path)
