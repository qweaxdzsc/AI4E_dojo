"""Miller时序物理场的VTK场景与标量缓冲区原位更新。"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import vtk
from vtk.util import numpy_support


class MillerFieldAnimation:
    """保持拓扑与相机稳定，只替换每帧标量缓冲区。"""

    def __init__(self, source: str | Path, *, initial_frame: int | None = None):
        source = Path(source)
        with np.load(source, allow_pickle=False) as arrays:
            self.frames = np.asarray(arrays["phi_surface_normalized"], dtype=np.float32)
            self.frame_numbers = np.asarray(arrays["frame"], dtype=np.int32)
            self.times = np.asarray(arrays["time_R_over_vti"], dtype=np.float64)
            x = np.asarray(arrays["surface_x"], dtype=np.float64)
            y = np.asarray(arrays["surface_y"], dtype=np.float64)
            z = np.asarray(arrays["surface_z"], dtype=np.float64)
            metadata = arrays.get("metadata_json")
            self.fps = 24.0
            if metadata is not None:
                try:
                    import json

                    decoded = json.loads(str(np.asarray(metadata).item()))
                    self.fps = float(decoded.get("fps", self.fps))
                except (TypeError, ValueError, json.JSONDecodeError):
                    pass

        if self.frames.ndim != 3:
            raise ValueError(f"MILLER_FIELD_SHAPE_INVALID: {self.frames.shape}")
        if x.shape != self.frames.shape[1:] or y.shape != x.shape or z.shape != x.shape:
            raise ValueError("MILLER_TOPOLOGY_SHAPE_INVALID")

        self.frame_count, rows, cols = self.frames.shape
        self.global_range = (float(np.min(self.frames)), float(np.max(self.frames)))
        self.current_frame = max(0, min(self.frame_count - 1, initial_frame if initial_frame is not None else self.frame_count // 2))

        points = vtk.vtkPoints()
        coordinates = np.column_stack((x.ravel(), y.ravel(), z.ravel()))
        points.SetData(numpy_support.numpy_to_vtk(coordinates, deep=True))
        quads = vtk.vtkCellArray()
        for row in range(rows - 1):
            base = row * cols
            next_base = (row + 1) * cols
            for col in range(cols - 1):
                quad = vtk.vtkQuad()
                quad.GetPointIds().SetId(0, base + col)
                quad.GetPointIds().SetId(1, base + col + 1)
                quad.GetPointIds().SetId(2, next_base + col + 1)
                quad.GetPointIds().SetId(3, next_base + col)
                quads.InsertNextCell(quad)

        self.surface = vtk.vtkPolyData()
        self.surface.SetPoints(points)
        self.surface.SetPolys(quads)
        self.scalars = numpy_support.numpy_to_vtk(self.frames[self.current_frame].ravel(), deep=True)
        self.scalars.SetName("phi_surface_normalized")
        self.surface.GetPointData().SetScalars(self.scalars)

        normals = vtk.vtkPolyDataNormals()
        normals.SetInputData(self.surface)
        normals.SplittingOff()
        normals.ConsistencyOn()
        normals.Update()

        lut = vtk.vtkLookupTable()
        lut.SetNumberOfTableValues(256)
        lut.SetHueRange(0.66, 0.0)
        lut.SetRange(*self.global_range)
        lut.Build()
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(normals.GetOutputPort())
        mapper.SetLookupTable(lut)
        mapper.SetScalarRange(*self.global_range)
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetInterpolationToPhong()
        actor.GetProperty().SetSpecular(0.18)

        renderer = vtk.vtkRenderer()
        renderer.SetBackground(0.055, 0.075, 0.105)
        renderer.AddActor(actor)
        camera = renderer.GetActiveCamera()
        camera.SetPosition(5.8, -6.2, 3.8)
        camera.SetFocalPoint(0.0, 0.0, 0.0)
        camera.SetViewUp(0.0, 0.0, 1.0)
        renderer.ResetCameraClippingRange()
        self.render_window = vtk.vtkRenderWindow()
        self.render_window.AddRenderer(renderer)

    def set_frame(self, index: int) -> dict[str, float | int]:
        """原位替换点标量并返回可直接传给UI的帧元数据。"""

        index = max(0, min(self.frame_count - 1, int(index)))
        target = numpy_support.vtk_to_numpy(self.scalars)
        np.copyto(target, self.frames[index].ravel())
        self.scalars.Modified()
        self.surface.GetPointData().Modified()
        self.surface.Modified()
        self.render_window.Modified()
        self.current_frame = index
        return {
            "index": index,
            "frame": int(self.frame_numbers[index]),
            "time": float(self.times[index]),
            "minimum": float(np.min(self.frames[index])),
            "maximum": float(np.max(self.frames[index])),
        }
