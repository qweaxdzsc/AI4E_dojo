"""无业务含义的可视化内核、缓存和抽样原语测试。"""

import math

import pytest
import vtk
from vtk.util.numpy_support import vtk_to_numpy

from modules.visEngine import (
    KernelCache,
    apply_paraview_light_kit,
    evenly_spaced_indices,
    paraview_light_kit_defaults,
    scalar_range,
)


def test_engine_cache_evicts_least_recently_used_value() -> None:
    """缓存到达容量后应淘汰最久未访问项。"""

    cache = KernelCache[int](capacity=2)
    cache.put("a", 1)
    cache.put("b", 2)
    assert cache.get("a") == 1
    cache.put("c", 3)
    assert cache.get("b") is None
    assert cache.get("c") == 3


def test_engine_numeric_primitives_cover_boundaries() -> None:
    """抽样覆盖首尾，标量范围忽略非有限值。"""

    indices = evenly_spaced_indices(11, 4)
    assert indices[0] == 0 and indices[-1] == 10
    assert scalar_range([math.nan, -2.0, 4.5, math.inf]) == (-2.0, 4.5)
    assert scalar_range([math.nan]) is None
    with pytest.raises(ValueError):
        evenly_spaced_indices(-1, 4)


def _light_items(renderer):
    """按集合顺序取出当前灯，便于核对类型与强度。"""

    lights = renderer.GetLights()
    return [lights.GetItemAsObject(index) for index in range(lights.GetNumberOfItems())]


def _visible_luminance_range(renderer):
    """离屏拍一帧，取非背景像素的最暗/最亮亮度。"""

    window = vtk.vtkRenderWindow()
    window.SetOffScreenRendering(1)
    window.SetSize(160, 160)
    window.AddRenderer(renderer)
    window.Render()
    capture = vtk.vtkWindowToImageFilter()
    capture.SetInput(window)
    capture.ReadFrontBufferOff()
    capture.Update()
    pixels = vtk_to_numpy(capture.GetOutput().GetPointData().GetScalars()).reshape(-1, 3)
    visible = [
        0.299 * row[0] + 0.587 * row[1] + 0.114 * row[2]
        for row in pixels
        if not (row[0] == 0 and row[1] == 0 and row[2] == 0)
    ]
    window.Finalize()
    assert visible
    return min(visible), max(visible)


def test_paraview_light_kit_replaces_automatic_headlight() -> None:
    """默认套件是五灯，强度按 VTK/ParaView 比例，且不会叠上自动头灯。"""

    defaults = paraview_light_kit_defaults()
    renderer = vtk.vtkRenderer()
    first = apply_paraview_light_kit(renderer)
    second = apply_paraview_light_kit(renderer)
    lights = _light_items(renderer)
    assert first is second
    assert renderer.GetAutomaticLightCreation() == 0
    assert len(lights) == 5
    types = sorted(light.GetLightType() for light in lights)
    assert types == [1, 2, 2, 2, 2]
    intensities = sorted(round(light.GetIntensity(), 6) for light in lights)
    expected = sorted(
        round(value, 6)
        for value in (
            defaults["key_intensity"],
            defaults["key_intensity"] / defaults["key_to_fill"],
            defaults["key_intensity"] / defaults["key_to_head"],
            defaults["key_intensity"] / defaults["key_to_back"],
            defaults["key_intensity"] / defaults["key_to_back"],
        )
    )
    assert intensities == expected
    extra = vtk.vtkLight()
    renderer.AddLight(extra)
    renderer.RemoveAllLights()
    apply_paraview_light_kit(renderer)
    assert len(_light_items(renderer)) == 5


def test_paraview_light_kit_lifts_grazing_faces() -> None:
    """与 VTK 单头灯相比，套件应抬高可见掠射面亮度，而不是把背光洗成纯黑。"""

    source = vtk.vtkSphereSource()
    source.SetThetaResolution(48)
    source.SetPhiResolution(48)
    source.Update()

    def scene(use_kit: bool):
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(source.GetOutputPort())
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(1, 1, 1)
        actor.GetProperty().SetAmbient(0)
        actor.GetProperty().SetDiffuse(1)
        actor.GetProperty().SetSpecular(0)
        renderer = vtk.vtkRenderer()
        renderer.SetBackground(0, 0, 0)
        renderer.AddActor(actor)
        camera = renderer.GetActiveCamera()
        camera.SetPosition(0, -3, 0.6)
        camera.SetFocalPoint(0, 0, 0)
        camera.SetViewUp(0, 0, 1)
        renderer.ResetCameraClippingRange()
        if use_kit:
            apply_paraview_light_kit(renderer)
        return renderer

    default_min, default_max = _visible_luminance_range(scene(False))
    kit_min, kit_max = _visible_luminance_range(scene(True))
    # 单头灯把掠射面压得很暗；套件用补光/轮廓光抬最暗可见面，同时不高光过曝。
    assert kit_min > default_min
    assert kit_min > 8
    assert kit_max < default_max
