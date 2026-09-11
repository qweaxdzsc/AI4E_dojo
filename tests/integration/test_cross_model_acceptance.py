"""真实五实验验收：只接受显式提供的本轮运行与完整数值产物。"""

import json
import os
from pathlib import Path

import numpy as np
import pytest
import torch
from PIL import Image


def test_formal_five_runs_and_reports():
    """真实硬件运行不能由合成夹具或历史结果自动替代。"""
    value = os.environ.get("DOJO_CROSS_MODEL_RESULTS")
    if not value:
        pytest.skip("需要显式 DOJO_CROSS_MODEL_RESULTS；跳过不算正式验收")
    root = Path(value)
    epochs = int(os.environ.get("DOJO_CROSS_MODEL_EPOCHS", "1"))
    device = os.environ.get("DOJO_CROSS_MODEL_DEVICE", "mps")
    assert epochs > 0
    training = json.loads((root / "training-runs.json").read_text())
    posts = json.loads((root / "post-runs.json").read_text())
    assert len(training) == len(posts) == 5
    from ai4e_core.abilities.eval.physical import PhysicalMetrics

    for name, run in training.items():
        assert run["status"] == "succeeded"
        path = Path(run["run"])
        report = json.loads((path / "artifacts/training.json").read_text())
        protocol = json.loads((path / "artifacts/training-protocol.json").read_text())
        expected = (84 if name.startswith("nasa") else 789) * epochs
        assert report["epochs"] == epochs and report["updates"] == expected
        assert len(protocol["inputs"]) == expected
        assert len(report["history"]) == epochs
        assert all(item["evaluation"] is None for item in report["history"])
        assert all(np.isfinite(item["loss"]) for item in report["history"])
        assert (
            protocol["execution"]["device"] == device
            and protocol["execution"]["precision"] == "fp32"
        )
        assert protocol["initialization"] != protocol["weights"]
        assert (path / "checkpoints/last.pt").exists()
        prediction = json.loads(Path(posts[name]["manifest"]).read_text())
        assert prediction["status"] == "succeeded" and len(prediction["results"]) == 5
        metric = PhysicalMetrics()
        for item in prediction["results"]:
            manifest_path = Path(item["manifest"])
            manifest = json.loads(manifest_path.read_text())
            arrays = {
                key: torch.load(manifest_path.parent / file, weights_only=True).numpy()
                for key, file in manifest["filemap"].items()
            }
            for domain, description in manifest["domains"].items():
                ids = arrays[description["ids"]]
                assert len(np.unique(ids)) == len(ids)
                if name.startswith("nasa"):
                    assert len(ids) == 454404
                for field, key in description["targets"].items():
                    metric.update(
                        domain + "." + field, arrays[key + ".prediction"], arrays[key + ".truth"]
                    )
        assert metric.finalize() == prediction["metrics"]
    for family, domains, images in [
        ("nasa", ["surface"], 24),
        ("shapenet", ["surface", "volume"], 9),
    ]:
        assert (root / "reports" / family / "index.html").is_file()
        rendering = json.loads((root / "reports" / family / "rendering.json").read_text())
        assert len(rendering) == images
        for item in rendering:
            with Image.open(item["path"]) as image:
                image.verify()
            with Image.open(item["path"]) as image:
                assert image.width >= 1000 and image.height >= 400
        for domain in domains:
            report = json.loads(
                (root / "comparison" / family / domain / "comparison.json").read_text()
            )
            assert report["status"] == "succeeded" and len(report["completed"]) == 5
            if family == "nasa":
                curves = [v for v in report["visuals"] if v["kind"] == "curve"]
                assert {v["span_fraction"] for v in curves} == {0.2, 0.5, 0.8}
                assert all(v["origin"][1] > 0 for v in curves)


def test_navigation_exists():
    root = Path(__file__).resolve().parents[2]
    assert (root / ".context/mvp/cross-model-acceptance.md").is_file()
    for name in ("ai4e-core", "ai4e-contrib", "ai4e-spec", "ai4e-viz", "recipes"):
        assert "cross-model-acceptance.md" in (root / ".context/modules" / f"{name}.md").read_text()


def test_package_dependency_boundaries():
    """检查本次正式包依赖方向，禁止把渲染或模型依赖放回 core。"""
    import ast

    root = Path(__file__).resolve().parents[2]
    for package, forbidden in [
        ("ai4e-spec", ("ai4e_core", "ai4e_contrib", "torch", "numpy")),
        ("ai4e-core", ("ai4e_contrib", "ai4e_viz", "noether", "user_project")),
        ("ai4e-viz", ("ai4e_core", "ai4e_contrib", "torch")),
    ]:
        for path in (root / "packages" / package).rglob("*.py"):
            tree = ast.parse(path.read_text())
            for node in ast.walk(tree):
                modules = (
                    [node.module]
                    if isinstance(node, ast.ImportFrom) and node.module
                    else [alias.name for alias in node.names]
                    if isinstance(node, ast.Import)
                    else []
                )
                assert not any(
                    module == prefix or module.startswith(prefix + ".")
                    for module in modules
                    for prefix in forbidden
                ), str(path)
