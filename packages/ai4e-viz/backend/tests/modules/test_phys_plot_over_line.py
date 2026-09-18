"""线段提取：沿线取样、对象树、Line Chart View、X/Y 轴与 CSV。"""

import csv
from pathlib import Path

from modules.visEngine import sample_line
from modules.visPhysField.modules.dataOverview.lineChart import line_chart_table

from .test_phys_display_updates import workspace as workspace_fixture

workspace = workspace_fixture


def _tree_ids(nodes):
    """展开对象树身份。"""
    for node in nodes:
        yield node["id"]
        yield from _tree_ids(node.get("children") or [])


def test_sample_line_count_and_arc_length(workspace):
    """分辨率决定点数，距离按弧长递增。"""
    _, scene, _ = workspace
    mesh = scene.datasets["base-s"]
    rows = sample_line(mesh, [0, 2, 2], [4, 2, 2], 11)
    assert len(rows) == 11
    assert rows[0]["distance"] == 0
    assert rows[-1]["distance"] == 4
    assert rows[5]["distance"] == 2
    assert all(rows[i]["distance"] <= rows[i + 1]["distance"] for i in range(10))


def test_plot_over_line_object_keeps_resolution(workspace):
    """应用线段提取后数据集点数与分辨率一致，曲线横轴为弧长。"""
    ui, scene, _ = workspace
    ui.begin("plot_over_line")
    ui.set_parameter("line_resolution", 20)
    assert ui.apply_selected(), ui.server.state.error
    identity = ui.server.state.selected
    mesh = scene.datasets[identity]
    assert mesh.GetNumberOfPoints() == 20
    rows = mesh._vis_line_rows
    assert len(rows) == 20
    assert rows[-1]["distance"] > 0
    ui.query_line()
    assert ui.server.state.query_curve
    assert "s=" in ui.server.state.query_curve
    assert identity in set(_tree_ids(ui.server.state.tree_nodes))
    assert next(n["type"] for n in scene.spec["pipeline"] if n["id"] == identity) == "plot_over_line"


def test_plot_over_line_opens_line_chart_view(workspace):
    """应用后对象树保留线段，右侧出现折线图视口而不是只在侧栏。"""
    ui, scene, _ = workspace
    ui.begin("plot_over_line")
    assert ui.helper_widget_kind() is None
    ui.set_parameter("line_resolution", 20)
    assert ui.apply_selected(), ui.server.state.error
    charts = [view for view in scene.spec["views"] if view.get("type") == "line_chart"]
    assert charts
    frames = ui.overlay_frames()
    chart_frame = next(frame for frame in frames if frame["view_type"] == "line_chart")
    assert chart_frame["has_chart"]
    assert "phys-line-chart-svg" in chart_frame["chart_html"]
    assert "<polyline" in chart_frame["chart_html"]
    assert ui.server.state.selected in set(_tree_ids(ui.server.state.tree_nodes))


def test_line_chart_xy_changes_series(workspace):
    """X/Y 是显示属性，改轴立即换序列，不重算取样点数。"""
    ui, scene, _ = workspace
    ui.begin("plot_over_line")
    ui.set_parameter("line_resolution", 12)
    assert ui.apply_selected(), ui.server.state.error
    rows = ui.line_rows()
    assert len(rows) == 12
    field = ui.server.state.chart_y_arrays[0]
    assert field
    headers, body = line_chart_table(rows, "arc_length", [field])
    assert headers == ["arc_length", field]
    assert len(body) == 12
    assert body[0][0] == 0
    ui.set_chart_axis("chart_x_array", "index")
    x_headers, x_body = line_chart_table(ui.line_rows(), ui.server.state.chart_x_array, [field])
    assert x_headers[0] == "index"
    assert [row[0] for row in x_body] != [row[0] for row in body]
    assert x_body[1][0] == 1
    assert len(ui.line_rows()) == 12
    ui.set_chart_axis("chart_y_arrays", [field, "Points_Y"])
    y_headers, y_body = line_chart_table(
        ui.line_rows(), ui.server.state.chart_x_array, ui.server.state.chart_y_arrays
    )
    assert y_headers == ["index", field, "Points_Y"]
    assert len(y_body[0]) == 3
    chart = next(view for view in scene.spec["views"] if view.get("type") == "line_chart")
    markup = ui.chart_markup(chart)
    assert field in markup
    assert "Points_Y" in markup


