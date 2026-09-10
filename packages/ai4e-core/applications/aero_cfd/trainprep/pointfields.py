"""逐点监督准备：冻结物理数据，按样本训练、按全部分块验证。"""

import json
import random
from pathlib import Path

import numpy as np
import torch

from ai4e_core.abilities.data.validate.fingerprint import fingerprint
from ai4e_core.abilities.transform.pointfields import FieldNormalization
from ai4e_core.base.events import sample_context

__all__ = ["FieldNormalization", "PointDataset", "collate", "features", "open_preparation"]


def features(raw, normalization):
    """坐标、法向和广播工况按有序输入契约拼接。"""
    conditions = normalization.apply("conditions", raw["conditions"])
    repeated = np.broadcast_to(conditions, (len(raw["points"]), len(conditions)))
    return np.ascontiguousarray(
        np.concatenate((raw["points"], raw["normals"], repeated), axis=1).astype(np.float32)
    )


class PointDataset(torch.utils.data.Dataset):
    """训练一次访问一个样本；验证每个访问对应一个完整分块。"""

    def __init__(self, view, normalization, split, *, training=False):
        self.chunk_count = int(view.describe()["chunk_count"])
        self.view, self.normalization, self.split, self.training = (
            view,
            normalization,
            split,
            training,
        )

    def __len__(self):
        return len(self.view.partitions[self.split]) * (1 if self.training else self.chunk_count)

    def __getitem__(self, index):
        """先按参考顺序消耗 chunk/offset 随机数，再读取对齐字段。"""
        item = index if self.training else index // self.chunk_count
        part = random.randrange(self.chunk_count) if self.training else index % self.chunk_count
        offset = random.randrange(4) if self.training else 0
        sample = self.view.partitions[self.split][item]
        with sample_context(
            "点场输入准备",
            [{"sample_id": sample, "index": item, "chunk": part, "partition": self.split}],
        ):
            raw = self.view.read(self.split, item, selection=part)
            x = features(raw, self.normalization)
            y = self.normalization.apply("labels", raw["labels"])
            chosen = slice(offset, None, 4) if self.training else slice(None)
            if len(x[chosen]) == 0:
                raise ValueError(f"{sample}/{part}: 训练抽稀后没有点")
            return {
                "inputs": {"features": torch.from_numpy(x[chosen])},
                "targets": {"fields": torch.from_numpy(y[chosen])},
                "physical": torch.from_numpy(raw["labels"][chosen]),
                "point_ids": torch.from_numpy(raw["point_ids"][chosen]),
                "metadata": {
                    "sample": sample,
                    "index": item,
                    "chunk": part,
                    "offset": offset,
                    "partition": self.split,
                },
            }


def collate(items):
    """参考批次严格为一；完整保留计算项身份。"""
    if len(items) != 1:
        raise ValueError("逐块参考流程当前只支持 batch_size=1")
    item = items[0]
    return {
        "inputs": {k: v[None] for k, v in item["inputs"].items()},
        "targets": {k: v[None] for k, v in item["targets"].items()},
        "physical": item["physical"][None],
        "point_ids": item["point_ids"][None],
        "metadata": [item["metadata"]],
    }


def open_preparation(config, component, reference=None, *, validate=True):
    """打开数据视图并验证冻结记录；内容变化不能靠旧文件名混过。"""
    path = (
        config["train"].get("manifest")
        or Path(config["paths"]["datasets"]["root"]) / "manifest.json"
    )
    previous = None
    if reference:
        reference_path = reference["preparation"] if isinstance(reference, dict) else reference
        previous = json.loads(Path(reference_path).read_text())
        if (
            config["train"].get("manifest")
            and Path(path).resolve() != Path(previous["manifest"]).resolve()
        ):
            raise ValueError("训练输入与准备清单冲突")
        path = previous["manifest"]
    view = component.View(path)
    normalization = FieldNormalization(view.describe()["statistics"])
    declaration = {
        "fields": view.describe()["fields"],
        "sampling": config["sampling"],
        "model": config["model"],
        "components": config["components"],
    }
    record = {
        "version": 1,
        "manifest": view.describe()["reference"],
        "dataset": view.content_digest(),
        "normalization": normalization.record,
        "declarations": declaration,
        "split_counts": {k: len(v) for k, v in view.partitions.items()},
    }
    record["digest"] = fingerprint(record)
    if previous and previous != record:
        raise ValueError("准备数据、模型、组件或变换声明已变化")
    if validate:
        for split, names in view.partitions.items():
            if not names:
                raise ValueError(f"分片为空: {split}")
            for index in range(len(names)):
                for part in range(view.describe()["chunk_count"]):
                    with sample_context(
                        "准备校验",
                        [
                            {
                                "sample_id": names[index],
                                "index": index,
                                "partition": split,
                                "chunk": part,
                            }
                        ],
                    ):
                        view.read(split, index, selection=part)
    return view, normalization, record
