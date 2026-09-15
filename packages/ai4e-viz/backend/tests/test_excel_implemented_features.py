"""Excel“功能模块”中既有实现能力的逐项后端回归。

本文件只覆盖能够从当前代码和重构前基线确认存在的功能。测试名保留Excel序号，方便
从功能矩阵反查自动化证据；未实现能力不会通过校验器或空Router伪装成业务通过。
"""

from __future__ import annotations

from pathlib import Path

import pytest
import vtk
from fastapi.testclient import TestClient

from modules.visConvertor.converter import convert_to_glb
from modules.visPhysField import legacy_scene_builder
from server.api import app


client = TestClient(app)


def test_excel_13_14_dataset_sampling_and_partial_statistics() -> None:
    """验证数据抽查可打开真实文件，画像确实返回覆盖、极值与均值。"""

    response = client.get("/api/artifact/A-1025/parse")
    assert response.status_code == 200
    profile = response.json()
    assert profile["format"] == "CSV"
    assert profile["rows"] == 5_941
    assert profile["time_column"] == "time"
    pressure = profile["column_profiles"]["pitot_p1"]
    assert pressure["missing"] == 0.0
    assert pressure["min"] == pytest.approx(102.936)
    assert pressure["max"] == pytest.approx(121.557)
    assert pressure["mean"] == pytest.approx(112.41812640969532)


@pytest.mark.parametrize(
    ("excel_id", "case_id", "view"),
    [
        (22, "CASE-RASTER-SCALAR", "raster"),
        (23, "CASE-RASTER-VECTOR", "raster_vector"),
        (22, "CASE-VOLUME-SCALAR", "volume"),
        (23, "CASE-VOLUME-VECTOR", "volume_vector"),
        (22, "CASE-FIELD-SCALAR", "field"),
        (23, "CASE-FIELD-VECTOR", "field_vector"),
    ],
)
def test_excel_22_23_scalar_and_vector_field_cases(
    excel_id: int, case_id: str, view: str
) -> None:
    """逐案例验证标量云图和矢量图由Trame/vtk.js真实场景承载。"""

    response = client.get(f"/api/examples/{case_id}")
    assert response.status_code == 200, f"Excel {excel_id} / {case_id}"
    payload = response.json()
    assert payload["renderer"]["owner"] == "trame-vtkjs"
    assert f"view={view}" in payload["renderer"]["url"]
    assert payload["data"]


def test_excel_26_volume_scene_contains_real_iso_surfaces() -> None:
    """验证体场场景包含体渲染Actor和两个真实等值面，而非仅有功能名称。"""

    renderers = legacy_scene_builder("volume")().GetRenderers()
    renderers.InitTraversal()
    renderer = renderers.GetNextItem()
    assert renderer is not None
    # 一个体渲染对象加两个等值面Actor；这是当前“等值面”已实现的明确边界。
    assert renderer.GetVolumes().GetNumberOfItems() == 1
    assert renderer.GetActors().GetNumberOfItems() >= 2


def test_excel_32_miller_timeline_has_240_frames_and_reuses_topology() -> None:
    """验证时序前进/后退/播放所依赖的240帧数据和原位标量更新。"""

    animation = legacy_scene_builder("miller_field")()
    assert animation.frame_count == 240
    points = animation.surface.GetPoints()
    scalars = animation.scalars
    before = scalars.GetMTime()
    metadata = animation.set_frame(1)
    assert metadata["index"] == 1
    assert animation.surface.GetPoints() is points
    assert animation.scalars is scalars
    assert scalars.GetMTime() > before


@pytest.mark.parametrize(
    ("excel_id", "case_id", "kind", "renderer"),
    [
        (48, "CASE-TABLE", "table", "perspective"),
        (49, "CASE-OPTIMIZATION", "optimization", "echarts-svg"),
        (50, "CASE-SERIES", "series", "echarts-svg"),
        (51, "CASE-DISTRIBUTION", "distribution", "echarts-svg"),
    ],
)
def test_excel_48_51_data_preview_payloads(
    excel_id: int, case_id: str, kind: str, renderer: str
) -> None:
    """验证表格、散点、折线和柱状预览具有真实数据与正确渲染器。"""

    response = client.get(f"/api/examples/{case_id}")
    assert response.status_code == 200, f"Excel {excel_id} / {case_id}"
    payload = response.json()
    assert payload["artifact"]["kind"] == kind
    assert payload["renderer"]["owner"] == renderer
    assert payload["data"]


@pytest.mark.parametrize("case_id", ["CASE-IMAGE", "A-1112"])
def test_excel_55_image_preview_is_a_real_png(case_id: str) -> None:
    """验证图片预览返回浏览器可直接读取的真实PNG字节。"""

    example = client.get(f"/api/examples/{case_id}")
    assert example.status_code == 200
    payload = example.json()
    assert payload["artifact"]["kind"] == "image"
    image_response = client.get(payload["data"]["url"].removeprefix("http://testserver"))
    assert image_response.status_code == 200
    assert image_response.content[:8] == b"\x89PNG\r\n\x1a\n"


def test_excel_100_stl_converts_to_valid_glb(tmp_path: Path) -> None:
    """验证Excel第100项STL转换真实生成GLB，而非只接受扩展名。"""

    source = tmp_path / "triangle.stl"
    source.write_text(
        "solid triangle\n"
        "facet normal 0 0 1\nouter loop\n"
        "vertex 0 0 0\nvertex 1 0 0\nvertex 0 1 0\n"
        "endloop\nendfacet\nendsolid triangle\n",
        encoding="utf-8",
    )
    output = tmp_path / "triangle.glb"
    convert_to_glb(str(source), str(output))
    assert output.read_bytes()[:4] == b"glTF"
    reader = vtk.vtkGLTFReader()
    reader.SetFileName(str(output))
    reader.Update()
    assert reader.GetOutput() is not None


def test_excel_105_csv_is_parsed_to_structured_json_for_frontend() -> None:
    """验证CSV转换为前端可消费的列画像和JSON记录，而非仅返回文件元数据。"""

    parsed = client.get("/api/artifact/A-1025/parse")
    assert parsed.status_code == 200
    payload = parsed.json()
    assert payload["columns"][0] == "time"
    assert payload["column_profiles"]["pitot_p1"]["dtype"] == "float64"


def test_excel_109_111_vtk_trame_scenes_are_renderable_windows() -> None:
    """验证九类场景都已由VTK构建并注册到统一Trame服务。"""

    views = ("raster", "raster_vector", "volume", "volume_vector", "field",
             "field_vector", "miller_field", "points", "trajectory")
    for view in views:
        result = legacy_scene_builder(view)()
        window = result.render_window if view == "miller_field" else result
        assert isinstance(window, vtk.vtkRenderWindow)
        window.Finalize()

