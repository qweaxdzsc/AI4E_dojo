"""已提交数据清单索引：只解析一次元数据，张量按样本读取。"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
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

    def remap_partitions(self, partitions: Mapping[str, Sequence[str]]) -> None:
        """按样本名确定性重挂分片；张量路径不变，空分片不进入索引。

        目标分片优先使用同名来源；``eval`` 与历史 ``validation`` 互为
        别名。没有精确来源时只允许唯一候选跨分片移动，避免同名多来源
        因清单顺序不同而静默选错物理样本。
        """
        by_name: dict[str, list[dict]] = {}
        for (_partition, sample), record in self.records.items():
            by_name.setdefault(sample, []).append(record)
        rebuilt: dict[tuple[str, str], dict] = {}
        remapped: dict[str, list[str]] = {}
        for name, samples in partitions.items():
            kept: list[str] = []
            for sample in samples:
                identity = str(sample)
                candidates = by_name.get(identity, [])
                aliases = {"eval": "validation", "validation": "eval"}
                record = next(
                    (item for item in candidates if item.get("partition") == name),
                    None,
                )
                if record is None and str(name) in aliases:
                    alias = aliases[str(name)]
                    record = next(
                        (item for item in candidates if item.get("partition") == alias),
                        None,
                    )
                if record is None and len(candidates) == 1:
                    record = candidates[0]
                if not candidates:
                    raise ValueError(f"重划分片找不到样本 {identity}")
                if record is None:
                    sources = sorted(str(item.get("partition")) for item in candidates)
                    raise ValueError(
                        f"重划分片样本 {identity} 在目标 {name} 存在歧义，候选来源: {sources}"
                    )
                rebuilt[(str(name), identity)] = record
                kept.append(identity)
            if kept:
                remapped[str(name)] = kept
        self.records = rebuilt
        self.partitions = remapped

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
        flattened = {}

        def check(name, value, spec):
            if isinstance(value, dict):
                if set(value) != set(spec.get("members", {})):
                    raise ValueError(f"字段成员与清单不一致: {sample}/{name}")
                for member, tensor in value.items():
                    check(name + "/" + member, tensor, spec["members"][member])
            else:
                if (
                    spec["state"] != self.manifest["state"]
                    or list(value.shape) != spec["shape"]
                    or str(value.dtype) != spec["dtype"]
                ):
                    raise ValueError(f"字段与清单不一致: {sample}/{name}")
                flattened[name] = value

        for name, value in fields.items():
            check(name, value, record["fields"][name])
        fields = flattened
        for alias, reference in record.get("field_aliases", {}).items():
            if alias in fields or reference not in fields:
                raise ValueError(f"字段别名冲突或来源缺失: {alias}")
            fields[alias] = fields[reference]
        selected = fields if requested is None else {key: fields[key] for key in requested}
        return (
            selected
            if selection is None
            else {key: value[selection] for key, value in selected.items()}
        )

    def resolve_asset(self, partition: str, index: int, name: str) -> Path:
        """解析样本清单显式声明的资产，拒绝未登记文件和路径越界。

        ``name`` 可以是 ``assets`` 中的文件名，也可以是 ``meshes`` 中的
        逻辑网格名。调用方不能借此接口遍历样本目录或读取历史残留文件。
        """
        samples = self.partitions.get(partition, [])
        if index < 0 or index >= len(samples):
            raise IndexError(f"分片 {partition} 没有第 {index} 个样本")
        record = self.records[(partition, samples[index])]
        meshes = record.get("meshes") or {}
        filename = meshes.get(name, name)
        declared = set(record.get("assets") or ()) | set(meshes.values())
        if filename not in declared or Path(filename).name != filename:
            raise ValueError(f"样本资产未声明或路径非法: {name}")
        root = Path(record["path"])
        if not root.is_absolute():
            root = self.path.parent / root
        target = root / filename
        if not target.is_file() or not target.resolve().is_relative_to(root.resolve()):
            raise FileNotFoundError(f"样本资产不存在或越出样本目录: {target}")
        return target.resolve()

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
                target = root / filename
                files = (
                    sorted(p for p in target.rglob("*") if p.is_file())
                    if target.is_dir()
                    else [target]
                )
                for path in files:
                    if target.is_dir():
                        hasher.update(path.relative_to(target).as_posix().encode())
                    with path.open("rb") as stream:
                        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                            hasher.update(chunk)
            covered = set(record["filemap"].values())
            asset_names = (
                set(record.get("assets", []))
                | set(record.get("identity_assets", []))
                | set((record.get("meshes") or {}).values())
            )
            for filename in sorted(asset_names):
                if filename in covered:
                    continue
                if Path(filename).name != filename:
                    raise ValueError("样本资产路径非法")
                hasher.update(filename.encode())
                with (root / filename).open("rb") as stream:
                    for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                        hasher.update(chunk)
        return hasher.hexdigest()
