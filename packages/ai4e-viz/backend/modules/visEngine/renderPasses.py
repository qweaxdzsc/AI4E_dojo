"""远程渲染阴影原语，以及与 ParaView 对齐的默认 Light Kit。"""

from __future__ import annotations

import sys

import vtk

# VTK `vtkLightKit` 构造默认值；ParaView Light Inspector 默认套件同源。
# 文档示例里改过的 K:F=2.5 / K:H=2.0 是演示值，不是默认。
PARAVIEW_LIGHT_KIT = {
    "key_intensity": 0.75,
    "key_to_fill": 3.0,
    "key_to_back": 3.5,
    "key_to_head": 3.0,
    "key_warmth": 0.6,
    "fill_warmth": 0.4,
    "back_warmth": 0.5,
    "head_warmth": 0.5,
    "key_elevation": 50.0,
    "key_azimuth": 10.0,
    "fill_elevation": -75.0,
    "fill_azimuth": -10.0,
    "back_elevation": 0.0,
    "back_azimuth": 110.0,
}

_LIGHT_KIT_ATTR = "_vis_light_kit"


def paraview_light_kit_defaults() -> dict[str, float]:
    """返回 ParaView/VTK 默认 Light Kit 强度、比例、色温与方位。"""

    return dict(PARAVIEW_LIGHT_KIT)


def apply_paraview_light_kit(renderer) -> vtk.vtkLightKit:
    """用五灯套件替换 VTK 自动单头灯，避免可见背光面全黑。

    套件含主光、补光、两盏轮廓光和一盏相机头灯，强度按 Key 与 K:F/K:B/K:H
    比例计算。材质 Ambient/Diffuse 仍走科学着色，不在这里抬环境系数。
    已挂过的套件复用同一组灯对象，避免本地序列化身份抖动。
    """

    if renderer is None:
        raise ValueError("light_kit_requires_renderer")
    kit = getattr(renderer, _LIGHT_KIT_ATTR, None)
    if kit is None:
        defaults = PARAVIEW_LIGHT_KIT
        kit = vtk.vtkLightKit()
        kit.SetKeyLightIntensity(defaults["key_intensity"])
        kit.SetKeyToFillRatio(defaults["key_to_fill"])
        kit.SetKeyToBackRatio(defaults["key_to_back"])
        kit.SetKeyToHeadRatio(defaults["key_to_head"])
        kit.SetKeyLightWarmth(defaults["key_warmth"])
        kit.SetFillLightWarmth(defaults["fill_warmth"])
        kit.SetBackLightWarmth(defaults["back_warmth"])
        kit.SetHeadLightWarmth(defaults["head_warmth"])
        kit.SetKeyLightAngle(defaults["key_elevation"], defaults["key_azimuth"])
        kit.SetFillLightAngle(defaults["fill_elevation"], defaults["fill_azimuth"])
        kit.SetBackLightAngle(defaults["back_elevation"], defaults["back_azimuth"])
        kit.Modified()
        renderer.AutomaticLightCreationOff()
        renderer.RemoveAllLights()
        kit.AddLightsToRenderer(renderer)
        setattr(renderer, _LIGHT_KIT_ATTR, kit)
        return kit
    renderer.AutomaticLightCreationOff()
    if renderer.GetLights().GetNumberOfItems() == 0:
        kit.AddLightsToRenderer(renderer)
    return kit


def enable_shadows(renderer) -> None:
    """只在受支持的 Linux 远程路径启用阴影通道；默认关闭。"""

    if sys.platform != "linux":
        raise ValueError("shadows_require_supported_linux_rendering")
    shadows = vtk.vtkShadowMapPass()
    sequence = vtk.vtkSequencePass()
    passes = vtk.vtkRenderPassCollection()
    passes.AddItem(shadows.GetShadowMapBakerPass())
    passes.AddItem(shadows)
    sequence.SetPasses(passes)
    camera = vtk.vtkCameraPass()
    camera.SetDelegatePass(sequence)
    renderer.SetPass(camera)
