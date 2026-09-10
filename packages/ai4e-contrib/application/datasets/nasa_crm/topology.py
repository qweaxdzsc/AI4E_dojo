"""NASA 邻接表的表面拓扑重建；不以近似三角剖分替代官方连接。"""

from pathlib import Path

import h5py
import numpy as np

from ai4e_core.abilities.postproc.surface_geometry import SurfaceTopology


def load_adjacency(path: Path) -> list[set[int]]:
    """Load and validate the official symmetric NASA CRM node adjacency.

    Args:
        path: ``connectivity_NASA-CRM.h5`` path.

    Returns:
        One neighbor set for every surface point.
    """
    if not path.is_file():
        raise FileNotFoundError(f"NASA CRM connectivity file not found: {path}")
    with h5py.File(path, "r") as source:
        if "Connectivity" not in source:
            raise ValueError(f"Connectivity group not found in {path}")
        group = source["Connectivity"]
        point_count = len(group)
        adjacency: list[set[int]] = []
        for point in range(point_count):
            key = str(point)
            if key not in group:
                raise ValueError(f"Missing connectivity entry for point {point}")
            values = np.asarray(group[key][:], dtype=np.int64)
            neighbors = set(map(int, values))
            if len(neighbors) != len(values):
                raise ValueError(f"Connectivity entry {point} contains duplicate neighbors")
            if point in neighbors:
                raise ValueError(f"Connectivity entry {point} contains a self edge")
            if any(neighbor < 0 or neighbor >= point_count for neighbor in neighbors):
                raise ValueError(f"Connectivity entry {point} contains an invalid point index")
            adjacency.append(neighbors)
    for point, neighbors in enumerate(adjacency):
        for neighbor in neighbors:
            if point not in adjacency[neighbor]:
                raise ValueError(f"Connectivity edge {point}-{neighbor} is not symmetric")
    return adjacency


def reconstruct_surface_topology(path: Path) -> SurfaceTopology:
    """Enumerate triangle cliques and chordless quad cycles from adjacency.

    The NASA file stores graph neighbors rather than a VTK cell array. A triangle
    is a three-node clique. A quad is a chordless four-cycle; excluding both
    diagonals avoids treating adjacent cells as larger or triangulated faces.

    Args:
        path: Official NASA CRM connectivity HDF5 path.

    Returns:
        Deduplicated mixed-cell surface topology.
    """
    adjacency = load_adjacency(path)
    triangles: list[tuple[int, int, int]] = []
    for first, first_neighbors in enumerate(adjacency):
        for second in first_neighbors:
            if second <= first:
                continue
            for third in first_neighbors.intersection(adjacency[second]):
                if third > second:
                    triangles.append((first, second, third))

    quads_by_nodes: dict[tuple[int, int, int, int], tuple[int, int, int, int]] = {}
    for first, first_neighbors in enumerate(adjacency):
        neighbors = sorted(first_neighbors)
        for left_index, second in enumerate(neighbors):
            for fourth in neighbors[left_index + 1 :]:
                if fourth in adjacency[second]:
                    continue
                for third in adjacency[second].intersection(adjacency[fourth]):
                    if third == first or third in first_neighbors:
                        continue
                    sorted_nodes = sorted((first, second, third, fourth))
                    key = (
                        sorted_nodes[0],
                        sorted_nodes[1],
                        sorted_nodes[2],
                        sorted_nodes[3],
                    )
                    quads_by_nodes.setdefault(key, (first, second, third, fourth))

    triangle_array = np.asarray(triangles, dtype=np.int64).reshape((-1, 3))
    quad_array = np.asarray(list(quads_by_nodes.values()), dtype=np.int64).reshape((-1, 4))
    edge_count = sum(len(neighbors) for neighbors in adjacency) // 2
    return SurfaceTopology(triangle_array, quad_array, len(adjacency), edge_count)
