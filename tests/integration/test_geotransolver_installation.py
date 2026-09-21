"""真实隔离wheel、许可和脱离原仓库的完整网络入口。"""

import json
import os
import subprocess
from pathlib import Path

import pytest


def test_installed_wheel_forward_and_packaged_cases():
    root = os.environ.get("DOJO_GEOTRANSOLVER_INSTALLATION")
    if root is None:
        pytest.skip("独立wheel验收需 DOJO_GEOTRANSOLVER_INSTALLATION；不代表已通过")
    root = Path(root)
    paths = json.loads((root / "installed-paths.json").read_text())
    assert all(str(root / "venv") in value for value in paths.values())
    repo = Path(__file__).resolve().parents[2]
    scope = [
        repo / "packages/ai4e-core/Notice/physicsnemo/source.json",
        repo / "packages/ai4e-contrib/ability/model/geotransolver/source.json",
    ]
    for provenance in scope:
        for item in json.loads(provenance.read_text())["records"]:
            relative = Path(item["target"])
            package = relative.parts[1].replace("-", "_")
            installed = Path(paths[package]).parent.joinpath(*relative.parts[2:])
            assert installed.read_bytes() == (repo / relative).read_bytes()
    for relative in (
        "ai4e_core/abilities/transform/point_features.py",
        "ai4e_core/abilities/inference/indexed_prediction.py",
        "ai4e_core/abilities/data/stats/physical.py",
        "ai4e_core/applications/aero_cfd/trainprep/point_inputs.py",
        "ai4e_core/applications/aero_cfd/train/physical.py",
        "ai4e_core/applications/aero_cfd/infer/point_prediction.py",
        "ai4e_core/applications/aero_cfd/infer/stage.py",
        "ai4e_core/applications/aero_cfd/infer/configuration.py",
        "ai4e_core/applications/aero_cfd/post/mesh_export.py",
        "ai4e_contrib/application/aero_cfd/geotransolver/binding.py",
        "ai4e_contrib/application/aero_cfd/geotransolver/configuration.py",
    ):
        parts = Path(relative).parts
        installed = Path(paths[parts[0]]).parent.joinpath(*parts[1:])
        source = repo / "packages" / parts[0].replace("_", "-")
        assert installed.read_bytes() == source.joinpath(*parts[1:]).read_bytes()
    assert (Path(paths["ai4e_task"]).parent / "tasks/assets.py").read_bytes() == (
        repo / "packages/ai4e-task/tasks/assets.py"
    ).read_bytes()
    code = """import torch,sys
from pathlib import Path
import ai4e_task as task
from ai4e_contrib.ability.model.geotransolver import GeoTransolver
from ai4e_core.abilities.modeling.modules.geometry_attention import GALEBlock
torch.set_num_threads(2)
x=torch.randn(1,9,3)
m=GeoTransolver(3,1,geometry_dim=3,n_layers=4,n_hidden=128,n_head=4,slice_num=64,structured_shape=(3,3))
y=m(x,geometry=x);y.square().mean().backward();assert torch.isfinite(y).all()
assert not any(n.startswith('physicsnemo') for n in sys.modules)
assert task.describe_help_symbol('ai4e_core.abilities.constraint.relative_norm.relative_norm')
"""
    env = {k: v for k, v in os.environ.items() if k not in {"PYTHONPATH", "VIRTUAL_ENV"}}
    result = subprocess.run(
        [
            "uv",
            "run",
            "--no-project",
            "--python",
            str(root / "venv/bin/python"),
            "python",
            "-c",
            code,
        ],
        cwd=root,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_installed_aero_replay_evidence():
    root = os.environ.get("DOJO_GEOTRANSOLVER_INSTALLATION")
    if root is None:
        pytest.skip("安装公开入口验收需 DOJO_GEOTRANSOLVER_INSTALLATION")
    report = json.loads((Path(root) / "replay/replay.json").read_text())
    assert str(Path(root) / "venv") in report["interpreter"]
    assert all(str(Path(root) / "venv") in p for p in report["packages"].values())
    assert set(report["cases"]) == {"shapenet_car", "nasa_crm"}
    for result in report["cases"].values():
        assert result["epochs"] == 5 and result["updates"] == 10
        assert result["all_prediction_arrays_exact"]
        assert result["weights_optimizer_scheduler_exact"]
        assert result["rng_exact"] and result["sample_query_stream_exact"]
    extension = json.loads((Path(root) / "extension/extension.json").read_text())
    assert extension["saved_error_consumed"] and extension["hidden"] == 64
