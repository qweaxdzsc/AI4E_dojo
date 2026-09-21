"""F：新增目录与100项验收映射有真实导航，案例显式复用业务步骤。"""

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def test_all_items_have_real_implementation_paths():
    """一百项叶子都有路径与明确状态，未完成项保留 pending。"""
    rows = json.loads((ROOT / ".context/mvp/transolver3-results/coverage.json").read_text())
    assert len(rows) == 100 and {r["id"] for r in rows} == set(range(1, 101))
    for row in rows:
        assert row["leaf"] and row["status"]
        assert (ROOT / row["dojo"]).is_file()
        for evidence in row["evidence"]:
            assert (ROOT / evidence).is_file()
    assert (ROOT / ".context/mvp/transolver3-acceptance.md").is_file()


def test_examples_share_configuration_and_explicit_domain_steps():
    """配置与阶段交接共享；来源与模型步骤允许可见的局部差异。"""
    for example in ("shapenet_car_abupt", "nasa_crm_transolver3"):
        for script in ("configuration.py", "pipeline.py"):
            assert (ROOT / "recipes/aero_cfd" / script).read_bytes() == (
                ROOT / "examples/aero_cfd" / example / script
            ).read_bytes()
        for script in ("rawprep.py", "trainprep.py", "train.py", "infer.py"):
            source = (ROOT / "examples/aero_cfd" / example / script).read_text()
            assert ".workflow" not in source
            assert "load_components" in source
        post = (ROOT / "examples/aero_cfd" / example / "post.py").read_text()
        assert "open_results" in post and "legacy_predict" not in post
        assert (
            "configure_objectives"
            in (ROOT / "examples/aero_cfd" / example / "train.py").read_text()
        )


def test_nasa_meshgraphnet_uses_physical_hdf_rawprep():
    """NASA 图案例沿 HDF5 物理适配器读取，不误用 VTK 目录数据集入口。"""
    source = (ROOT / "examples/aero_cfd/nasa_crm_meshgraphnet/rawprep.py").read_text()
    assert "rawprep import physical" in source
    assert "physical.execute" in source


def test_topological_aero_examples_enable_vtkhdf():
    """来源具有网格拓扑的外流案例显式交付 VTKHDF。"""
    root = ROOT / "examples/aero_cfd"
    for name in (
        "shapenet_car_abupt",
        "shapenet_car_transolver3_surface",
        "shapenet_car_transolver3_volume",
    ):
        cfg = yaml.safe_load((root / name / "config.yaml").read_text())
        assert cfg["rawprep"]["vtkhdf"] is True
    for name in ("nasa_crm_abupt", "nasa_crm_transolver3"):
        cfg = yaml.safe_load((root / name / "config.yaml").read_text())
        assert cfg["rawprep"]["vtkhdf"] is True
    template = yaml.safe_load((ROOT / "recipes/aero_cfd/config.yaml").read_text())
    assert template["rawprep"]["vtkhdf"] is True


def test_module_navigation_and_no_reference_runtime_dependency():
    """模块索引登记职责；正式包没有参考仓库的运行导入。"""
    for module in ("ai4e-core", "ai4e-contrib", "ai4e-spec", "recipes"):
        assert (
            "transolver3-acceptance.md" in (ROOT / ".context/modules" / f"{module}.md").read_text()
        )
    for path in (ROOT / "packages").rglob("*.py"):
        text = path.read_text()
        assert "from user_project" not in text and "import user_project" not in text
