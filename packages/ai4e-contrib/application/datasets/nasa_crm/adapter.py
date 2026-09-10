"""NASA CRM HDF5 与 NPY 分块适配；不运行训练或批量前处理。"""

import hashlib
import json
from pathlib import Path

import h5py
import numpy as np

from ai4e_core.abilities.data.validate.fingerprint import file_fingerprint
from ai4e_core.abilities.sampling.stride import indices

from .constants import (
    AREA_FIELD,
    CONDITION_FIELDS,
    COORDINATE_FIELDS,
    GLOBAL_TARGET_FIELDS,
    INPUT_FIELDS,
    LABEL_FIELDS,
    NORMAL_FIELDS,
    REQUIRED_ATTRIBUTES,
    REQUIRED_DATASETS,
)


def manifest_digest(manifest):
    """保持参考 manifest 的稳定 JSON 摘要算法。"""
    value = {k: v for k, v in manifest.items() if k != "fingerprint"}
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def inspect(path):
    """检查全部 group 的必需字段和共同点数，不读取场数组。"""
    path = Path(path)
    counts = set()
    with h5py.File(path, "r") as source:
        names = sorted(source.keys())
        if not names:
            raise ValueError(f"数据源为空: {path}")
        for name in names:
            group = source[name]
            missing = REQUIRED_DATASETS - set(group)
            attrs = REQUIRED_ATTRIBUTES - set(group.attrs)
            if missing or attrs:
                raise ValueError(f"{path}/{name}: 缺字段 {sorted(missing)}，工况 {sorted(attrs)}")
            shapes = {tuple(group[key].shape) for key in REQUIRED_DATASETS}
            if len(shapes) != 1:
                raise ValueError(f"{name}: 字段形状不一致")
            shape = next(iter(shapes))
            if len(shape) != 1 or shape[0] < 1:
                raise ValueError(f"{name}: 点字段必须为非空一维")
            counts.add(shape[0])
    if len(counts) != 1:
        raise ValueError("样本点数不一致")
    stat = path.stat()
    return {
        "path": str(path),
        "size_bytes": stat.st_size,
        "mtime_ns": stat.st_mtime_ns,
        "sample_count": len(names),
        "point_count": counts.pop(),
        "sample_ids": names,
    }


class RawDataset:
    """原始数据只在单样本读取期间打开；分片含明确的来源文件。"""

    def __init__(self, settings):
        self.settings = dict(settings)
        self.global_target_fields = GLOBAL_TARGET_FIELDS
        self.sources = {
            "training": inspect(settings["train_h5"]),
            "test": inspect(settings["test_h5"]),
        }
        if self.sources["training"]["point_count"] != self.sources["test"]["point_count"]:
            raise ValueError("训练与测试点数不一致")
        fraction = float(settings.get("validation_fraction", 0.2))
        if not 0 < fraction < 1:
            raise ValueError("验证比例必须在零和一之间")
        seed = int(settings.get("split_seed", 42))
        shuffled = (
            np.random.default_rng(seed).permutation(self.sources["training"]["sample_ids"]).tolist()
        )
        count = max(1, round(len(shuffled) * fraction))
        if count >= len(shuffled):
            raise ValueError("划分后训练集为空")
        self.partitions = {
            "train": sorted(shuffled[count:]),
            "validation": sorted(shuffled[:count]),
            "test": self.sources["test"]["sample_ids"],
        }
        self.point_count = self.sources["training"]["point_count"]
        self.chunk_count = int(settings.get("chunk_count", 20))
        if self.chunk_count < 1 or self.chunk_count > self.point_count:
            raise ValueError("分块数须为正且不能产生空块")

    def read(self, partition, index=0, *, fields=None, selection=None):
        """按稳定字段顺序读出点字段和样本工况。"""
        name = self.partitions[partition][index]
        source = self.sources["test" if partition == "test" else "training"]["path"]
        with h5py.File(source, "r") as stream:
            group = stream[name]
            result = {
                "points": np.column_stack([group[k][:] for k in COORDINATE_FIELDS]).astype(
                    np.float32
                ),
                "normals": np.column_stack([group[k][:] for k in NORMAL_FIELDS]).astype(np.float32),
                "area": np.asarray(group[AREA_FIELD][:], dtype=np.float32),
                "labels": np.column_stack([group[k][:] for k in LABEL_FIELDS]).astype(np.float32),
                "conditions": np.asarray(
                    [group.attrs[k] for k in CONDITION_FIELDS], dtype=np.float32
                ),
                "global_targets": np.asarray(
                    [group.attrs[k] for k in GLOBAL_TARGET_FIELDS], dtype=np.float64
                ),
            }
        for key, value in result.items():
            if not np.isfinite(value).all():
                raise ValueError(f"{name}/{key}: 非有限数值")
        if fields is not None:
            result = {key: result[key] for key in fields}
        return result

    def describe(self):
        """提供参考兼容数据清单的业务声明，不包含统计结果。"""
        return {
            "schema_version": 1,
            "fields": {
                "coordinates": list(COORDINATE_FIELDS),
                "normals": list(NORMAL_FIELDS),
                "conditions": list(CONDITION_FIELDS),
                "labels": list(LABEL_FIELDS),
                "area": AREA_FIELD,
            },
            "input_fields": list(INPUT_FIELDS),
            "input_dim": 12,
            "out_dim": 4,
            "chunk_count": self.chunk_count,
            "point_count": self.point_count,
            "split_seed": int(self.settings.get("split_seed", 42)),
            "validation_fraction": float(self.settings.get("validation_fraction", 0.2)),
            "splits": self.partitions,
            "sources": {
                k: {a: b for a, b in v.items() if a != "sample_ids"}
                for k, v in self.sources.items()
            },
        }

    def content_digest(self):
        """源内容与分片声明共同决定身份。"""
        return manifest_digest(
            {
                "source_hashes": {k: file_fingerprint(v["path"]) for k, v in self.sources.items()},
                "description": self.describe(),
            }
        )


