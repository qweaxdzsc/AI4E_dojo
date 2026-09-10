"""已提交数据清单索引：只解析一次元数据，张量按样本读取。"""

from __future__ import annotations

import json
from pathlib import Path

from ai4e_core.abilities.data.save.store import load_named_tensors


class ManifestIndex:
    """校验物理清单并建立稳定的分片与样本身份索引。"""

    def __init__(self, path: str | Path):
        """读取清单元数据，不预加载任何场张量。"""
        self.path = Path(path)
        self.manifest = json.loads(self.path.read_text())
        if self.manifest.get("version") != 1 or self.manifest.get("state") not in {
            "physical",
            "normalized",
        }:
            raise ValueError("当前读盘仅支持 version=1 的物理或归一化数据清单")
        self.partitions = self.manifest["partitions"]
        self.records = {}
        for record in self.manifest["samples"]:
            key = (record["partition"], record["sample"])
            if key in self.records:
                raise ValueError(f"清单重复样本身份: {key}")
            self.records[key] = record
        for partition, samples in self.partitions.items():
            if len(samples) != len(set(samples)):
                raise ValueError(f"分片包含重复样本: {partition}")
            for sample in samples:
                record = self.records.get((partition, sample))
                if record is None or not record.get("written"):
                    raise ValueError(f"清单没有唯一已提交样本: {sample}")

    def read(self, partition: str, index: int = 0, *, fields=None, selection=None):
        """读取指定样本，校验每个字段的空间状态、形状与类型。"""
        samples = self.partitions.get(partition, [])
        if index < 0 or index >= len(samples):
            raise IndexError(f"分片 {partition} 没有第 {index} 个样本")
        sample = samples[index]
        record = self.records[(partition, sample)]
        directory = Path(record["path"])
        if not directory.is_absolute():
            directory = self.path.parent / directory
        requested = fields
        fields = load_named_tensors(directory, record["filemap"])
        for name, value in fields.items():
            spec = record["fields"][name]
            if (
                spec["state"] != self.manifest["state"]
                or list(value.shape) != spec["shape"]
                or str(value.dtype) != spec["dtype"]
            ):
                raise ValueError(f"字段与清单不一致: {sample}/{name}")
        selected = fields if requested is None else {key: fields[key] for key in requested}
        return (
            selected
            if selection is None
            else {key: value[selection] for key, value in selected.items()}
        )

    def describe(self):
        """返回已发布清单的结构声明。"""
        return self.manifest

    def content_digest(self):
        """逐文件摘要，维持既有准备身份的精确算法。"""
        import hashlib

        hasher = hashlib.sha256(json.dumps(self.manifest, sort_keys=True).encode())
        for identity, record in sorted(self.records.items()):
            hasher.update(json.dumps(identity).encode())
            root = Path(record["path"])
            if not root.is_absolute():
                root = self.path.parent / root
            for name, filename in sorted(record["filemap"].items()):
                hasher.update(name.encode())
                with (root / filename).open("rb") as stream:
                    for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                        hasher.update(chunk)
        return hasher.hexdigest()
