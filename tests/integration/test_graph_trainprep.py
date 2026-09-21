"""中立网格图、PT/VTKHDF 对齐、缓存、分区和 halo 契约。"""

import pytest
import torch
import vtk
from test_platform_mesh_dataset import platform_dataset

from ai4e_core.abilities.data.source.physical import PhysicalView
from ai4e_core.abilities.geometry.mesh_graph import (
    cells_to_edges,
    induced_subgraph,
    vtk_cell_edges,
)
from ai4e_core.abilities.sampling import graph as graph_sampling
from ai4e_core.abilities.sampling.graph import core_partitions, expand_halo, partition_with_halo
from ai4e_core.applications.aero_cfd.trainprep.topology import TopologyView


def test_vtkhdf_binding_aligns_ids_and_rebuilds_deleted_cache(tmp_path):
    view = TopologyView(
        PhysicalView(platform_dataset(tmp_path)),
        {"domains": {"surface": {"mesh": "surface"}}},
        tmp_path / "cache",
    )
    first = view.read("train", 0)["domains"]["surface"]["graph"]
    assert first["edge_index"].shape == (2, 8)
    cache = next((tmp_path / "cache").rglob("*.pt"))
    cache.unlink()
    second = view.read("train", 0)["domains"]["surface"]["graph"]
    assert torch.equal(first["edge_index"], second["edge_index"])
    assert first["topology_digest"] == second["topology_digest"]


def test_topology_binding_caches_partition_and_halo_for_reuse(tmp_path, monkeypatch):
    """trainprep 按当前预算缓存分区，后续读取不重复展开同一大图。"""
    output = tmp_path / "cache"
    sampling = {
        "domains": {
            "surface": {
                "train": {"method": "core_halo", "core_nodes": 2, "halo_hops": 1},
                "infer": {"method": "core_halo", "core_nodes": 2, "halo_hops": 1},
            }
        }
    }
    from ai4e_core.applications.aero_cfd.trainprep import topology

    calls = 0
    original = topology.partition_with_halo

    def counted(*args, **kwargs):
        nonlocal calls
        calls += 1
        return original(*args, **kwargs)

    monkeypatch.setattr(topology, "partition_with_halo", counted)
    first = TopologyView(
        PhysicalView(platform_dataset(tmp_path)),
        {"domains": {"surface": {"mesh": "surface"}}},
        output,
        sampling,
    ).read("train", 0)["domains"]["surface"]["graph"]
    assert len(first["partitions"]["train"]["items"]) == 2
    assert calls == 1

    monkeypatch.setattr(
        "ai4e_core.applications.aero_cfd.trainprep.topology.partition_with_halo",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("不应重算分区")),
    )
    second = TopologyView(
        PhysicalView(tmp_path / "manifest.json"),
        {"domains": {"surface": {"mesh": "surface"}}},
        output,
        sampling,
    ).read("train", 0)["domains"]["surface"]["graph"]
    assert torch.equal(
        first["partitions"]["train"]["items"][0]["node_ids"],
        second["partitions"]["train"]["items"][0]["node_ids"],
    )


@pytest.mark.parametrize("failure", ["missing_mesh", "coordinate_mismatch"])
def test_topology_binding_rejects_missing_mesh_and_misaligned_coordinates(tmp_path, failure):
    manifest = platform_dataset(tmp_path)
    if failure == "missing_mesh":
        (tmp_path / "train/sample/surface.vtkhdf").unlink()
    else:
        path = tmp_path / "train/sample/position.pt"
        torch.save(torch.load(path, weights_only=True) + 10, path)
    view = TopologyView(
        PhysicalView(manifest),
        {"domains": {"surface": {"mesh": "surface"}}},
        tmp_path / "cache",
    )
    with pytest.raises((FileNotFoundError, ValueError)):
        view.read("train", 0)


def test_cells_induced_subgraph_partition_and_halo_are_stable():
    triangles = torch.tensor([[0, 1, 2]])
    quads = torch.tensor([[2, 3, 4, 5]])
    hexahedra = torch.tensor([[6, 7, 8, 9, 10, 11, 12, 13]])
    edges = cells_to_edges([triangles, quads, hexahedra])
    assert edges.shape[1] == 2 * (3 + 4 + 12)
    local, source = induced_subgraph(edges, torch.tensor([2, 3, 4, 5]), node_count=14)
    assert source.tolist() == [2, 3, 4, 5]
    assert local.shape == (2, 8)
    chain = torch.tensor([[0, 1, 1, 2, 2, 3, 3, 4], [1, 0, 2, 1, 3, 2, 4, 3]])
    parts = core_partitions(chain, 5, 2)
    assert torch.cat(parts).sort().values.tolist() == [0, 1, 2, 3, 4]
    assert sum(len(part) for part in parts) == 5
    nodes, mask = expand_halo(chain, torch.tensor([2]), 5, 1)
    assert nodes.tolist() == [1, 2, 3]
    assert nodes[mask].tolist() == [2]


def test_partition_with_halo_builds_large_graph_adjacency_once(monkeypatch):
    """组合分区复用同一邻接表，避免为每个核心块重复展开全部边。"""
    chain = torch.tensor([[0, 1, 1, 2, 2, 3, 3, 4], [1, 0, 2, 1, 3, 2, 4, 3]])
    calls = 0
    original = graph_sampling._adjacency

    def counted(edge_index, node_count):
        nonlocal calls
        calls += 1
        return original(edge_index, node_count)

    monkeypatch.setattr(graph_sampling, "_adjacency", counted)
    parts = partition_with_halo(chain, node_count=5, max_nodes=2, hops=1)

    assert calls == 1
    assert torch.cat([part["core_ids"] for part in parts]).sort().values.tolist() == [0, 1, 2, 3, 4]


def test_mixed_vtk_cells_use_real_local_edges():
    """三角、四边、四面体和六面体不会被展开成单元完全图。"""
    mesh = vtk.vtkUnstructuredGrid()
    points = vtk.vtkPoints()
    for index in range(19):
        points.InsertNextPoint(float(index), 0.0, 0.0)
    mesh.SetPoints(points)
    declarations = [
        (vtk.VTK_TRIANGLE, [0, 1, 2]),
        (vtk.VTK_QUAD, [3, 4, 5, 6]),
        (vtk.VTK_TETRA, [7, 8, 9, 10]),
        (vtk.VTK_HEXAHEDRON, list(range(11, 19))),
    ]
    for cell_type, ids in declarations:
        values = vtk.vtkIdList()
        for value in ids:
            values.InsertNextId(value)
        mesh.InsertNextCell(cell_type, values)
    edges = vtk_cell_edges(mesh)
    assert edges.shape == (2, 2 * (3 + 4 + 6 + 12))
