from pathlib import Path

from modules.reportManage import quarto as quarto_service
from modules.reportDesigner import replace_draft
from modules.reportManage import create_export, create_report, freeze_report


def _export_fixture(tmp_path: Path, monkeypatch, *, mode: str = "portable", orientation: str = "portrait") -> dict:
    monkeypatch.setenv("QODER_REPORT_DB", str(tmp_path / "report.sqlite3"))
    monkeypatch.setattr(quarto_service, "EXPORT_ROOT", tmp_path / "exports")
    draft = create_report({
        "title": "Quarto 配置合约",
        "author": "CI",
        "audience": "工程团队",
        "goal": "验证安全文本与 Typst 格式",
        "template": "analysis",
        "orientation": orientation,
    })
    document = draft["document"]
    document["sections"][0]["rows"][0]["blocks"][0]["body"] = (
        "**合法 Markdown**\n\n<script>alert('x')</script>\n\n```{python}\nraise SystemExit\n```"
    )
    replace_draft(draft["report_id"], draft["draft_revision"], document)
    version = freeze_report(draft["report_id"])
    return create_export(draft["report_id"], version["version"], "html", mode)


def test_generated_quarto_project_has_sibling_html_and_typst_formats(tmp_path, monkeypatch):
    export = _export_fixture(tmp_path, monkeypatch)
    project, manifest = quarto_service._write_project(export)
    config = (project / "_quarto.yml").read_text(encoding="utf-8")

    assert config.count("\n  html:\n") == 1
    assert config.count("\n  typst:\n") == 1
    assert "\n  typst:\n    typst:" not in config
    assert "embed-resources: false" in config
    assert "execute:\n  enabled: false" in config
    assert "lang: zh-CN" in config
    assert config.count("toc-title: 目录") == 2
    assert manifest["execute_enabled"] is False
    for relative in (
        "assets/echarts.min.js",
        "assets/plotly.min.js",
        "assets/vega.min.js",
        "assets/vega-lite.min.js",
        "assets/vega-embed.min.js",
        "assets/react.production.min.js",
        "assets/react-dom.production.min.js",
        "assets/react-flow.min.js",
        "assets/react-flow.css",
        "assets/perspective/cdn/perspective-viewer.js",
        "assets/perspective/cdn/perspective-viewer-datagrid.js",
        "assets/perspective/wasm/perspective-viewer.wasm",
    ):
        assert (project / relative).is_file(), relative


def test_report_markdown_cannot_emit_raw_html_or_executable_fences(tmp_path, monkeypatch):
    export = _export_fixture(tmp_path, monkeypatch)
    project, _ = quarto_service._write_project(export)
    qmd = (project / "index.qmd").read_text(encoding="utf-8")

    assert "**合法 Markdown**" in qmd
    assert "<script>" not in qmd
    assert "&lt;script&gt;" in qmd
    assert "```{python}" not in qmd
    assert "｀｀｀{python}" in qmd


def test_landscape_typst_uses_controlled_page_flip(tmp_path, monkeypatch):
    export = _export_fixture(tmp_path, monkeypatch, orientation="landscape")
    project, _ = quarto_service._write_project(export)
    config = (project / "_quarto.yml").read_text(encoding="utf-8")
    assert "#set page(flipped: true)" in config


def test_connected_html_preserves_external_visualization_iframes(tmp_path, monkeypatch):
    export = _export_fixture(tmp_path, monkeypatch, mode="connected")
    project, _ = quarto_service._write_project(export)
    config = (project / "_quarto.yml").read_text(encoding="utf-8")

    assert "embed-resources: false" in config


