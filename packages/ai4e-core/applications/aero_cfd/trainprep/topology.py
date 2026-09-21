"""平台 PT 与 VTKHDF 的拓扑绑定、身份校验和可重建缓存。"""

from __future__ import annotations

import hashlib
from copy import deepcopy
from pathlib import Path

import torch
from vtk.util.numpy_support import vtk_to_numpy

from ai4e_core.abilities.data.source.read import read_file
from ai4e_core.abilities.geometry.mesh_graph import induced_subgraph, vtk_cell_edges
from ai4e_core.abilities.sampling.graph import partition_with_halo
from ai4e_core.base.config import plain


class TopologyView:
    """为物理视图附加中立图拓扑；底层平台数据保持只读。"""

    def __init__(self, view, settings: dict, output: str | Path, sampling: dict | None = None):
        self.base = view
        self.settings = deepcopy(settings)
        self.sampling = deepcopy(sampling or {})
        self.output = Path(output)
        self.partitions = view.partitions
        self.digests: dict[str, str] = {}

    def remap_partitions(self, partitions) -> None:
        """把切片重挂委托给底层视图。"""
        self.base.remap_partitions(partitions)
        self.partitions = self.base.partitions

    def describe(self) -> dict:
        """保留物理视图说明并追加拓扑准备声明。"""
        return {**self.base.describe(), "topology": deepcopy(self.settings)}

    def content_digest(self) -> str:
        """平台数据摘要已覆盖 VTKHDF；设置另进入准备记录。"""
        return self.base.content_digest()

    def read(self, partition: str, index: int = 0, **kwargs) -> dict:
        """读取物理样本，并为已声明域附加图缓存内容。"""
        sample = self.base.read(partition, index, **kwargs)
        for domain, declaration in (self.settings.get("domains") or {}).items():
            if domain not in sample["domains"]:
                raise ValueError(f"拓扑声明引用未知域: {domain}")
            mesh_name = declaration.get("mesh", domain)
            mesh_path = sample["domains"][domain].get("mesh")
            if mesh_path is None:
                raise ValueError(
                    f"{partition}/{sample['identity']['sample']}/{domain}: 缺少网格资产"
                )
            if Path(mesh_path).stem != mesh_name and Path(mesh_path).name != mesh_name:
                raise ValueError(f"{domain}: 网格逻辑名与样本资产不一致")
            graph = self._load_or_build(sample, domain, Path(mesh_path))
            sample["domains"][domain]["graph"] = graph
        return sample

    def validate_all(self) -> None:
        """逐样本建立或核对缓存，使准备阶段尽早暴露身份错误。"""
        for partition, names in self.partitions.items():
            for index in range(len(names)):
                self.read(partition, index)

    def _load_or_build(self, sample: dict, domain: str, path: Path) -> dict:
        identity = f"{sample['identity']['partition']}/{sample['identity']['sample']}/{domain}"
        digest = topology_digest(path, sample["domains"][domain]["ids"])
        self.digests[identity] = digest
        target = self.output / digest[:2] / f"{digest}.pt"
        if target.is_file():
            cached = torch.load(target, map_location="cpu", weights_only=True)
            if cached.get("topology_digest") == digest:
                if self._bind_partitions(cached, domain):
                    _write_cache(target, cached)
                return cached
        graph = graph_from_vtkhdf(
            path,
            sample["fields"][sample["domains"][domain]["position"]],
            sample["domains"][domain]["ids"],
        )
        graph["topology_digest"] = digest
        self._bind_partitions(graph, domain)
        _write_cache(target, graph)
        return graph

    def _bind_partitions(self, graph: dict, domain: str) -> bool:
        """按当前运行采样预算补齐可重建分区缓存，不冻结进准备声明。"""
        changed = False
        cache = graph.setdefault("partitions", {})
        reusable = {
            _partition_key(record["settings"]): record["items"]
            for record in cache.values()
            if record.get("settings") and record.get("items")
        }
        roles = (self.sampling.get("domains") or {}).get(domain) or {}
        for role, value in roles.items():
            settings = _partition_settings(value)
            if settings is None:
                continue
            current = cache.get(role)
            if current and current.get("settings") == settings:
                continue
            key = _partition_key(settings)
            if key in reusable:
                cache[role] = {"settings": settings, "items": reusable[key]}
                changed = True
                continue
            items = partition_with_halo(
                graph["edge_index"],
                len(graph["source_ids"]),
                settings["core_nodes"],
                settings["halo_hops"],
            )
            cache[role] = {
                "settings": settings,
                "items": items,
            }
            reusable[key] = items
            changed = True
        return changed


