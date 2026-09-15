"""远程渲染光照原语，平台支持由运行探测和验收决定。"""
import sys
import vtk


def enable_shadows(renderer) -> None:
    """只在受支持的 Linux 远程路径启用阴影通道。"""
    if sys.platform != 'linux':
        raise ValueError('shadows_require_supported_linux_rendering')
    shadows = vtk.vtkShadowMapPass()
    sequence = vtk.vtkSequencePass()
    passes = vtk.vtkRenderPassCollection()
    passes.AddItem(shadows.GetShadowMapBakerPass())
    passes.AddItem(shadows)
    sequence.SetPasses(passes)
    camera = vtk.vtkCameraPass()
    camera.SetDelegatePass(sequence)
    renderer.SetPass(camera)