def test_mesh_connected_export_does_not_duplicate_glb_and_portable_keeps_o3dv(tmp_path, monkeypatch):
    source = tmp_path / "fusion.glb"
    source.write_bytes(b"glTF" + b"\x00" * 32)
    monkeypatch.setattr(quarto_service, "get_artifact", lambda _artifact_id: {"file_path": str(source)})
    monkeypatch.setattr(
        quarto_service,
        "_capture_visualization_static",
        lambda _visualization, _project_dir: ("assets/static/viz-mesh-v1.png", None),
    )
    visualization = {
        "visualization_id": "viz-mesh",
        "artifact_id": "A-GEO",
        "spec_id": "vspec-geo",
        "spec_version": 1,
        "parameters": {"show_edges": True, "camera_projection": "orthographic"},
        "payload": {
            "artifact": {"kind": "mesh", "name": "聚变站几何", "takeaway": "由 O3DV 冻结同参数证据。"},
            "renderer": {"owner": "o3dv"},
        },
    }

    html_block, pdf_block = quarto_service._visualization_html(visualization, tmp_path / "project", portable=False)

    assert "#/visualizations/viz-mesh?embed=1" in html_block
    assert "assets/static/viz-mesh-v1.png" in pdf_block
    assert not (tmp_path / "project" / "assets" / "models" / "A-GEO.glb").exists()

    portable_html, _ = quarto_service._visualization_html(visualization, tmp_path / "portable", portable=True)
    assert "assets/o3dv/embed.html" in portable_html
    assert "../models/A-GEO.glb" in portable_html
    assert (tmp_path / "portable" / "assets" / "models" / "A-GEO.glb").is_file()


def test_capture_error_summary_keeps_actionable_playwright_context():
    stderr = """page.goto: Timeout 60000ms exceeded.\nCall log:\n  - navigating to URL\nNode.js v24.16.0\n"""

    summary = quarto_service._capture_error_summary(stderr, "")

    assert "page.goto: Timeout 60000ms exceeded" in summary
    assert "Node.js v24.16.0" not in summary


def test_export_compaction_keeps_only_required_download_artifacts(tmp_path, monkeypatch):
    monkeypatch.setattr(quarto_service, "EXPORT_ROOT", tmp_path / "exports")

    portable_root = quarto_service.EXPORT_ROOT / "export-portable"
    (portable_root / "project" / "output" / "assets").mkdir(parents=True)
    (portable_root / "project" / "output" / "assets" / "model.glb").write_bytes(b"model")
    archive = portable_root / "report.zip"
    archive.write_bytes(b"zip")
    (portable_root / "quarto.log").write_text("ok", encoding="utf-8")
    result = quarto_service.compact_export_directory("export-portable", output_path=str(archive))
    assert result["reclaimed_bytes"] > 0
    assert archive.is_file()
    assert (portable_root / "quarto.log").is_file()
    assert not (portable_root / "project").exists()

    pdf_root = quarto_service.EXPORT_ROOT / "export-pdf"
    (pdf_root / "project" / "assets").mkdir(parents=True)
    (pdf_root / "project" / "assets" / "model.glb").write_bytes(b"source-copy")
    (pdf_root / "project" / "output" / "assets").mkdir(parents=True)
    (pdf_root / "project" / "output" / "assets" / "model.glb").write_bytes(b"output-copy")
    pdf = pdf_root / "project" / "output" / "index.pdf"
    pdf.write_bytes(b"pdf")
    quarto_service.compact_export_directory("export-pdf", output_path=str(pdf))
    assert pdf.is_file()
    assert not (pdf_root / "project" / "assets").exists()
    assert not (pdf_root / "project" / "output" / "assets").exists()

    connected_root = quarto_service.EXPORT_ROOT / "export-connected"
    (connected_root / "project" / "assets").mkdir(parents=True)
    (connected_root / "project" / "assets" / "source-copy.glb").write_bytes(b"source")
    (connected_root / "project" / "output" / "assets").mkdir(parents=True)
    runtime = connected_root / "project" / "output" / "assets" / "runtime.js"
    runtime.write_text("live", encoding="utf-8")
    html = connected_root / "project" / "output" / "index.html"
    html.write_text("<html></html>", encoding="utf-8")
    quarto_service.compact_export_directory("export-connected", output_path=str(html))
    assert html.is_file()
    assert runtime.is_file()
    assert not (connected_root / "project" / "assets").exists()
