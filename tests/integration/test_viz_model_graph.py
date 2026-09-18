"""可视化模块两档官方结构图；失败不发布半份页。"""

from pathlib import Path

import pytest
import torch
from ai4e_viz.inspect.model_graph import PLATFORM_VIEWS, export_platform_views, fit_graph_viewport


def test_fit_graph_viewport_uses_width_not_entire_graph():
    html = (
        "const scale = Math.min(width / graphWidth, height / graphHeight) * 0.9;\n"
        "height / 2 - (minY + graphHeight / 2) * scale"
    )
    fitted = fit_graph_viewport(html)
    assert "height / graphHeight" not in fitted
    assert "24 - minY * scale" in fitted


def test_export_platform_views_writes_official_pair(tmp_path):
    model = torch.nn.Sequential(torch.nn.Linear(3, 4), torch.nn.Tanh(), torch.nn.Linear(4, 1))
    result = export_platform_views(
        model,
        torch.ones(2, 3),
        tmp_path,
        revision="r1",
        input_source={"sample": "viz-pair"},
    )
    assert result["status"] == "succeeded"
    assert result["default_view"] == "stage_trunk"
    assert result["graph_view"] == "stage_trunk"
    assert result["parameter_count"] == 21
    for spec in PLATFORM_VIEWS:
        path = tmp_path / spec["member"]
        assert path.is_file()
        html = path.read_text(encoding="utf-8")
        assert "html" in html.lower()
        assert result["views"][spec["id"]]["member"] == spec["member"]
        assert result["views"][spec["id"]]["graph_nodes"] == html.count('"node_type"')


def _display_names(html: str) -> str:
    start = html.find("const graph_node_display_names = ")
    if start < 0:
        return ""
    end = html.find("};", start)
    return html[start:end]


def test_export_platform_views_matches_selected_stage_boxes(tmp_path):
    from ai4e_contrib.ability.model.abupt.model import predict
    from tests.integration.test_abupt_multidomain import inputs, make_model

    result = export_platform_views(
        make_model(),
        inputs(),
        tmp_path,
        revision="r-ef",
        input_source={"sample": "stage-boxes"},
        predict=predict,
    )
    trunk = (tmp_path / "model.stage-trunk.html").read_text(encoding="utf-8")
    blocks = (tmp_path / "model.stage-blocks.html").read_text(encoding="utf-8")
    trunk_names = _display_names(trunk)
    blocks_names = _display_names(blocks)
    for required in (
        '"encoder"',
        '"geometry_blocks"',
        '"embed"',
        '"physics_blocks"',
        '"decoder_surface"',
        '"readout_surface"',
        '"decoder_volume"',
        '"readout_volume"',
    ):
        assert required in trunk_names
        assert required in blocks_names
    assert '"network"' not in trunk_names
    assert "isfinite" not in trunk_names
    assert "isfinite" not in blocks_names
    assert (
        result["views"]["stage_trunk"]["graph_nodes"]
        < result["views"]["stage_blocks"]["graph_nodes"]
    )


def test_export_platform_views_does_not_leave_half_pair(tmp_path, monkeypatch):
    from ai4e_viz.inspect import model_graph

    model = torch.nn.Linear(3, 1)
    calls = {"count": 0}
    original = model_graph._export_one

    def fail_after_first(target_model, inputs, target: Path, options):
        calls["count"] += 1
        if calls["count"] == 1:
            return original(target_model, inputs, target, options)
        raise RuntimeError("forced second-view failure")

    monkeypatch.setattr(model_graph, "_export_one", fail_after_first)
    with pytest.raises(RuntimeError, match="forced second-view failure"):
        export_platform_views(
            model,
            torch.ones(2, 3),
            tmp_path,
            revision="r-fail",
            input_source={"sample": "half"},
        )
    assert list(tmp_path.glob("*.html")) == []
    assert not (tmp_path / "model-inspection.json").exists()