def test_line_chart_csv_columns_and_rows(workspace, tmp_path):
    """CSV 导出当前图的 X + 所选 Y，读回列名与行数一致。"""
    ui, _, _ = workspace
    ui.begin("plot_over_line")
    ui.set_parameter("line_resolution", 15)
    assert ui.apply_selected(), ui.server.state.error
    field = ui.server.state.chart_y_arrays[0]
    ui.set_chart_axis("chart_x_array", "arc_length")
    ui.set_chart_axis("chart_y_arrays", [field, "Points_Z"])
    path = tmp_path / "line_chart.csv"
    ui.export_line_chart_csv(path)
    with path.open(encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        assert reader.fieldnames == ["arc_length", field, "Points_Z"]
        exported = list(reader)
    assert len(exported) == 15
    assert float(exported[0]["arc_length"]) == 0
    text = ui.export_line_chart_csv()
    assert text.splitlines()[0] == f"arc_length,{field},Points_Z"


def test_new_viewport_can_be_line_chart(workspace):
    """新增视口可选三维渲染或折线图；旧窗口缺 type 当三维。"""
    ui, scene, _ = workspace
    assert scene.spec["views"][0].get("type", "render") == "render"
    assert ui.overlay_frames()[0]["view_type"] == "render"
    ui.view_action("view_create", view_type="line_chart")
    assert any(view.get("type") == "line_chart" for view in scene.spec["views"])
    assert any(view.get("type", "render") == "render" for view in scene.spec["views"])
    names = [view["name"] for view in scene.spec["views"]]
    assert any(name.startswith("LineChartView") for name in names)
    grid = (
        Path(__file__).resolve().parents[2]
        / "modules/visPhysField/trameUI/viewportGrid.py"
    ).read_text(encoding="utf-8")
    assert "三维渲染" in grid
    assert "折线图" in grid


def test_line_chart_tree_only_lists_plot_over_line(workspace):
    """折线图活跃时树只留下线段提取；切回三维恢复全树。"""
    ui, scene, _ = workspace
    ui.begin("slice")
    assert ui.apply_selected(), ui.server.state.error
    slice_id = ui.server.state.selected
    ui.select("base-s")
    ui.begin("plot_over_line")
    ui.set_parameter("line_resolution", 8)
    assert ui.apply_selected(), ui.server.state.error
    line_id = ui.server.state.selected
    charts = [view for view in scene.spec["views"] if view.get("type") == "line_chart"]
    assert charts
    ui.activate_view(charts[0]["id"])
    ids = set(_tree_ids(ui.server.state.tree_nodes))
    assert line_id in ids
    assert slice_id not in ids
    ui.visible(slice_id, False)
    assert ui.server.state.error == "折线图窗只能显示线段提取"
    render = next(view["id"] for view in scene.spec["views"] if view.get("type", "render") == "render")
    ui.activate_view(render)
    restored = set(_tree_ids(ui.server.state.tree_nodes))
    assert slice_id in restored
    assert line_id in restored


def test_plot_over_line_apply_clears_sample_fields(workspace):
    """新应用不再写取样场；旧修订场名只读，再应用改为全部。"""
    ui, scene, _ = workspace
    ui.begin("plot_over_line")
    ui.set_parameter("line_resolution", 10)
    assert ui.apply_selected(), ui.server.state.error
    identity = ui.server.state.selected
    node = next(item for item in scene.spec["pipeline"] if item["id"] == identity)
    assert node["parameters"]["fields"] == []
    rows = ui.line_rows()
    assert rows and (rows[0].get("fields") or rows[0].get("values"))
    scene.command(
        {
            "operation": "object_update",
            "id": identity,
            "type": "plot_over_line",
            "input": "base-s",
            "view": 0,
            "parameters": {
                **node["parameters"],
                "fields": ["point:temperature"],
            },
        }
    )
    stored = next(item for item in scene.spec["pipeline"] if item["id"] == identity)
    assert stored["parameters"]["fields"] == ["point:temperature"]
    ui.select(identity)
    ui.query_line()
    sampled = ui.line_rows()
    keys = set(sampled[0].get("fields") or sampled[0].get("values") or {})
    assert keys == {"point:temperature"}
    assert ui.apply_selected(), ui.server.state.error
    updated = next(item for item in scene.spec["pipeline"] if item["id"] == identity)
    assert updated["parameters"]["fields"] == []


def test_colorbar_and_probe_and_sample_field_markup():
    """色标用属性行，Probe 只有开关，线段提取没有取样物理量。"""
    from pathlib import Path

    root = Path(__file__).resolve().parents[2] / "modules/visPhysField/trameUI"
    toolbar = (root / "toolbar.py").read_text(encoding="utf-8")
    properties = (root / "propertiesPanel.py").read_text(encoding="utf-8")
    grid = (root / "viewportGrid.py").read_text(encoding="utf-8")
    assert "phys-legend-menu" in properties
    assert "phys-legend-popup" in properties
    assert "phys-legend-heading" in properties
    assert "apply_legend" in properties
    assert "prepare_legend" in properties
    assert "色标 · {{ object_name }}" in properties
    assert 'aria_label="色标"' not in toolbar
    assert "phys-legend-menu" not in toolbar
    assert "legend_select_menu" not in toolbar
    assert "legend_select_menu" not in properties
    assert "menu_props=" not in properties
    position = properties.split('aria_label="位置"', 1)[1]
    assert "menu_props" not in position.split("位置 X", 1)[0]
    assert "取样物理量" not in properties
    assert "phys-probe-pick-toggle" not in properties
    assert "phys-probe-pick-hint" not in properties
    assert 'label="{{ probe_pick_enabled ? \'开\' : \'关\' }}"' not in properties
    assert 'attach="#phys-window-toolbar"' in grid
    assert 'attach="body"' not in grid


def test_legend_position_uses_plain_select():
    """位置是字段旁的普通下拉，不把菜单挂到 body，也不把 Python True 写进模板。"""
    from pathlib import Path
    from trame.app import get_server
    from uuid import uuid4

    from modules.visPhysField.scene import Scene, default_spec
    from modules.visPhysField.trameUI.layout import build_ui

    properties = (
        Path(__file__).resolve().parents[2]
        / "modules/visPhysField/trameUI/propertiesPanel.py"
    ).read_text(encoding="utf-8")
    css = (
        Path(__file__).resolve().parents[2]
        / "modules/visPhysField/trameUI/client/workbench.css"
    ).read_text(encoding="utf-8")
    assert "legend_select_menu" not in properties
    assert "phys-legend-dropdown" not in properties
    assert 'content_class="phys-legend-popup"' in properties
    assert ".phys-legend-heading{" in css
    assert ".v-menu__content.phys-legend-popup{" in css
    assert "overflow:visible!important" in css
    assert ".phys-legend-actions{" in css
    server = get_server(name=uuid4().hex, client_type="vue2")
    scene = Scene([], default_spec([]))
    try:
        build_ui(server, scene)
        assert not hasattr(server.state, "legend_select_menu") or server.state.legend_select_menu is None
    finally:
        scene.close()


def test_analysis_icons_are_shrunk():
    """七个原图标约缩小四分之一，第八项共用尺寸。"""
    css = (
        Path(__file__).resolve().parents[2]
        / "modules/visPhysField/trameUI/client/workbench.css"
    ).read_text(encoding="utf-8")
    assert ".phys-analysis-main.v-btn{height:48px" in css
    assert ".phys-analysis-main .phys-icon{height:23px;width:23px}" in css
    icons = (
        Path(__file__).resolve().parents[2] / "modules/visPhysField/trameUI/icons.py"
    ).read_text(encoding="utf-8")
    assert "plot_over_line" in icons
