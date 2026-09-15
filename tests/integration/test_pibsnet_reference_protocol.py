"""外部参考运行保留原目标，完整配点协议不得静默降级。"""

import importlib.util
from pathlib import Path

import pytest

from ai4e_contrib.application.datasets.parametric import component

ROOT = Path(__file__).resolve().parents[2]


def test_advection_original_loop_short_execution(tmp_path):
    """短执行核对原分支交接，不将一轮结果用于正式精度验收。"""
    source = ROOT.parent / "PI-BSNet/src/advection.ipynb"
    if not source.exists():
        pytest.skip("锁定外部参考仓库不可用")
    spec = importlib.util.spec_from_file_location(
        "reference_advection", ROOT / "tools/verification/pibsnet/reference_advection.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    component("advection").generate(
        {"output": str(tmp_path / "data"), "train": 2, "test": 2, "nx": 10, "nt": 10}
    )
    result = module.run(source, tmp_path / "data/manifest.json", tmp_path / "reference", epochs=1)
    assert result["updates"] == 2
    assert len(result["samples"]) == 2
    assert result["pde_points"] == "complete_dataset_grid"
    assert result["loss_weights"] == {"pde": 1, "data": 10, "initial": 0, "periodic": 0}


@pytest.mark.parametrize("case", ["burgers", "diffusion_trapezoid"])
def test_notebook_reference_short_execution(tmp_path, case):
    """验证真实原函数训练及完整输出，固定正式模型大小但缩短数据和轮次。"""
    source = ROOT.parent / f"PI-BSNet/src/{case}.ipynb"
    if not source.exists():
        pytest.skip("锁定外部参考仓库不可用")
    spec = importlib.util.spec_from_file_location(
        "reference_notebooks", ROOT / "tools/verification/pibsnet/reference_notebooks.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    component(case).generate(
        {
            "output": str(tmp_path / "data"),
            "train": 1,
            "test": 1,
            "nx": 10,
            "nt": 10,
            **({"ny": 10, "nt": 201} if case == "diffusion_trapezoid" else {}),
        }
    )
    result = module.run(
        case, source, tmp_path / "data/manifest.json", tmp_path / "reference", epochs=1
    )
    assert result["updates"] == 1
    assert len(result["samples"]) == 1
    assert result["pde_points"] == "complete_dataset_grid"


def test_comparison_rejects_subset_and_extra_weights():
    from tests.integration.test_pibsnet_training import configuration

    spec = importlib.util.spec_from_file_location(
        "pibsnet_compare", ROOT / "tools/verification/pibsnet/compare.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    cfg = configuration.defaults("advection")
    reference = {
        "pde_points": "complete_dataset_grid",
        "loss_weights": {"pde": 1, "data": 10, "initial": 0, "periodic": 0},
    }
    module.validate_objective(cfg, reference)
    cfg["model"]["sampling"]["interior"]["include_boundary"] = False
    with pytest.raises(ValueError, match="配点协议不同"):
        module.validate_objective(cfg, reference)
    cfg["model"]["sampling"]["interior"]["include_boundary"] = True
    cfg["model"]["constraints"]["periodic_boundary_conditions"]["weight"] = 1
    with pytest.raises(ValueError, match="损失权重不同"):
        module.validate_objective(cfg, reference)


def test_report_missing_predictions_stays_partial(tmp_path, monkeypatch):
    """完整度是业务门槛，不能把缺失预测的空报告标成验收完成。"""
    monkeypatch.syspath_prepend(str(ROOT / "tools/verification/pibsnet"))
    spec = importlib.util.spec_from_file_location(
        "pibsnet_report", ROOT / "tools/verification/pibsnet/report.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result = module.build(tmp_path / "missing", tmp_path / "report")
    assert result["status"] == "partial"
    assert result["precision_acceptance"] == "not_established"
    assert len(result["cases"]) == 5
    assert all(row["status"] == "pending" for row in result["cases"])


def test_generalization_rejects_nonfinite_evaluations(tmp_path):
    """41次评价存在并不代表可以用无穷大拟合经验关系。"""
    import torch

    spec = importlib.util.spec_from_file_location(
        "pibsnet_generalization", ROOT / "tools/verification/pibsnet/generalization.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    state = {
        "epoch": 2000,
        "history": [
            {
                "epoch": epoch,
                "loss": 1 / (index + 1),
                "evaluation": {"samples": 30, "max_absolute_error": float("inf")},
            }
            for index, epoch in enumerate([*range(1, 2000, 50), 2000])
        ],
    }
    checkpoint = tmp_path / "checkpoint.pt"
    torch.save(state, checkpoint)
    with pytest.raises(ValueError, match="不足两个点"):
        module.summarize(checkpoint, tmp_path / "result.json")
    assert not (tmp_path / "result.json").exists()
