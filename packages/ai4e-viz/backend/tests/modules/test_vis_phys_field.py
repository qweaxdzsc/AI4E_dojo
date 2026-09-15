"""visPhysField一级基座、九类Trame场景和二级业务接入测试。"""

from modules.visPhysField import build_field_command
from modules.visPhysField.modules.dataExtraction.spatial import SpatialExtraction, validate_spatial_extraction
from modules.visPhysField.modules.dataOverview.basicCharts import validate_basic_chart
from modules.visPhysField.modules.fieldVisualization.timeline import clamp_frame
from modules.visPhysField import legacy_scene_builder
from modules.visPhysField import trameServer


def test_nine_trame_scenes_are_registered() -> None:
    """验证九类现有Trame场景全部由物理场一级模块注册。"""

    views = {"raster", "raster_vector", "volume", "volume_vector", "field",
             "field_vector", "miller_field", "points", "trajectory"}
    assert all(callable(legacy_scene_builder(view)) for view in views)
    # 导入入口不建立工作进程或九份场景，示例只能显式构建。
    assert not hasattr(trameServer, "SCENES")
    animation = legacy_scene_builder("miller_field")()
    assert animation.frame_count == 240
    animation.render_window.Finalize()


def test_second_level_business_uses_first_level_command() -> None:
    """验证二级展示、提取和概览规则可被一级命令统一编排。"""

    extraction = validate_spatial_extraction(SpatialExtraction("surface", ("pressure",), {"normal": [0, 0, 1]}))
    command = build_field_command("extractData", {"kind": extraction.kind})
    assert command.payload["kind"] == "surface"
    assert clamp_frame(-1, 10) == 0
    assert validate_basic_chart("scatter", "x", "pressure")[0] == "scatter"
