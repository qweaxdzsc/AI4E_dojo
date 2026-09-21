"""物理张量公开视图：具名域和样本条件与文件布局解耦。"""

from copy import deepcopy
from pathlib import Path

import torch

from ai4e_core.abilities.data.validate.fingerprint import fingerprint

from .manifest import ManifestIndex


class PhysicalView:
    """复用 PT 清单；没有来源 ID 的旧产物显式使用产物行身份。"""

    def __init__(self, path: str | Path, *, layout: dict | None = None):
        path = Path(path)
        self._index = ManifestIndex(path / "manifest.json" if path.is_dir() else path)
        description = self._index.describe()
        if description["state"] != "physical":
            raise ValueError("公共物理视图拒绝已归一化张量，请先恢复物理数据")
        self._layout = deepcopy(description.get("physical_layout") or layout)
        if not self._layout or not self._layout.get("domains"):
            raise ValueError("物理视图缺少域和字段声明")
        self.partitions = deepcopy(self._index.partitions)

    def remap_partitions(self, partitions) -> None:
        """套用准备阶段的新划分，同步公开分片名单与内部索引。"""
        self._index.remap_partitions(partitions)
        self.partitions = deepcopy(self._index.partitions)

    def describe(self) -> dict:
        """返回布局和持久引用，统计相对路径按清单位置解释。"""
        stats = deepcopy(self._index.describe().get("statistics"))
        if isinstance(stats, dict) and stats.get("path"):
            path = Path(stats["path"])
            stats["path"] = str(path if path.is_absolute() else self._index.path.parent / path)
        return {
            "reference": str(self._index.path.resolve()),
            "state": "physical",
            "layout": deepcopy(self._layout),
            "statistics": stats,
            "partitions": deepcopy(self.partitions),
        }

    def content_digest(self) -> str:
        """内容和声明共同标识物理数据，模型选择不参与。"""
        return fingerprint({"data": self._index.content_digest(), "layout": self._layout})

    def read(self, partition: str, index: int = 0, *, fields=None, selection=None) -> dict:
        """先校验完整样本，再选择字段；点选择由准备能力逐域执行。"""
        if selection is not None:
            raise ValueError("物理样本点选择由准备能力逐域执行")
        values = self._index.read(partition, index)
        sample = self.partitions[partition][index]
        context = f"{partition}/{sample}"
        for name, value in values.items():
            if not isinstance(value, torch.Tensor) or not torch.isfinite(value).all():
                raise ValueError(f"{context}/{name}: 非有限或非张量字段")

        def required(name):
            if name not in values:
                raise ValueError(f"{context}/{name}: 缺少声明字段")
            return values[name]

        record = self._index.records[(partition, sample)]
        identity_mapping = {}
        if record.get("identity_assets"):
            import json

            root = Path(record["path"])
            if not root.is_absolute():
                root = self._index.path.parent / root
            identity_mapping = json.loads((root / record["identity_assets"][0]).read_text())
        domains = {}
        for domain, declaration in self._layout["domains"].items():
            position = declaration["position"]
            points = required(position)
            if points.ndim != 2 or points.shape[1] != 3 or len(points) == 0:
                raise ValueError(f"{context}/{domain}/{position}: 坐标须为非空 N×3")
            for name in declaration.get("fields", {}).values():
                value = required(name)
                if value.ndim not in (1, 2) or len(value) != len(points):
                    raise ValueError(f"{context}/{domain}/{name}: 点字段行数或维度不一致")
                if value.ndim == 1:
                    values[name] = value[:, None]
            id_field = declaration.get("ids")
            identity_ref = record.get("field_aliases", {}).get(position, position)
            identity_record = identity_mapping.get(identity_ref)
            ids = (
                required(id_field)
                if id_field
                else (
                    torch.tensor(identity_record["entity_ids"], dtype=torch.int64)
                    if identity_record
                    else torch.arange(len(points))
                )
            )
            if (
                ids.ndim != 1
                or ids.dtype != torch.int64
                or len(ids) != len(points)
                or len(ids.unique()) != len(ids)
                or (ids < 0).any()
            ):
                raise ValueError(f"{context}/{domain}: 实体身份不合法")
            domains[domain] = {
                "position": position,
                "fields": deepcopy(declaration.get("fields", {})),
                "ids": ids,
                "identity_basis": "source" if id_field or identity_record else "artifact",
                "topology": deepcopy(record.get("topology", {}).get(domain)),
                "mesh": (
                    str(self._index.resolve_asset(partition, index, mesh_name))
                    if (mesh_name := (record.get("meshes") or {}).get(domain))
                    else None
                ),
            }
        conditions = {}
        for name, width in self._layout.get("conditions", {}).items():
            value = required(name)
            if value.numel() != width:
                raise ValueError(f"{context}/{name}: 样本条件维度不一致")
            conditions[name] = value.reshape(1, width)
        selected = values if fields is None else {k: required(k) for k in fields}
        return {
            "identity": {
                "sample": sample,
                "partition": partition,
                "index": index,
                "source": deepcopy(record.get("source")),
            },
            "fields": selected,
            "domains": domains,
            "conditions": conditions,
        }