class View:
    """参考 NPY 分块的只读视图，支持已有合法产物而不重写它。"""

    def __init__(self, path):
        path = Path(path)
        self.path = path / "manifest.json" if path.is_dir() else path
        self.root = self.path.parent
        self.manifest = json.loads(self.path.read_text())
        m = self.manifest
        if m.get("fingerprint") != manifest_digest(m):
            raise ValueError("Manifest fingerprint mismatch")
        if (
            tuple(m["fields"]["conditions"]) != CONDITION_FIELDS
            or tuple(m["fields"]["labels"]) != LABEL_FIELDS
        ):
            raise ValueError("工况或标签顺序不一致")
        if m.get("input_dim") != 12 or m.get("out_dim") != 4:
            raise ValueError("数据必须为 12 维输入与 4 维输出")
        if (
            tuple(m["fields"]["coordinates"]) != COORDINATE_FIELDS
            or tuple(m["fields"]["normals"]) != NORMAL_FIELDS
            or m["fields"]["area"] != AREA_FIELD
            or tuple(m["input_fields"]) != INPUT_FIELDS
        ):
            raise ValueError("坐标、法向、面积或模型输入字段顺序不一致")
        self.partitions = m["splits"]
        self.point_count, self.chunk_count = int(m["point_count"]), int(m["chunk_count"])
        if not 0 < self.chunk_count <= self.point_count:
            raise ValueError("分块规模不合法")
        if any(len(names) != len(set(names)) for names in self.partitions.values()):
            raise ValueError("同一分片样本身份重复")
        if set(self.partitions["train"]) & set(self.partitions["validation"]):
            raise ValueError("训练与验证分片重叠")
        for names in self.partitions.values():
            if any(
                not isinstance(name, str) or name in {"", ".", ".."} or Path(name).name != name
                for name in names
            ):
                raise ValueError("样本身份必须为单个目录名")

    def read(self, partition, index=0, *, fields=None, selection=None):
        """selection 是块下标；点字段携带原始点 ID，工况保持样本级。"""
        sample = self.partitions[partition][index]
        directory = self.root / partition / sample
        part = 0 if selection is None else int(selection)
        ids = indices(self.point_count, self.chunk_count, part)
        expected = {
            "points": (len(ids), 3),
            "normals": (len(ids), 3),
            "area": (len(ids),),
            "labels": (len(ids), 4),
        }
        chosen = tuple(expected) if fields is None else tuple(fields)
        result = {}
        for name in chosen:
            value = np.load(directory / f"{name}_part{part}.npy", allow_pickle=False)
            if (
                value.shape != expected[name]
                or value.dtype != np.float32
                or not np.isfinite(value).all()
            ):
                raise ValueError(f"{partition}/{sample}/{part}/{name}: 数组契约不符")
            result[name] = value
        conditions = np.load(directory / "conditions.npy", allow_pickle=False)
        if (
            conditions.shape != (6,)
            or conditions.dtype != np.float32
            or not np.isfinite(conditions).all()
        ):
            raise ValueError(f"{sample}: 工况契约不符")
        metadata = json.loads((directory / "metadata.json").read_text())
        if (
            metadata["sample_id"] != sample
            or metadata["split"] != partition
            or metadata["point_count"] != self.point_count
            or metadata["chunk_count"] != self.chunk_count
        ):
            raise ValueError(f"{sample}: 样本元数据不符")
        return {**result, "conditions": conditions, "metadata": metadata, "point_ids": ids}

    def describe(self):
        """返回完整数据声明，调用者不需要识别 NPY 文件名。"""
        return {**self.manifest, "reference": str(self.path.resolve())}

    def content_digest(self):
        """逐文件内容摘要，包含工况、元数据和全部块。"""
        digest = hashlib.sha256(json.dumps(self.manifest, sort_keys=True).encode())
        for split, names in sorted(self.partitions.items()):
            for name in names:
                directory = self.root / split / name
                files = [directory / "conditions.npy", directory / "metadata.json"]
                files += [
                    directory / f"{field}_part{part}.npy"
                    for part in range(self.chunk_count)
                    for field in ("points", "normals", "area", "labels")
                ]
                for path in files:
                    digest.update(str(path.relative_to(self.root)).encode())
                    digest.update(file_fingerprint(path).encode())
        return digest.hexdigest()
