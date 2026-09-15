"""三维物理场统一Trame会话适配器。

这里复用模块内 ``trameServer`` 的真实场景构建函数。导入采用惰性方式，避免模块
发现阶段创建Trame Server或加载VTK数据。
"""

from collections.abc import Callable


def legacy_scene_builder(view: str) -> Callable[[], object]:
    """按现有视图名返回真实Trame场景构建器，不在此处创建独立Server。"""

    from . import exampleScenes as trameServer

    builders = {
        "raster": trameServer.build_raster_scene,
        "raster_vector": trameServer.build_raster_vector_scene,
        "points": trameServer.build_points_scene,
        "volume": trameServer.build_volume_scene,
        "volume_vector": trameServer.build_volume_vector_scene,
        "trajectory": trameServer.build_trajectory_scene,
        "field": trameServer.build_field_scene,
        "field_vector": trameServer.build_field_vector_scene,
        "miller_field": trameServer.build_miller_field_scene,
    }
    try:
        return builders[view]
    except KeyError as exc:
        raise ValueError(f"未知Trame物理场视图: {view}") from exc
