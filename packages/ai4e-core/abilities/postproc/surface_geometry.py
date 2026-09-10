"""表面拓扑描述、面积比与朝向；保持参考几何算法次序。"""

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class SurfaceTopology:
    """Mixed triangle/quad topology reconstructed from node adjacency."""

    triangles: np.ndarray
    quads: np.ndarray
    point_count: int
    edge_count: int

    @property
    def face_count(self) -> int:
        """Return the number of reconstructed surface cells."""
        return int(self.triangles.shape[0] + self.quads.shape[0])

    @property
    def euler_characteristic(self) -> int:
        """Return ``V - E + F`` for topology diagnostics."""
        return self.point_count - self.edge_count + self.face_count


def surface_area_ratio(
    topology: SurfaceTopology, points: np.ndarray, nodal_area: np.ndarray
) -> float:
    """Compare reconstructed polygon area with the provided NASA nodal-area sum."""
    face_area = 0.0
    if topology.triangles.size:
        triangle_points = points[topology.triangles]
        face_area += float(
            (
                0.5
                * np.linalg.norm(
                    np.cross(
                        triangle_points[:, 1] - triangle_points[:, 0],
                        triangle_points[:, 2] - triangle_points[:, 0],
                    ),
                    axis=1,
                )
            ).sum()
        )
    if topology.quads.size:
        quad_points = points[topology.quads]
        first = 0.5 * np.linalg.norm(
            np.cross(quad_points[:, 1] - quad_points[:, 0], quad_points[:, 2] - quad_points[:, 0]),
            axis=1,
        )
        second = 0.5 * np.linalg.norm(
            np.cross(quad_points[:, 2] - quad_points[:, 0], quad_points[:, 3] - quad_points[:, 0]),
            axis=1,
        )
        face_area += float((first + second).sum())
    supplied_area = float(np.asarray(nodal_area, dtype=np.float64).sum())
    if supplied_area <= 0:
        raise ValueError("NASA nodal surface area must be positive")
    return face_area / supplied_area


def orient_topology(
    topology: SurfaceTopology, points: np.ndarray, normals: np.ndarray
) -> SurfaceTopology:
    """Orient every face to agree with the supplied NASA nodal normals."""
    if points.shape != (topology.point_count, 3) or normals.shape != points.shape:
        raise ValueError("Points and normals do not match the reconstructed topology")
    triangles = topology.triangles.copy()
    if triangles.size:
        triangle_normals = np.cross(
            points[triangles[:, 1]] - points[triangles[:, 0]],
            points[triangles[:, 2]] - points[triangles[:, 0]],
        )
        expected = normals[triangles].sum(axis=1)
        flip = np.einsum("ij,ij->i", triangle_normals, expected) < 0
        triangles[flip] = triangles[flip][:, [0, 2, 1]]

    quads = topology.quads.copy()
    if quads.size:
        quad_points = points[quads]
        next_points = np.roll(quad_points, -1, axis=1)
        quad_normals = np.cross(quad_points, next_points).sum(axis=1)
        expected = normals[quads].sum(axis=1)
        flip = np.einsum("ij,ij->i", quad_normals, expected) < 0
        quads[flip] = quads[flip][:, [0, 3, 2, 1]]
    return SurfaceTopology(triangles, quads, topology.point_count, topology.edge_count)
