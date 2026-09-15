"""旋转、平移、缩放、坐标轴、标准视图和适合窗口业务规则。"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ViewTransform:
    """与渲染器无关的视图变换；坐标采用右手系，角度单位为度。"""

    azimuth: float = 0.0
    elevation: float = 0.0
    zoom: float = 1.0


def validate_view(transform: ViewTransform) -> ViewTransform:
    """校验视图缩放，防止零值或负值进入VTK相机。"""

    if transform.zoom <= 0:
        raise ValueError("视图缩放必须大于零")
    return transform


def camera_spec(camera) -> dict:
    """将相机转成跨进程、跨渲染模式的配置。"""
    return {'position': list(camera.GetPosition()), 'focal_point': list(camera.GetFocalPoint()), 'view_up': list(camera.GetViewUp()), 'parallel_scale': camera.GetParallelScale(), 'parallel_projection': bool(camera.GetParallelProjection())}


def set_camera(camera, value: dict) -> None:
    """恢复相机配置。"""
    for key, setter in [('position', camera.SetPosition), ('focal_point', camera.SetFocalPoint), ('view_up', camera.SetViewUp), ('parallel_scale', camera.SetParallelScale), ('parallel_projection', camera.SetParallelProjection)]:
        if key in value:
            setter(value[key])

