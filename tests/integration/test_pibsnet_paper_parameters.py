"""论文参数补丁门禁：严格定位、损失数值、完整预算及未决算法不变。"""

import ast
import importlib.util
import json
import os
import sys
from pathlib import Path

import pytest
import torch

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "paper_parameters", ROOT / "tools/verification/pibsnet/paper_parameters.py"
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
SOURCE = Path(
    os.environ.get(
        "PIBSNET_FROZEN_SOURCE",
        "/Users/zonghui/work/project_simulation/dojo_train/pibsnet/original_baseline/source",
    )
)


@pytest.mark.parametrize("variant", module.VARIANTS)
def test_only_approved_training_cell_changes(variant):
    case, epochs, updates = module.VARIANTS[variant]
    path = SOURCE / (case + ".ipynb")
    if not path.exists():
        pytest.skip("需要真实冻结来源；跳过不代表原来源验收通过")
    notebook = json.loads(path.read_text())
    target = 5 if case == "burgers" else 2
    for index, cell in enumerate(notebook["cells"]):
        if cell["cell_type"] != "code":
            continue
        before = "".join(cell["source"])
        after = module.amend_cell(before, case, index, variant)
        if index != target:
            assert after == before
            continue
        # Notebook 安装魔法不属于数值代码，执行器同样移除此行。
        old_tree, new_tree = (
            ast.parse(text.replace("!pip install shapely", "# isolated dependency"))
            for text in (before, after)
        )
        old_functions = {
            n.name: ast.dump(n)
            for n in old_tree.body
            if isinstance(n, (ast.FunctionDef, ast.ClassDef))
        }
        new_functions = {
            n.name: ast.dump(n)
            for n in new_tree.body
            if isinstance(n, (ast.FunctionDef, ast.ClassDef))
        }
        assert new_functions == old_functions
        if case == "burgers":
            assert "epochs = 5000" in after and updates == 500000
            names = {"pde_residual", "physics_loss", "data_loss", "loss"}
            assignments = [
                n
                for n in ast.walk(new_tree)
                if isinstance(n, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id in names for t in n.targets)
            ]
            values = {
                name: torch.tensor([1.0, 2.0], requires_grad=True)
                for name in ("B_surface_t", "B_surface", "B_surface_x", "B_surface_xx", "U_tensor")
            }
            values.update(mu=1.2, nu=0.01, torch=torch)
            values["U_tensor"] = torch.zeros(2)
            for node in assignments:
                exec(compile(ast.Module(body=[node], type_ignores=[]), "loss", "exec"), values)  # noqa: S102 - 锁定源码中筛选的损失赋值
            expected_residual = torch.tensor([2.19, 6.78])
            torch.testing.assert_close(values["pde_residual"], expected_residual)
            torch.testing.assert_close(values["loss"], expected_residual.square().mean() + 15 * 2.5)
            values["loss"].backward()
            assert torch.isfinite(values["B_surface"].grad).all()
        else:
            count = int(variant.rsplit("_", 1)[1])
            assert f"N_train = {count}" in after
            assert "n_cp_t = 100; n_cp_x = 20; n_cp_y = 20" in after
            assert "lambda_phys=0.001" in after
            assert "n_epochs = 3000" in after and updates == count * epochs


def test_source_drift_rejected():
    with pytest.raises(ValueError):
        module.replace_once("x x", "x", "y")
    with pytest.raises(ValueError):
        module.amend_cell("unknown source", "burgers", 5, "burgers")


def test_report_metric_protocols_and_invalid_prediction(monkeypatch):
    import numpy as np

    monkeypatch.setitem(sys.modules, "paper_parameters", module)
    report_spec = importlib.util.spec_from_file_location(
        "paper_trial_report", ROOT / "tools/verification/pibsnet/paper_trial_report.py"
    )
    reporter = importlib.util.module_from_spec(report_spec)
    report_spec.loader.exec_module(reporter)
    target = np.array([[[1.0]], [[10.0]]])
    pred = target + 1
    assert reporter.prediction_metrics(pred, target, time_average=True) == pytest.approx(0.55)
    assert reporter.prediction_metrics(pred, target) == pytest.approx(np.sqrt(2 / 101))
    with pytest.raises(ValueError):
        reporter.prediction_metrics(np.array([np.nan]), np.array([1.0]))
    with pytest.raises(ValueError):
        reporter.prediction_metrics(np.zeros(3), np.zeros(2))