def bind_topology(data, *, settings, output, sampling=None) -> object:
    """把平台网格及当前分区预算绑定到物理准备，并验证全部已声明样本。"""
    values = deepcopy(plain(settings))
    if not values.get("domains"):
        raise ValueError("trainprep.topology.domains 不能为空")
    data.view = TopologyView(data.view, values, output, plain(sampling or {}))
    data.topology = {"settings": values}
    data.view.validate_all()
    return data


def _partition_settings(value) -> dict | None:
    """只缓存通用核心块和 halo 参数；完整图不需要派生缓存。"""
    settings = plain(value or {})
    if settings.get("method", "full") != "core_halo":
        return None
    return {
        "method": "core_halo",
        "core_nodes": int(settings["core_nodes"]),
        "halo_hops": int(settings["halo_hops"]),
    }


def _partition_key(settings: dict) -> tuple[int, int]:
    """相同核心块和 halo 预算可跨训练、推理角色复用。"""
    return int(settings["core_nodes"]), int(settings["halo_hops"])


def _write_cache(target: Path, graph: dict) -> None:
    """原子更新可重建拓扑缓存。"""
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(".tmp")
    torch.save(graph, temporary)
    temporary.replace(target)


def topology_digest(path: Path, ids: torch.Tensor) -> str:
    """以完整 VTKHDF 字节和 PT 原点身份标识图缓存。"""
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(chunk)
    hasher.update(torch.as_tensor(ids, dtype=torch.int64).contiguous().numpy().tobytes())
    return hasher.hexdigest()


def graph_from_vtkhdf(path: Path, positions: torch.Tensor, source_ids: torch.Tensor) -> dict:
    """读取规范网格，按 PT 原点 ID 对齐坐标并构造诱导子图。"""
    mesh = read_file(path)
    point_ids = mesh.GetPointData().GetArray("ai4e_point_id")
    if point_ids is None:
        raise ValueError(f"{path}: VTKHDF 缺少 ai4e_point_id")
    vtk_ids = torch.from_numpy(vtk_to_numpy(point_ids).astype("int64", copy=True))
    if len(vtk_ids.unique()) != len(vtk_ids) or (vtk_ids < 0).any():
        raise ValueError(f"{path}: VTK 原点身份不合法")
    requested = torch.as_tensor(source_ids, dtype=torch.long)
    lookup = {int(value): index for index, value in enumerate(vtk_ids.tolist())}
    try:
        rows = torch.tensor([lookup[int(value)] for value in requested.tolist()], dtype=torch.long)
    except KeyError as exc:
        raise ValueError(f"{path}: PT 原点身份未出现在 VTKHDF") from exc
    mesh_points = torch.from_numpy(vtk_to_numpy(mesh.GetPoints().GetData()).copy()).to(positions)
    if positions.shape != mesh_points[rows].shape or not torch.allclose(
        positions, mesh_points[rows], rtol=1e-5, atol=1e-6
    ):
        raise ValueError(f"{path}: PT 坐标与 VTK 原点身份不一致")
    full_edges = vtk_cell_edges(mesh)
    edge_index, _ = induced_subgraph(full_edges, rows, node_count=mesh.GetNumberOfPoints())
    return {"edge_index": edge_index.cpu(), "source_ids": requested.cpu()}
